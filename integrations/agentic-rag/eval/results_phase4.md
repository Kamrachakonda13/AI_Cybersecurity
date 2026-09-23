# Phase 4 Results — Agentic RAG with Observability

**Date:** 2026-09-16
**Deliverable:** ReAct-style reasoning loop with tool calling, token
metering, per-tool timeouts, and a containerized observability stack.
**Model:** openai/gpt-oss-20b via Groq
**Max reasoning steps:** 5
**Tool timeout:** 10 seconds per call

## Why an agent layer

Phases 1–3 gave the system retrieval. Phase 4 gives it *agency*:
the ability to decide what to retrieve, when to compute, when to
look something up, and when to stop.

The design principle from the roadmap: "RAG is a component in a
larger decision system, and you must be able to control cost,
latency, and autonomy." Every Phase 4 decision is measured against
that line.

## Tool set

Five tools exposed to the reasoning loop:

| Tool | Purpose | Returns |
|------|---------|---------|
| `retrieve(query)` | Wraps Phase 2 Hybrid RAG | Top-5 chunks with scores |
| `calculate(expression)` | Safe arithmetic evaluation | Numeric result |
| `parse_date(text)` | Natural-language date parsing | ISO 8601 date |
| `query_sql(sql)` | Read-only SQL against demo DB | Rows as JSON |
| `web_search(query)` | External lookup (bounded) | Snippets + URLs |

The router selects the tool based on the reason step's output.
Correctness measured against a hand-labeled question set.

## Tool routing accuracy

**5/5 on the labeled tool-selection set.**

| Query | Expected tool | Selected |
|-------|---------------|----------|
| "How many failed logins trigger lockout?" | retrieve | retrieve |
| "What is 15% of 2,340?" | calculate | calculate |
| "When did the KEV entry last update?" | parse_date | parse_date |
| "How many users have CONFIDENTIAL clearance?" | query_sql | query_sql |
| "What CVE corresponds to Log4Shell?" | web_search | web_search |

## Reasoning loop

The loop is ReAct-style: reason → select tool → execute → observe →
repeat. Bounded at 5 steps. On step-limit exhaustion, the agent
returns a best-effort answer with a `truncated: true` flag so the
caller knows the reasoning was cut short.

Two hard rules, established later in Phase 5 but worth naming here:

1. Every answer requires at least one tool call. A direct answer
   from the model weights bypasses grounding and audit.
2. A tool failure is observable to the loop. Timeouts return a
   structured error that the reason step can decide how to handle.

## Token metering

Every LLM call records:

- `prompt_tokens`
- `completion_tokens`
- `cost_estimate` (using Groq's published rates)
- `latency_ms`

Exposed at `/metrics` as cumulative totals across the session.
The Metrics dashboard page (added in Phase 7) consumes this data.

Sample run totals (from the development period):

- Total requests: 104
- Total tokens: 266,287 (234,270 prompt + 32,017 completion)
- Average latency: 11,955 ms
- Estimated cost: $0.0394

## Async execution and timeouts

Every tool call is wrapped in `asyncio.wait_for(..., timeout=10)`.
On timeout, the loop receives a structured error and can decide to
retry with a different tool or return a partial answer.

This is the difference between "the agent works in demos" and
"the agent is deployable" — a hung tool cannot hang the request.

## Dockerization

The stack ships as four containers:

docker compose up -d --build

| Service | Image | Purpose |
|---------|-------|---------|
| api | vector-rag-api | FastAPI + agent + dashboard |
| postgres | pgvector/pgvector:pg16 | Vector store |
| neo4j | neo4j:5.24-community | Graph store |
| minio | quay.io/minio/minio | S3-compatible object store |

The `api` container is built from the project Dockerfile. The other
three are stock images with persistent volumes.

## Known limitations

1. **`web_search` is bounded by free-tier API limits.** Not suitable
   for high-volume production without a paid provider.

2. **`query_sql` is read-only by design.** Write access would need
   a review queue and audit-before-apply flow.

3. **No cost ceiling in the loop itself.** Token metering is passive.
   A production agent should refuse to run past a budget threshold.

4. **Single-provider dependency.** All reasoning runs through Groq.
   A fallback provider would improve resilience.

5. **No trace-level replay.** Traces are logged, not re-executable.
   A future phase would allow "replay this trace against a modified
   prompt" for regression testing.

## What Phase 4 demonstrates for the portfolio

- **Agents are not a framework, they are a control problem.** The
  value is in the bounds — step limit, timeout, metering — not in
  the loop itself.
- **Observability is designed in, not bolted on.** Traces and metrics
  came with the agent, not after.
- **Containerization is a decision**, not a checkbox. Four services,
  one compose file, restartable individually.
'''