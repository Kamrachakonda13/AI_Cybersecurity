import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv  # noqa: E402
from groq import Groq  # noqa: E402

from src.hallucination import check_hallucination  # noqa: E402
from src.pii import check_pii, mask_pii  # noqa: E402
from src.confidence import (  # noqa: E402
    check_query_coverage,
    evaluate_confidence,
    evaluate_graph_confidence,
)
from src.metrics import record_llm_call  # noqa: E402
from src.tools.audit_tool import query_audit_log  # noqa: E402
from src.tools.calc_tool import calculate  # noqa: E402
from src.tools.date_tool import parse_date  # noqa: E402
from src.tools.graph_tool import graph_query  # noqa: E402
from src.tools.retrieve_tool import retrieve  # noqa: E402
from src.tools.sql_tool import query_sql  # noqa: E402
from src.tools.web_search_tool import web_search  # noqa: E402
from src.traces import append_step, new_trace_id  # noqa: E402

load_dotenv()

MODEL_NAME = "openai/gpt-oss-20b"
MAX_STEPS = 5

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key.startswith("placeholder"):
            raise RuntimeError("GROQ_API_KEY is not set in .env")
        _client = Groq(api_key=api_key)
    return _client


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "retrieve",
            "description": (
                "Retrieve relevant chunks from the corpus using hybrid search. "
                "Use for questions answerable from a single document or paragraph."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "graph_query",
            "description": (
                "Traverse the knowledge graph for relationship questions. "
                "Use when the query asks what depends on what, what connects to what, "
                "or transitive relationships between services, policies, or databases."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The relationship query."}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate an arithmetic expression. Use for any numeric computation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Arithmetic expression, e.g. '15 * 24 + 7'.",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "parse_date",
            "description": "Extract and normalize a date from text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text that contains a date."}
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_audit_log",
            "description": "Query the audit log for recent requests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max rows to return."},
                    "route": {
                        "type": "string",
                        "description": "Optional filter: agent, graph, or hybrid.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information. Use for questions about recent events, latest developments, current news, general knowledge not in the enterprise corpus, or topics like external APIs, public documentation, or industry trends.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."},
                    "max_results": {"type": "integer", "description": "Max results (1-10). Default 5."}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_sql",
            "description": "Run a read-only SQL SELECT query against the company database. Use for questions about transactions, users, products, or support tickets that require counting, aggregating, filtering, or joining structured data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "A SELECT statement."},
                    "limit": {"type": "integer", "description": "Max rows. Default 50."}
                },
                "required": ["sql"],
            },
        },
    },
]


def _execute_tool(tool_name: str, args: dict, user_clearance: str, tenant_id: str) -> dict:
    try:
        if tool_name == "retrieve":
            return retrieve(query=args.get("query", ""), user_clearance=user_clearance, tenant_id=tenant_id)
        if tool_name == "graph_query":
            return graph_query(query=args.get("query", ""), user_clearance=user_clearance)
        if tool_name == "calculate":
            return calculate(expression=args.get("expression", ""))
        if tool_name == "parse_date":
            return parse_date(text=args.get("text", ""))
        if tool_name == "query_audit_log":
            return query_audit_log(limit=int(args.get("limit", 10)), route=args.get("route"))
        if tool_name == "web_search":
            return web_search(query=args.get("query", ""), max_results=int(args.get("max_results", 5)))
        if tool_name == "query_sql":
            return query_sql(sql=args.get("sql", ""), limit=int(args.get("limit", 50)))
        return {
            "tool": tool_name,
            "ok": False,
            "result": None,
            "summary": f"Unknown tool: {tool_name}",
            "error": "unknown_tool",
        }
    except Exception as e:
        return {
            "tool": tool_name,
            "ok": False,
            "result": None,
            "summary": f"Tool {tool_name} raised: {e}",
            "error": str(e),
        }


SYSTEM_PROMPT = (
    "You are an enterprise retrieval agent. Answer the user's question by calling "
    "the available tools when you need evidence. Use retrieve for semantic questions, "
    "graph_query for relationship questions, calculate for arithmetic, parse_date for "
    "date extraction, and query_audit_log for audit history. When you have enough "
    "evidence, respond with a final grounded answer that cites the chunk IDs you used. "
    "If no evidence supports an answer, respond exactly: "
    "'I don't know based on the provided context.' "
    "\n\nRouting rules:\n"
    "- If the question is about \"latest\", \"recent\", \"current\", \"news\", "
    "  or \"developments\" in a topic, use web_search.\n"
    "- If the question involves counting, aggregating, filtering, or joining "
    "  structured data (transactions, users, products, tickets), use query_sql.\n"
    "- If the question is about internal policies, runbooks, or enterprise documents, "
    "  use retrieve.\n"
    "- If the question is about relationships between services or dependencies, "
    "  use graph_query."
)

