"""VEYRA baseline engine — approved baseline vs current drift (P6-B).

Baselines are explicitly approved, versioned, and attributed to an owner.
Drift = set difference between approved snapshot and current observation.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone

from typing import Any


def _sha(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def create_baseline(
    db,
    scope: str,
    snapshot: dict,
    owner: str = "security_operator",
    approved: bool = False,
) -> object:
    """Create a baseline row (not yet approved unless flagged)."""
    from app.models import NetworkBaseline

    bid = "base_" + uuid.uuid4().hex[:16]
    sha = _sha(snapshot)
    row = NetworkBaseline(
        baseline_id=bid,
        scope=scope,
        owner=owner,
        snapshot_json=json.dumps(snapshot, sort_keys=True),
        snapshot_sha256=sha,
        approved=approved,
        approved_at=datetime.now(timezone.utc) if approved else None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def approve_baseline(db, baseline_id: str) -> object:
    from app.models import NetworkBaseline

    row = db.query(NetworkBaseline).filter(NetworkBaseline.baseline_id == baseline_id).first()
    if not row:
        raise ValueError(f"Baseline {baseline_id} not found")
    row.approved = True
    row.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return row


def get_approved_baseline(db, scope: str):
    from app.models import NetworkBaseline

    return (
        db.query(NetworkBaseline)
        .filter(NetworkBaseline.scope == scope, NetworkBaseline.approved.is_(True))
        .order_by(NetworkBaseline.created_at.desc())
        .first()
    )


def drift_against_baseline(approved_snapshot: dict, current: dict) -> dict:
    """Compare two snapshots. Returns {added, removed, changed, drift_count}."""
    a_keys = set(approved_snapshot.keys())
    c_keys = set(current.keys())
    added = sorted(c_keys - a_keys)
    removed = sorted(a_keys - c_keys)
    changed = sorted(k for k in a_keys & c_keys if approved_snapshot[k] != current[k])
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "drift_count": len(added) + len(removed) + len(changed),
        "has_drift": bool(added or removed or changed),
    }


def evaluate_current(db, scope: str, current: dict) -> dict:
    """Evaluate current observation against approved baseline for scope."""
    base = get_approved_baseline(db, scope)
    if not base:
        return {"scope": scope, "baseline": None, "drift": None, "status": "no_baseline"}
    approved_snapshot = json.loads(base.snapshot_json or "{}")
    drift = drift_against_baseline(approved_snapshot, current)
    status = "drift" if drift["has_drift"] else "stable"
    return {"scope": scope, "baseline_id": base.baseline_id, "drift": drift, "status": status}
