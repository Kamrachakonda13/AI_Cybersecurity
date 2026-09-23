import threading
from collections import defaultdict

# Groq pricing per 1M tokens for openai/gpt-oss-20b (approximate, USD).
# Update if Groq changes pricing.
PRICE_PER_M_INPUT = 0.10
PRICE_PER_M_OUTPUT = 0.50

_lock = threading.Lock()

_metrics = {
    "total_calls": 0,
    "total_prompt_tokens": 0,
    "total_completion_tokens": 0,
    "total_cost_usd": 0.0,
    "by_tool": defaultdict(lambda: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0}),
    "by_model": defaultdict(lambda: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0}),
}


def record_llm_call(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    tool: str | None = None,
):
    """
    Record a single LLM call. Thread-safe. Called after every Groq response.
    """
    cost = (
        (prompt_tokens / 1_000_000) * PRICE_PER_M_INPUT
        + (completion_tokens / 1_000_000) * PRICE_PER_M_OUTPUT
    )

    with _lock:
        _metrics["total_calls"] += 1
        _metrics["total_prompt_tokens"] += prompt_tokens
        _metrics["total_completion_tokens"] += completion_tokens
        _metrics["total_cost_usd"] += cost
        _metrics["by_model"][model]["calls"] += 1
        _metrics["by_model"][model]["prompt_tokens"] += prompt_tokens
        _metrics["by_model"][model]["completion_tokens"] += completion_tokens

        if tool:
            _metrics["by_tool"][tool]["calls"] += 1
            _metrics["by_tool"][tool]["prompt_tokens"] += prompt_tokens
            _metrics["by_tool"][tool]["completion_tokens"] += completion_tokens


def snapshot() -> dict:
    """Return a JSON-serializable snapshot of current metrics."""
    with _lock:
        return {
            "total_calls": _metrics["total_calls"],
            "total_prompt_tokens": _metrics["total_prompt_tokens"],
            "total_completion_tokens": _metrics["total_completion_tokens"],
            "total_cost_usd": round(_metrics["total_cost_usd"], 6),
            "by_tool": {k: dict(v) for k, v in _metrics["by_tool"].items()},
            "by_model": {k: dict(v) for k, v in _metrics["by_model"].items()},
        }


def reset():
    """Reset all metrics. Used in tests."""
    with _lock:
        _metrics["total_calls"] = 0
        _metrics["total_prompt_tokens"] = 0
        _metrics["total_completion_tokens"] = 0
        _metrics["total_cost_usd"] = 0.0
        _metrics["by_tool"] = defaultdict(lambda: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0})
        _metrics["by_model"] = defaultdict(lambda: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0})


if __name__ == "__main__":
    import json

    record_llm_call("openai/gpt-oss-20b", 500, 120, tool="retrieve")
    record_llm_call("openai/gpt-oss-20b", 300, 80, tool="graph_query")
    record_llm_call("openai/gpt-oss-20b", 200, 50)

    print(json.dumps(snapshot(), indent=2))