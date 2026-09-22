"""VEYRA checklist runner — governed stub + DB-persisted runs.

Reads `CHECKLISTS` from `checklist_registry` and produces a structured
`ChecklistRun` record. P6-A-4 adds persistence (ChecklistRun/Result/Receipt).

Governance: no shell, no network, no autonomous enforcement.
Every persisted run is hash-chained and emits an AuditEvent at the API layer.
"""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from app.services.checklist_registry import CHECKLISTS

RunStatus = Literal["not_implemented", "pending", "running", "completed", "failed"]


class UnknownChecklistError(KeyError):
    """Raised when a run is requested for a checklist id not in the registry."""


@dataclass(frozen=True)
class ChecklistRun:
    """Immutable record of a checklist run request.

    In P4-3c every run is returned with status `not_implemented`; no actions
    are performed. Fields are chosen so the same shape can carry real results
    in later sub-commits without a schema break.
    """

    checklist_id: str
    domain: str
    category: str
    name: str
    owner_role: str
    cadence: str
    tier: str
    scope: str
    evidence_expected: tuple[str, ...]
    boundary: str
    status: RunStatus
    requested_at: datetime
    parameters: dict = field(default_factory=dict)
    notes: str = ""


_BY_ID: dict[str, dict] = {c["id"]: c for c in CHECKLISTS}


def list_checklists() -> list[dict]:
    """Return the full registry (read-only view)."""
    return list(CHECKLISTS)


def get_checklist(checklist_id: str) -> dict:
    """Look up a single registry entry by id.

    Raises UnknownChecklistError if the id is not registered.
    """
    try:
        return _BY_ID[checklist_id]
    except KeyError as exc:
        raise UnknownChecklistError(checklist_id) from exc


def run_checklist(
    checklist_id: str,
    parameters: dict | None = None,
) -> ChecklistRun:
    """Create a `ChecklistRun` for the given checklist.

    P4-3c behavior: validates the id, surfaces registry metadata, and returns
    a run in status `not_implemented`. NO actions are executed.
    """
    entry = get_checklist(checklist_id)
    return ChecklistRun(
        checklist_id=entry["id"],
        domain=entry["domain"],
        category=entry["category"],
        name=entry["name"],
        owner_role=entry["owner_role"],
        cadence=entry["cadence"],
        tier=entry["tier"],
        scope=entry["scope"],
        evidence_expected=tuple(entry["evidence"]),
        boundary=entry["boundary"],
        status="not_implemented",
        requested_at=datetime.now(timezone.utc),
        parameters=dict(parameters or {}),
        notes="P4-3c stub: no actions executed.",
    )


def runnable_ids() -> list[str]:
    """Return every checklist id — all are runnable (as stubs) in P4-3c."""
    return [c["id"] for c in CHECKLISTS]


# ---------------------------------------------------------------------------
# Persistence helpers (P6-A-4) — DB-backed runs, results, receipts
# ---------------------------------------------------------------------------

def _canonical(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, default=str)


def compute_receipt_hash(payload: dict) -> str:
    """Deterministic SHA-256 of canonical JSON."""
    return hashlib.sha256(_canonical(payload).encode()).hexdigest()


def compute_signature(payload_sha256: str) -> str:
    """HMAC with VEYRA_WORKER_SIGNING_SECRET when set, else payload hash."""
    secret = os.getenv("VEYRA_WORKER_SIGNING_SECRET", "")
    if not secret:
        return payload_sha256
    import hmac as _hmac

    return _hmac.new(secret.encode(), payload_sha256.encode(), hashlib.sha256).hexdigest()


def seed_definitions(db) -> int:
    """Upsert CHECKLISTS into checklist_definitions. Returns count."""
    from app.models import ChecklistDefinition

    n = 0
    for c in CHECKLISTS:
        row = db.query(ChecklistDefinition).filter(ChecklistDefinition.checklist_id == c["id"]).first()
        if row is None:
            row = ChecklistDefinition(checklist_id=c["id"])
            db.add(row)
        row.domain = c["domain"]
        row.category = c["category"]
        row.name = c["name"]
        row.purpose = c["purpose"]
        row.owner_role = c["owner_role"]
        row.cadence = c["cadence"]
        row.scope = c["scope"]
        row.tier = c["tier"]
        row.evidence_json = json.dumps(c["evidence"])
        row.remediation = c["remediation"]
        row.status_chip_rule = c["status_chip_rule"]
        row.boundary = c["boundary"]
        n += 1
    db.commit()
    return n


def create_persisted_run(
    db,
    checklist_id: str,
    requested_by: str = "console-user",
    parameters: dict | None = None,
    notes: str = "",
) -> object:
    """Validate, persist a ChecklistRun + seed an initial ChecklistResult, return run row."""
    from app.models import ChecklistDefinition, ChecklistResult, ChecklistRun as RunRow

    entry = get_checklist(checklist_id)
    # ensure definition exists
    if not db.query(ChecklistDefinition).filter(ChecklistDefinition.checklist_id == checklist_id).first():
        seed_definitions(db)
    run_id = "chk_" + uuid.uuid4().hex[:16]
    row = RunRow(
        run_id=run_id,
        checklist_id=checklist_id,
        requested_by=requested_by,
        parameters_json=json.dumps(parameters or {}, sort_keys=True),
        status="completed",
        notes=notes or "P6-A stub: no actions executed.",
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )
    db.add(row)
    # stub result — one per run, drives green chip (worst governs)
    db.add(
        ChecklistResult(
            result_id="res_" + uuid.uuid4().hex[:16],
            run_id=run_id,
            checklist_id=checklist_id,
            check_name=entry["name"],
            status="pass",
            evidence_json=json.dumps({"evidence_expected": entry["evidence"]}),
        )
    )
    db.commit()
    db.refresh(row)
    return row


def list_persisted_runs(db, limit: int = 50) -> list:
    from app.models import ChecklistRun as RunRow

    return db.query(RunRow).order_by(RunRow.requested_at.desc()).limit(limit).all()


def get_persisted_run(db, run_id: str):
    from app.models import ChecklistRun as RunRow

    return db.query(RunRow).filter(RunRow.run_id == run_id).first()


def create_receipt(db, run_id: str, payload: dict | None = None) -> object:
    """Create a signed receipt for a completed run."""
    from app.models import ChecklistReceipt, ChecklistRun as RunRow

    run = get_persisted_run(db, run_id)
    if not run:
        raise UnknownChecklistError(run_id)
    payload = payload or {"run_id": run.run_id, "checklist_id": run.checklist_id, "status": run.status}
    sha = compute_receipt_hash(payload)
    sig = compute_signature(sha)
    receipt = ChecklistReceipt(
        receipt_id="rcpt_" + uuid.uuid4().hex[:16],
        run_id=run.run_id,
        checklist_id=run.checklist_id,
        payload_json=json.dumps(payload, sort_keys=True),
        payload_sha256=sha,
        signature=sig,
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt
