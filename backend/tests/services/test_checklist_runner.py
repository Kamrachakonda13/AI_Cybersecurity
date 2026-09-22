"""Tests for the checklist runner stub (P4-3c).

The runner must:
- reject unknown ids
- surface registry metadata on every run
- NEVER execute anything (status is always `not_implemented`)
- be importable without DB / network access
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.services.checklist_registry import CHECKLISTS
from app.services.checklist_runner import (
    ChecklistRun,
    UnknownChecklistError,
    get_checklist,
    list_checklists,
    run_checklist,
    runnable_ids,
)


# ---------------------------------------------------------------------------
# Registry access helpers
# ---------------------------------------------------------------------------

def test_list_checklists_returns_registry():
    items = list_checklists()
    assert isinstance(items, list)
    assert len(items) == len(CHECKLISTS)


def test_list_checklists_is_a_copy():
    a = list_checklists()
    b = list_checklists()
    assert a == b
    a.clear()
    assert list_checklists()  # unaffected


def test_get_checklist_known_id():
    first = CHECKLISTS[0]
    entry = get_checklist(first["id"])
    assert entry["id"] == first["id"]
    assert entry["domain"] == first["domain"]


def test_get_checklist_unknown_id_raises():
    with pytest.raises(UnknownChecklistError):
        get_checklist("does-not-exist")


def test_unknown_checklist_error_is_keyerror():
    # Backwards-compatible with callers catching KeyError.
    assert issubclass(UnknownChecklistError, KeyError)


def test_runnable_ids_matches_registry_order():
    assert runnable_ids() == [c["id"] for c in CHECKLISTS]


# ---------------------------------------------------------------------------
# run_checklist
# ---------------------------------------------------------------------------

def test_run_known_checklist_returns_run():
    first = CHECKLISTS[0]
    run = run_checklist(first["id"])
    assert isinstance(run, ChecklistRun)
    assert run.checklist_id == first["id"]
    assert run.domain == first["domain"]
    assert run.category == first["category"]
    assert run.name == first["name"]
    assert run.owner_role == first["owner_role"]
    assert run.cadence == first["cadence"]
    assert run.tier == first["tier"]
    assert run.scope == first["scope"]
    assert run.evidence_expected == tuple(first["evidence"])
    assert run.boundary == first["boundary"]


def test_run_status_is_never_executed():
    for entry in CHECKLISTS:
        run = run_checklist(entry["id"])
        assert run.status == "not_implemented", entry["id"]


def test_run_records_requested_at_in_utc():
    run = run_checklist(CHECKLISTS[0]["id"])
    assert isinstance(run.requested_at, datetime)
    assert run.requested_at.tzinfo == timezone.utc


def test_run_is_frozen():
    run = run_checklist(CHECKLISTS[0]["id"])
    with pytest.raises(Exception):  # FrozenInstanceError
        run.status = "completed"  # type: ignore[misc]


def test_run_carries_parameters_when_supplied():
    run = run_checklist(CHECKLISTS[0]["id"], parameters={"target": "lab"})
    assert run.parameters == {"target": "lab"}


def test_run_parameters_default_to_empty_dict():
    run = run_checklist(CHECKLISTS[0]["id"])
    assert run.parameters == {}


def test_run_unknown_id_raises():
    with pytest.raises(UnknownChecklistError):
        run_checklist("does-not-exist")


def test_notes_mark_stub():
    run = run_checklist(CHECKLISTS[0]["id"])
    assert "stub" in run.notes.lower()


# ---------------------------------------------------------------------------
# Guardrail: every registered checklist is runnable as a stub
# ---------------------------------------------------------------------------

def test_every_checklist_is_runnable_as_stub():
    for entry in CHECKLISTS:
        run = run_checklist(entry["id"])
        assert run.checklist_id == entry["id"]
        assert run.boundary  # non-empty
        assert run.evidence_expected  # non-empty
