"""Tests for backend/app/services/response_mesh.py.

Uses an in-memory SQLite session (matching test_discovery patterns).
Covers: rule seeding, event evaluation, alert ingestion, response action
lifecycle (request → verify), and structural boundaries.
"""
import json
import re
import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models as _models  # noqa: registers tables
from app.db import Base
from app.services import response_mesh


REPO = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO / "backend" / "app" / "services" / "response_mesh.py"


# ---------------------------------------------------------------------------
# Session fixture
# ---------------------------------------------------------------------------

def _db():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    S = sessionmaker(bind=eng)
    Base.metadata.create_all(bind=eng)
    return S()


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_default_rules_shape():
    assert isinstance(response_mesh.DEFAULT_RULES, list)
    assert len(response_mesh.DEFAULT_RULES) >= 5


def test_default_rules_have_required_fields():
    for r in response_mesh.DEFAULT_RULES:
        assert set(r.keys()) >= {
            "rule_id", "name", "source", "event_types", "min_risk_score", "action"
        }


def test_default_rule_ids_unique():
    ids = [r["rule_id"] for r in response_mesh.DEFAULT_RULES]
    assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# connector_health()
# ---------------------------------------------------------------------------

def test_connector_health_returns_list():
    result = response_mesh.connector_health()
    assert isinstance(result, list)
    assert len(result) >= 5


def test_connector_health_entries_shape():
    for entry in response_mesh.connector_health():
        assert "name" in entry
        assert "kind" in entry
        assert "status" in entry
        assert "mode" in entry


def test_connector_health_includes_soar():
    names = {c["name"] for c in response_mesh.connector_health()}
    assert any("SOAR" in n for n in names)


# ---------------------------------------------------------------------------
# ensure_rules()
# ---------------------------------------------------------------------------

def test_ensure_rules_seeds_defaults():
    from app.models import DetectionRule
    db = _db()
    try:
        assert db.query(DetectionRule).count() == 0
        response_mesh.ensure_rules(db)
        assert db.query(DetectionRule).count() == len(
            response_mesh.DEFAULT_RULES)
    finally:
        db.close()


def test_ensure_rules_idempotent():
    from app.models import DetectionRule
    db = _db()
    try:
        response_mesh.ensure_rules(db)
        response_mesh.ensure_rules(db)
        assert db.query(DetectionRule).count() == len(
            response_mesh.DEFAULT_RULES)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# evaluate_event()
# ---------------------------------------------------------------------------

def _seed_event(db, event_id=None, event_type="agent_tool_call", risk=75):
    from app.models import UnifiedSecurityEvent
    eid = event_id or f"evt-{uuid.uuid4().hex[:8]}"
    row = UnifiedSecurityEvent(
        event_id=eid, trace_id="t-1", plane="ai", event_type=event_type,
        actor="agent-x", source="ai-gateway", target="tool-y",
        risk_score=risk, severity="HIGH",
        payload=json.dumps({"k": "v"}), event_sha256="a" * 64,
    )
    db.add(row)
    db.commit()
    return eid


def test_evaluate_event_unknown_raises():
    db = _db()
    try:
        with pytest.raises(ValueError, match="Unknown event"):
            response_mesh.evaluate_event(db, "no-such-event")
    finally:
        db.close()


def test_evaluate_event_matches_high_risk_ai_tool_call():
    db = _db()
    try:
        eid = _seed_event(db, event_type="agent_tool_call", risk=75)
        result = response_mesh.evaluate_event(db, eid)
        assert result["event_id"] == eid
        assert result["decision"] == "investigate"
        assert len(result["matched"]) >= 1
        ids = {m["rule_id"] for m in result["matched"]}
        assert "DET-AI-001" in ids
    finally:
        db.close()


def test_evaluate_event_below_threshold_observes():
    db = _db()
    try:
        eid = _seed_event(db, event_type="agent_tool_call", risk=10)
        result = response_mesh.evaluate_event(db, eid)
        assert result["decision"] == "observe"
        assert result["matched"] == []
    finally:
        db.close()


def test_evaluate_event_unmatched_type_observes():
    db = _db()
    try:
        eid = _seed_event(db, event_type="__nonsense_event_type__", risk=99)
        result = response_mesh.evaluate_event(db, eid)
        assert result["decision"] == "observe"
    finally:
        db.close()


# ---------------------------------------------------------------------------
# ingest_alert()
# ---------------------------------------------------------------------------

def test_ingest_alert_creates_event():
    db = _db()
    try:
        result = response_mesh.ingest_alert(db, {
            "payload": {"x": 1},
            "event_type": "agent_tool_call",
            "risk_score": 80,
            "severity": "HIGH",
        })
        assert result["status"] == "ingested"
        assert "event_id" in result
    finally:
        db.close()


