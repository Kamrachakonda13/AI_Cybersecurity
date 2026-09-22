"""VEYRA trends — posture, MTTR, coverage, regression (P6-H).

Pure DB aggregation, no external calls. Advisory only.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta


def _parse_day(iso: str) -> str:
    try:
        return iso[:10]
    except Exception:
        return ""


def coverage_percent(db) -> dict:
    from app.models import ChecklistDefinition, ChecklistRun

    total_defs = db.query(ChecklistDefinition).count()
    if not total_defs:
        # fallback to registry size if not seeded
        from app.services.checklist_registry import CHECKLISTS

        total_defs = len(CHECKLISTS)
    runs = db.query(ChecklistRun).all()
    exercised = len({r.checklist_id for r in runs})
    pct = round(100 * exercised / total_defs, 1) if total_defs else 0
    return {"total_definitions": total_defs, "exercised": exercised, "percent": pct}


def posture_over_time(db, days: int = 14) -> list[dict]:
    from app.models import ChecklistRun

    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.query(ChecklistRun).filter(ChecklistRun.requested_at >= since).all()
    by_day = Counter(_parse_day(r.requested_at.isoformat()) for r in rows)
    out = []
    for i in range(days):
        d = (datetime.now(timezone.utc) - timedelta(days=days - 1 - i)).date().isoformat()
        out.append({"date": d, "runs": by_day.get(d, 0)})
    return out


def mttr_per_checklist(db) -> list[dict]:
    from app.models import ChecklistRun

    rows = db.query(ChecklistRun).all()
    by_check: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        if r.started_at and r.completed_at:
            delta = (r.completed_at - r.started_at).total_seconds()
            by_check[r.checklist_id].append(delta)
    out = []
    for cid, vals in by_check.items():
        out.append({"checklist_id": cid, "samples": len(vals), "mean_seconds": round(sum(vals) / len(vals), 1) if vals else 0, "p95_seconds": round(sorted(vals)[int(len(vals) * 0.95)] if vals else 0, 1)})
    return sorted(out, key=lambda x: x["mean_seconds"], reverse=True)[:20]


def regression_flags(db, days: int = 7) -> list[dict]:
    """Flag checklists whose runs in last 7d exceed baseline by 2x."""
    series = posture_over_time(db, days=days)
    avg = sum(s["runs"] for s in series) / len(series) if series else 0
    flags = []
    for s in series:
        if avg and s["runs"] > 2 * avg:
            flags.append({"date": s["date"], "runs": s["runs"], "avg": round(avg, 1), "flag": "spike"})
    return flags


def overview(db) -> dict:
    return {
        "coverage": coverage_percent(db),
        "posture_series": posture_over_time(db, 14),
        "mttr": mttr_per_checklist(db),
        "regressions": regression_flags(db, 7),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
