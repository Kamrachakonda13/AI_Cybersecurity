"""VEYRA checklist runner (governed, non-executing stub).

Reads `CHECKLISTS` from `checklist_registry` and produces a structured
`ChecklistRun` object describing what a run *would* do.

This module intentionally does NOT execute anything:
- No shell, no network, no DB writes.
- Every run is created in status `not_implemented` until a real executor
  lands in a later sub-commit (P4-3d+).

The goal of P4-3c is to lock down the interface and the guardrails:
  * unknown checklist ids are rejected
  * boundary text from the registry is surfaced on every run
  * evidence_expected is surfaced so downstream UI can render it
  * runs are immutable (frozen dataclass)

Execution semantics (real actions, DB persistence, API exposure) arrive in
later sub-commits and MUST go through the existing execution_plane gates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from app.services.checklist_registry import CHECKLISTS

RunStatus = Literal["not_implemented", "pending", "completed", "failed"]


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