REFUSAL_PATTERNS = [
    "i can't help",
    "i cannot help",
    "i can't assist",
    "i cannot assist",
    "i'm sorry",
    "i am sorry",
    "i won't",
    "i will not",
    "i'm not able to",
    "i am not able to",
    "i don't know based on the provided context",
    "i cannot provide",
    "i can't provide",
    "i cannot give",
    "i can't give",
    "i'm unable to",
    "i am unable to",
    "i must decline",
    "i have to decline",
]


def _looks_like_refusal(text: str) -> bool:
    lowered = (text or "").lower()
    # Normalize typographic apostrophes to straight ones for matching
    lowered = lowered.replace("\u2019", "'").replace("\u2018", "'")
    return any(p in lowered for p in REFUSAL_PATTERNS)

def _summarize_tool_result(result: dict) -> str:
    return result.get("summary", "") or f"{result.get('tool', 'tool')} returned."


def _score_tool_confidence(tool_name: str, result: dict, query: str):
    if not result.get("ok"):
        return None

    if tool_name == "retrieve":
        chunks = (result.get("result") or {}).get("chunks", [])
        score_conf = evaluate_confidence(chunks)
        if not score_conf["confident"]:
            return score_conf

        coverage = check_query_coverage(query, chunks)
        if not coverage["covered"]:
            return {
                "confident": False,
                "top_score": score_conf.get("top_score"),
                "num_chunks": score_conf.get("num_chunks"),
                "reason": coverage["reason"],
            }

        return {**score_conf, "coverage": coverage}

    if tool_name == "graph_query":
        edges = (result.get("result") or {}).get("edges", [])
        return evaluate_graph_confidence(edges)

    return None


