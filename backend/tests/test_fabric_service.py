"""Tests for backend/app/services/fabric.py.

Covers pure helpers (utc, stable_hash, normalize_event) and DB-backed
functions (security_fabric_overview, ai_attack_paths, _bfs_paths).
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models as _models  # noqa: registers tables
from app.db import Base
from app.services import fabric


REPO = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO / "backend" / "app" / "services" / "fabric.py"


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
# Pure helpers
# ---------------------------------------------------------------------------

def test_utc_returns_timezone_aware():
    t = fabric.utc()
    assert isinstance(t, datetime)
    assert t.tzinfo is not None


def test_stable_hash_deterministic():
    a = fabric.stable_hash({"x": 1, "y": 2})
    b = fabric.stable_hash({"y": 2, "x": 1})
    assert a == b
    assert isinstance(a, str)
    assert len(a) == 64


def test_stable_hash_changes_with_content():
    assert fabric.stable_hash({"a": 1}) != fabric.stable_hash({"a": 2})


def test_stable_hash_handles_non_serializable():
    """Uses default=str for things like datetime/uuid."""
    h = fabric.stable_hash(
        {"when": datetime.now(timezone.utc), "id": uuid.uuid4()})
    assert len(h) == 64


# ---------------------------------------------------------------------------
# normalize_event
# ---------------------------------------------------------------------------

def test_normalize_event_shape():
    evt = fabric.normalize_event("ai", "agent.invoke")
    expected = {
        "event_id", "trace_id", "plane", "event_type", "actor", "source",
        "target", "risk_score", "severity", "payload", "event_sha256", "observed_at",
    }
    assert set(evt.keys()) == expected


def test_normalize_event_echoes_inputs():
    evt = fabric.normalize_event(
        plane="ai", event_type="agent.invoke",
        actor="alice", source="srv-1", target="tool-x",
        risk_score=50, payload={"k": "v"}, trace_id="t-123",
    )
    assert evt["plane"] == "ai"
    assert evt["event_type"] == "agent.invoke"
    assert evt["actor"] == "alice"
    assert evt["source"] == "srv-1"
    assert evt["target"] == "tool-x"
    assert evt["risk_score"] == 50
    assert evt["payload"] == {"k": "v"}
    assert evt["trace_id"] == "t-123"


def test_normalize_event_severity_bands():
    """Severity bands: CRITICAL≥90, HIGH≥70, MEDIUM≥40, LOW>0, INFO=0."""
    for risk, expected in [
        (0, "INFO"),
        (1, "LOW"),
        (39, "LOW"),
        (40, "MEDIUM"),
        (69, "MEDIUM"),
        (70, "HIGH"),
        (89, "HIGH"),
        (90, "CRITICAL"),
        (100, "CRITICAL"),
    ]:
        evt = fabric.normalize_event("ai", "x", risk_score=risk)
        assert evt["severity"] == expected, f"risk={risk}"


def test_normalize_event_event_id_is_uuid4():
    evt = fabric.normalize_event("ai", "x")
    # uuid4 format check
    uuid_re = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
    assert uuid_re.match(evt["event_id"]), evt["event_id"]


def test_normalize_event_hash_is_over_body():
    """The event_sha256 should be stable over the same inputs (minus UUID/timestamp)."""
    evt = fabric.normalize_event("ai", "x", actor="alice", risk_score=50)
    body = {
        "plane": "ai", "event_type": "x", "actor": "alice", "source": "",
        "target": "", "risk_score": 50, "payload": {}, "trace_id": "",
    }
    expected_hash = hashlib.sha256(
        json.dumps(body, sort_keys=True, default=str).encode()
    ).hexdigest()
    assert evt["event_sha256"] == expected_hash


def test_normalize_event_observed_at_is_iso():
    evt = fabric.normalize_event("ai", "x")
    # Should be ISO 8601 parseable
    datetime.fromisoformat(evt["observed_at"])


# ---------------------------------------------------------------------------
# security_fabric_overview
# ---------------------------------------------------------------------------

def test_overview_shape_on_empty_db():
    db = _db()
    try:
        result = fabric.security_fabric_overview(db)
        expected_keys = {
            "planes", "open_findings", "open_incidents",
            "queued_security_jobs", "ai_runtime_events",
        }
        assert set(result.keys()) == expected_keys
    finally:
        db.close()


def test_overview_plane_keys():
    db = _db()
    try:
        planes = fabric.security_fabric_overview(db)["planes"]
        assert set(planes.keys()) == {
            "observation", "detection", "intelligence",
            "response", "governance", "evidence",
        }
    finally:
        db.close()


def test_overview_zero_on_empty_db():
    db = _db()
    try:
        result = fabric.security_fabric_overview(db)
        for plane, count in result["planes"].items():
            assert count == 0, plane
        assert result["open_findings"] == 0
        assert result["open_incidents"] == 0
        assert result["queued_security_jobs"] == 0
        assert result["ai_runtime_events"] == 0
    finally:
        db.close()


# ---------------------------------------------------------------------------
# ai_attack_paths
# ---------------------------------------------------------------------------

def test_attack_paths_shape_on_empty_db():
    db = _db()
    try:
        result = fabric.ai_attack_paths(db)
        assert set(result.keys()) == {"nodes", "edges", "paths"}
        assert isinstance(result["nodes"], dict)
        assert isinstance(result["edges"], list)
        assert isinstance(result["paths"], list)
    finally:
        db.close()


def test_attack_paths_always_includes_internet_node():
    db = _db()
    try:
        result = fabric.ai_attack_paths(db)
        assert "internet" in result["nodes"]
        assert result["nodes"]["internet"]["kind"] == "internet"
    finally:
        db.close()


def test_attack_paths_respects_max_paths():
    db = _db()
    try:
        result = fabric.ai_attack_paths(db, max_paths=2)
        assert len(result["paths"]) <= 2
    finally:
        db.close()


# ---------------------------------------------------------------------------
# _bfs_paths (pure)
# ---------------------------------------------------------------------------

def test_bfs_paths_empty_graph():
    result = fabric._bfs_paths({}, [], 10)
    assert result == []


def test_bfs_paths_identity_to_cloud():
    nodes = {
        "identity:alice": {"kind": "identity"},
        "cloud:prod": {"kind": "cloud"},
    }
    edges = [{"src": "identity:alice",
              "dst": "cloud:prod", "relation": "accesses"}]
    paths = fabric._bfs_paths(nodes, edges, 10)
    assert ["identity:alice", "cloud:prod"] in paths


def test_bfs_paths_identity_to_ai():
    nodes = {
        "identity:alice": {"kind": "identity"},
        "ai:chatbot": {"kind": "ai"},
    }
    edges = [{"src": "identity:alice",
              "dst": "ai:chatbot", "relation": "controls"}]
    paths = fabric._bfs_paths(nodes, edges, 10)
    assert any(p[-1] == "ai:chatbot" for p in paths)


def test_bfs_paths_avoids_cycles():
    nodes = {"identity:a": {"kind": "identity"}, "cloud:c": {"kind": "cloud"}}
    edges = [
        {"src": "identity:a", "dst": "cloud:c"},
        {"src": "cloud:c", "dst": "identity:a"},
    ]
    paths = fabric._bfs_paths(nodes, edges, 10)
    for p in paths:
        # no node repeats within a path
        assert len(p) == len(set(p)), p


def test_bfs_paths_respects_max_paths():
    nodes = {"identity:a": {"kind": "identity"}}
    edges = []
    for i in range(20):
        nodes[f"cloud:c{i}"] = {"kind": "cloud"}
        edges.append({"src": "identity:a", "dst": f"cloud:c{i}"})
    paths = fabric._bfs_paths(nodes, edges, 5)
    assert len(paths) <= 5


def test_bfs_paths_ignores_short_paths():
    """A path of length 1 (identity only) is not a valid target path."""
    nodes = {"identity:a": {"kind": "identity"}}
    paths = fabric._bfs_paths(nodes, [], 10)
    assert paths == []


# ---------------------------------------------------------------------------
# Structural guards
# ---------------------------------------------------------------------------

def test_module_does_not_execute_shell():
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert not re.search(r"\bos\.system\b", source)
    assert not re.search(r"\bos\.popen\b", source)