def test_ingest_alert_duplicate_returns_observe():
    db = _db()
    try:
        eid = f"evt-{uuid.uuid4().hex[:8]}"
        response_mesh.ingest_alert(
            db, {"event_id": eid, "event_type": "x", "payload": {}})
        second = response_mesh.ingest_alert(
            db, {"event_id": eid, "event_type": "x", "payload": {}})
        assert second["status"] == "duplicate"
        assert second["decision"] == "observe"
    finally:
        db.close()


def test_ingest_alert_matched_creates_case():
    db = _db()
    try:
        result = response_mesh.ingest_alert(db, {
            "event_type": "agent_tool_call",
            "risk_score": 90,
            "payload": {},
        })
        assert result["decision"] == "investigate"
        assert "case_id" in result
    finally:
        db.close()


# ---------------------------------------------------------------------------
# request_response()
# ---------------------------------------------------------------------------

def _seed_case(db):
    from app.models import InvestigationCase
    row = InvestigationCase(
        case_id=f"case-{uuid.uuid4().hex[:8]}", title="t", status="open")
    db.add(row)
    db.commit()
    return row.case_id


def test_request_response_rejects_unknown_action():
    db = _db()
    try:
        cid = _seed_case(db)
        with pytest.raises(ValueError, match="Unsupported response action"):
            response_mesh.request_response(
                db, cid, "launch_missiles", "host-1")
    finally:
        db.close()


def test_request_response_rejects_unknown_case():
    db = _db()
    try:
        with pytest.raises(ValueError, match="Unknown case"):
            response_mesh.request_response(
                db, "no-such-case", "isolate_host", "host-1")
    finally:
        db.close()


def test_request_response_without_approval_pending():
    db = _db()
    try:
        cid = _seed_case(db)
        result = response_mesh.request_response(
            db, cid, "isolate_host", "host-1")
        assert result["status"] == "pending_approval"
        assert result["verification_status"] == "not_started"
    finally:
        db.close()


def test_request_response_with_approval_ready_for_adapter():
    db = _db()
    try:
        cid = _seed_case(db)
        result = response_mesh.request_response(
            db, cid, "isolate_host", "host-1", approval_id="apr-1"
        )
        assert result["status"] == "approved_for_adapter"
        assert result["approval_id"] == "apr-1"
    finally:
        db.close()


def test_request_response_all_allowed_actions():
    db = _db()
    try:
        cid = _seed_case(db)
        for action in ("isolate_host", "revoke_sessions", "block_ip", "collect_evidence"):
            r = response_mesh.request_response(db, cid, action, "t")
            assert r["action"] == action
    finally:
        db.close()


# ---------------------------------------------------------------------------
# verify_response()
# ---------------------------------------------------------------------------

def test_verify_response_unknown_raises():
    db = _db()
    try:
        with pytest.raises(ValueError, match="Unknown response action"):
            response_mesh.verify_response(db, "no-such-action", True)
    finally:
        db.close()


def test_verify_response_success():
    db = _db()
    try:
        cid = _seed_case(db)
        action = response_mesh.request_response(db, cid, "isolate_host", "t")
        result = response_mesh.verify_response(
            db, action["action_id"], True, {"note": "ok"})
        assert result["status"] == "completed"
        assert result["verification_status"] == "verified"
        assert len(result["evidence_sha256"]) == 64
    finally:
        db.close()


def test_verify_response_failure():
    db = _db()
    try:
        cid = _seed_case(db)
        action = response_mesh.request_response(db, cid, "isolate_host", "t")
        result = response_mesh.verify_response(db, action["action_id"], False)
        assert result["status"] == "verification_failed"
        assert result["verification_status"] == "failed"
    finally:
        db.close()


# ---------------------------------------------------------------------------
# serialize_action() & list_actions()
# ---------------------------------------------------------------------------

def test_list_actions_empty():
    db = _db()
    try:
        assert response_mesh.list_actions(db) == []
    finally:
        db.close()


def test_list_actions_returns_recent():
    db = _db()
    try:
        cid = _seed_case(db)
        response_mesh.request_response(db, cid, "isolate_host", "h1")
        response_mesh.request_response(db, cid, "block_ip", "h2")
        rows = response_mesh.list_actions(db)
        assert len(rows) == 2
        for r in rows:
            assert "action_id" in r
            assert "case_id" in r
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Structural guards
# ---------------------------------------------------------------------------

def test_module_does_not_execute_shell():
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert not re.search(r"\bos\.system\b", source)
    assert not re.search(r"\bos\.popen\b", source)


def test_module_has_no_external_network_calls():
    """Structural: no requests/urllib/httpx imports."""
    source = MODULE_PATH.read_text(encoding="utf-8")
    for bad in ("import requests", "import httpx", "import urllib.request"):
        assert bad not in source, f"unexpected network import: {bad}"
