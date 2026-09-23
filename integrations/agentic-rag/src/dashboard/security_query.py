"""
Phase 9.8 — Query helpers for the dashboard Security page.

Reads data/security/blocked.jsonl (the injection firewall's log) and
produces aggregates for the dashboard.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Optional

BLOCKED_LOG = Path("data/security/blocked.jsonl")


def _read_events() -> list[dict]:
    if not BLOCKED_LOG.exists():
        return []
    events = []
    for line in BLOCKED_LOG.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def summary() -> dict:
    """Top-level counts for the summary cards."""
    events = [e for e in _read_events() if e.get("event") == "blocked"]
    total = len(events)

    # Last 24h (relative to most recent event, not wall-clock — the
    # data is generated in a fixed window)
    if events:
        latest_ts = max(e["ts"] for e in events)
        cutoff = latest_ts - 86400
        last_24h = sum(1 for e in events if e["ts"] >= cutoff)
    else:
        last_24h = 0

    by_source = Counter(e.get("source", "unknown") for e in events)
    by_category = Counter(e.get("category") or "unknown" for e in events)

    return {
        "total": total,
        "last_24h": last_24h,
        "by_source": dict(by_source),
        "by_category": dict(by_category),
        "avg_confidence": (
            round(sum(e.get("confidence", 0) for e in events) / total, 3)
            if total else 0.0
        ),
    }


def blocks_by_category() -> list[dict]:
    events = [e for e in _read_events() if e.get("event") == "blocked"]
    counts = Counter(e.get("category") or "unknown" for e in events)
    return [{"category": k, "count": v} for k, v in sorted(counts.items(), key=lambda kv: -kv[1])]


def blocks_by_source() -> list[dict]:
    events = [e for e in _read_events() if e.get("event") == "blocked"]
    counts = Counter(e.get("source") or "unknown" for e in events)
    return [{"source": k, "count": v} for k, v in sorted(counts.items(), key=lambda kv: -kv[1])]


def recent_blocks(limit: int = 50) -> list[dict]:
    events = [e for e in _read_events() if e.get("event") == "blocked"]
    events.sort(key=lambda e: e.get("ts", 0), reverse=True)
    return events[:limit]


if __name__ == "__main__":
    print(json.dumps(summary(), indent=2))