def run_agent(query: str, user_clearance: str, tenant_id: str) -> dict:
    """
    Execute the reasoning loop using Groq's native tool-calling API.
    Confidence gate refuses on the first weak tool result.
    Refusal is terminal: the loop stops immediately.
    """
    trace_id = new_trace_id()
    start_ts = time.time()

    append_step(trace_id, 0, {"kind": "request", "query": query, "route": "agent"})

    steps = [{"kind": "user", "text": query}]

    # PII check on input
    pii_check = check_pii(query)
    if pii_check.get("has_pii"):
        pii_step = {
            "kind": "pii_detected_input",
            "count": pii_check["count"],
            "types": [e["type"] for e in pii_check["entities"]],
        }
        append_step(trace_id, 0, pii_step)
        steps.append(pii_step)
        # Mask the query before it goes to the LLM
        masked_result = mask_pii(query)
        query = masked_result["masked"]
        # Update the user step to show the masked query
        steps[0] = {"kind": "user", "text": query}

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]

    tool_call_count = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    final_answer = None
    refused = False
    last_confidence = None

    for step_index in range(1, MAX_STEPS + 1):
        t0 = time.time()
        response = get_client().chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            temperature=0.0,
        )
        latency_ms = int((time.time() - t0) * 1000)

        usage = getattr(response, "usage", None)
        if usage is not None:
            pt = getattr(usage, "prompt_tokens", 0) or 0
            ct = getattr(usage, "completion_tokens", 0) or 0
            total_prompt_tokens += pt
            total_completion_tokens += ct
            record_llm_call(MODEL_NAME, pt, ct, tool="agent")

        msg = response.choices[0].message
        tool_calls = getattr(msg, "tool_calls", None) or []
        content = getattr(msg, "content", None) or ""

        append_step(trace_id, step_index, {
            "kind": "llm_thought",
            "step_index": step_index,
            "content_preview": content[:400],
            "num_tool_calls": len(tool_calls),
            "latency_ms": latency_ms,
        })

        # No tool calls: model wants to answer directly.
        if not tool_calls:
            if last_confidence is not None and not last_confidence.get("confident", False):
                final_answer = "I don't know based on the provided context."
                append_step(trace_id, step_index, {
                    "kind": "refusal",
                    "text": final_answer,
                    "reason": "Latest tool result was below confidence threshold.",
                })
                steps.append({
                    "kind": "refusal",
                    "text": final_answer,
                    "reason": "Latest tool result was below confidence threshold.",
                })
                refused = True
                break

            if tool_call_count == 0 and step_index < MAX_STEPS:
                append_step(trace_id, step_index, {
                    "kind": "policy_enforcement",
                    "reason": "Model attempted to answer without calling any tool.",
                })
                messages.append({
                    "role": "system",
                    "content": (
                        "You must call at least one tool before answering. "
                        "Call the retrieve tool with a query derived from the user's question."
                    ),
                })
                continue

            final_answer = content.strip() or "I don't know based on the provided context."

            # Detect model-driven refusals (safety filters) as refusals.
            if _looks_like_refusal(final_answer):
                refused = True

            append_step(trace_id, step_index, {
                "kind": "answer",
                "text": final_answer,
                "refused": refused,
            })
            steps.append({"kind": "answer", "text": final_answer})
            break

        # Tool calls present: append assistant message with the calls.
        messages.append({
            "role": "assistant",
            "content": content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ],
        })

        refused_in_tool_loop = False

        for tc in tool_calls:
            tool_call_count += 1
            tool_name = tc.function.name

            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            steps.append({"kind": "tool_call", "tool": tool_name, "args": args})
            append_step(trace_id, step_index, {
                "kind": "tool_call",
                "tool": tool_name,
                "args": args,
            })

            result = _execute_tool(tool_name, args, user_clearance, tenant_id)
            summary = _summarize_tool_result(result)

            steps.append({
                "kind": "tool_result",
                "tool": tool_name,
                "ok": result.get("ok", False),
                "summary": summary,
            })
            append_step(trace_id, step_index, {
                "kind": "tool_result",
                "tool": tool_name,
                "ok": result.get("ok", False),
                "summary": summary,
                "result_preview": json.dumps(result.get("result"), default=str)[:600],
            })

            confidence = _score_tool_confidence(tool_name, result, query)
            if confidence is not None:
                last_confidence = confidence
                steps.append({"kind": "confidence", **confidence})
                append_step(trace_id, step_index, {"kind": "confidence", **confidence})

                if not confidence["confident"]:
                    final_answer = "I don't know based on the provided context."
                    append_step(trace_id, step_index, {
                        "kind": "refusal",
                        "text": final_answer,
                        "reason": confidence["reason"],
                    })
                    steps.append({
                        "kind": "refusal",
                        "text": final_answer,
                        "reason": confidence["reason"],
                    })
                    refused = True
                    refused_in_tool_loop = True
                    break

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps({
                    "ok": result.get("ok", False),
                    "summary": summary,
                    "confidence": confidence if confidence is not None else "n/a",
                    "result": result.get("result"),
                }, default=str)[:4000],
            })

        if refused_in_tool_loop:
            break

    if final_answer is None:
        final_answer = "I don't know based on the provided context."

    latency_ms_total = int((time.time() - start_ts) * 1000)
    append_step(trace_id, MAX_STEPS + 1, {
        "kind": "summary",
        "tool_calls": tool_call_count,
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
        "latency_ms": latency_ms_total,
        "refused": refused,
    })

    # Output-side checks: PII masking and hallucination verification
    output_pii = mask_pii(final_answer)
    if output_pii["count"] > 0:
        final_answer = output_pii["masked"]
        append_step(trace_id, MAX_STEPS + 2, {
            "kind": "pii_masked_output",
            "count": output_pii["count"],
            "types": [e["type"] for e in output_pii["entities"]],
        })

    # Hallucination check: only when we have retrieved context
    retrieved_context = "\n\n".join(
        s.get("text", "") for s in steps
        if s.get("kind") == "tool_result" and "retrieve" in s.get("tool", "")
    )
    # Get content from retrieved chunks
    retrieved_content = ""
    for s in steps:
        if s.get("kind") == "tool_result" and s.get("tool") in ("retrieve", "graph_query"):
            pass
    # Build context from the tool_result previews
    context_parts = []
    for s in steps:
        if s.get("kind") == "tool_result" and s.get("tool") in ("retrieve", "graph_query"):
            context_parts.append(s.get("summary", ""))
    # Fallback: use the summary strings, not ideal but better than nothing
    # A proper implementation would pass the actual chunks
    hallucination_result = None

    if not refused and final_answer and "I don't know" not in final_answer:
        # Only run on answers derived from retrieval
        retrieval_used = any(
            s.get("kind") == "tool_call" and s.get("tool") in ("retrieve", "graph_query")
            for s in steps
        )
        if retrieval_used:
            # For now, use a simplified context
            # (A full implementation would thread the actual chunk content through)
            hallucination_result = None
            append_step(trace_id, MAX_STEPS + 3, {
                "kind": "hallucination_check",
                "status": "skipped",
                "reason": "context_not_threaded",
            })

    return {
        "trace_id": trace_id,
        "answer": final_answer,
        "steps": steps,
        "tool_calls": tool_call_count,
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
        "latency_ms": latency_ms_total,
        "refused": refused,
    }


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "What does billing-service depend on?"
    result = run_agent(q, user_clearance="CONFIDENTIAL", tenant_id="acme")
    print("Trace ID:", result["trace_id"])
    print("Tool calls:", result["tool_calls"])
    print("Refused:", result["refused"])
    print("Prompt tokens:", result["prompt_tokens"])
    print("Completion tokens:", result["completion_tokens"])
    print("Latency ms:", result["latency_ms"])
    print()
    print("Answer:", result["answer"])
    print()
    print("Steps:")
    for s in result["steps"]:
        print(" -", json.dumps(s, default=str)[:150])