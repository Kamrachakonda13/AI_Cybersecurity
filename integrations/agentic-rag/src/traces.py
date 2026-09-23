import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

TRACES_FILE = Path("data/traces.jsonl")
TRACES_FILE.parent.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_trace_id() -> str:
    return str(uuid.uuid4())


def append_step(trace_id: str, step_index: int, payload: dict) -> None:
    """
    Append a single step to the trace file. Thread-safe.
    Each line is a self-contained JSON object.
    """
    record = {
        "trace_id": trace_id,
        "step_index": step_index,
        "ts": _now_iso(),
        **payload,
    }
    with _lock:
        with TRACES_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")


def _read_all(max_lines: int = 5000) -> list:
    """Read the tail of the traces file (newest appended at end)."""
    if not TRACES_FILE.exists():
        return []
    with TRACES_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = lines[-max_lines:]
    records = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def list_traces(limit: int = 50) -> list:
    """
    Return a list of trace summaries (most recent first).
    A trace summary includes trace_id, start/end times, and step count.
    """
    records = _read_all()
    by_trace: dict = {}
    for r in records:
        tid = r.get("trace_id")
        if not tid:
            continue
        entry = by_trace.setdefault(tid, {
            "trace_id": tid,
            "start_ts": r.get("ts"),
            "end_ts": r.get("ts"),
            "steps": 0,
            "query": None,
            "route": None,
        })
        entry["end_ts"] = r.get("ts")
        entry["steps"] += 1
        if r.get("kind") == "request":
            entry["query"] = r.get("query")
            entry["route"] = r.get("route")

    ordered = sorted(by_trace.values(), key=lambda x: x["end_ts"] or "", reverse=True)
    return ordered[:limit]


def get_trace(trace_id: str) -> list:
    """Return all steps for a single trace, ordered by step_index."""
    records = _read_all()
    steps = [r for r in records if r.get("trace_id") == trace_id]
    steps.sort(key=lambda x: x.get("step_index", 0))
    return steps


def delete_traces_file() -> None:
    """Used in tests to start with a clean file."""
    with _lock:
        if TRACES_FILE.exists():
            TRACES_FILE.unlink()


if __name__ == "__main__":
    import json

    delete_traces_file()

    tid = new_trace_id()
    append_step(tid, 0, {"kind": "request", "query": "test query", "route": "hybrid"})
    append_step(tid, 1, {"kind": "tool_call", "tool": "retrieve", "args": {"query": "test"}})
    append_step(tid, 2, {"kind": "tool_result", "tool": "retrieve", "ok": True, "summary": "5 chunks"})
    append_step(tid, 3, {"kind": "answer", "text": "5 failed login attempts."})

    print("Traces:", json.dumps(list_traces(), indent=2))
    print()
    print("Trace steps:", json.dumps(get_trace(tid), indent=2))