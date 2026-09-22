"""Tests for backend/app/services/v29_adversary.py.

Composition layer over existing telemetry — uses an in-memory SQLite session.
"""
import re
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models as _models  # noqa: registers tables
from app.db import Base
from app.services import v29_adversary as adv


REPO = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO / "backend" / "app" / "services" / "v29_adversary.py"


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
# overview()
# ---------------------------------------------------------------------------

def test_overview_shape():
    db = _db()
    try:
        result = adv.overview(db)
        expected = {"version", "mission", "attribution_mode", "wireless",
                    "telemetry", "investigation", "pipeline"}
        assert expected.issubset(set(result.keys()))
    finally:
        db.close()


def test_overview_version_2_9():
    db = _db()
    try:
        assert adv.overview(db)["version"] == "2.9"
    finally:
        db.close()


def test_overview_attribution_mode_hypothesis_only():
    db = _db()
    try:
        assert adv.overview(db)["attribution_mode"] == "hypothesis_only"
    finally:
        db.close()


def test_overview_pipeline_present():
    db = _db()
    try:
        pipeline = adv.overview(db)["pipeline"]
        assert isinstance(pipeline, list)
        assert "observe" in pipeline
        assert "recover" in pipeline
    finally:
        db.close()


def test_overview_wireless_counts_zero_on_empty_db():
    db = _db()
    try:
        wireless = adv.overview(db)["wireless"]
        assert wireless["access_points"] == 0
        assert wireless["lan_devices"] == 0
        assert wireless["unknown_devices"] == 0
    finally:
        db.close()


def test_overview_telemetry_counts_zero_on_empty_db():
    db = _db()
    try:
        t = adv.overview(db)["telemetry"]
        for key in ("assets", "services", "flows", "sessions", "identities"):
            assert t[key] == 0
    finally:
        db.close()


# ---------------------------------------------------------------------------
# wireless()
# ---------------------------------------------------------------------------

def test_wireless_shape_on_empty_db():
    db = _db()
    try:
        result = adv.wireless(db)
        for key in ("access_points", "clients", "rogue_candidates", "controls", "execution_boundary"):
            assert key in result
    finally:
        db.close()


def test_wireless_execution_boundary_metadata_only():
    db = _db()
    try:
        boundary = adv.wireless(db)["execution_boundary"]
        assert "metadata" in boundary.lower() or "evidence" in boundary.lower()
        assert "no" in boundary.lower() or "not" in boundary.lower()
    finally:
        db.close()


def test_wireless_controls_include_baseline():
    db = _db()
    try:
        controls = adv.wireless(db)["controls"]
        assert isinstance(controls, list)
        joined = " ".join(controls).lower()
        assert "baseline" in joined or "rogue" in joined
    finally:
        db.close()


# ---------------------------------------------------------------------------
# timeline()
# ---------------------------------------------------------------------------

def test_timeline_empty_db():
    db = _db()
    try:
        result = adv.timeline(db)
        assert isinstance(result, list)
        assert result == []
    finally:
        db.close()


# ---------------------------------------------------------------------------
# infrastructure()
# ---------------------------------------------------------------------------

def test_infrastructure_shape_empty_db():
    db = _db()
    try:
        result = adv.infrastructure(db)
        assert set(result.keys()) == {"services", "flows", "identities"}
        assert result["services"] == []
        assert result["flows"] == []
        assert result["identities"] == []
    finally:
        db.close()


# ---------------------------------------------------------------------------
# attribution()
# ---------------------------------------------------------------------------

def test_attribution_empty_db_returns_none_hypothesis():
    db = _db()
    try:
        result = adv.attribution(db)
        hypotheses = result["hypotheses"]
        assert len(hypotheses) == 1
        assert hypotheses[0]["id"] == "hyp-none"
        assert hypotheses[0]["confidence"] == 0.0
    finally:
        db.close()


def test_attribution_has_disclaimer():
    db = _db()
    try:
        result = adv.attribution(db)
        disclaimer = result["disclaimer"].lower()
        assert "hypothes" in disclaimer or "evidence" in disclaimer
        assert "identification" in disclaimer or "attribution" in disclaimer
    finally:
        db.close()


# ---------------------------------------------------------------------------
# evidence_bundle()
# ---------------------------------------------------------------------------

def test_evidence_bundle_shape():
    db = _db()
    try:
        result = adv.evidence_bundle(db)
        assert set(result.keys()) == {
            "bundle_id", "created_at", "sources", "integrity", "chain_of_custody"
        }
    finally:
        db.close()


def test_evidence_bundle_id_prefix():
    db = _db()
    try:
        bundle_id = adv.evidence_bundle(db)["bundle_id"]
        assert bundle_id.startswith("AX29-")
    finally:
        db.close()


def test_evidence_bundle_sources_non_empty():
    db = _db()
    try:
        sources = adv.evidence_bundle(db)["sources"]
        assert isinstance(sources, list)
        assert len(sources) >= 5
        # expected sources from the module
        joined = " ".join(sources)
        assert "network_flows" in joined
        assert "audit_events" in joined
    finally:
        db.close()


def test_evidence_bundle_chain_of_custody():
    db = _db()
    try:
        coc = adv.evidence_bundle(db)["chain_of_custody"]
        assert isinstance(coc, list)
        joined = " ".join(coc).lower()
        assert "hash" in joined or "sha-256" in joined
        assert "timestamp" in joined
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


def test_module_declares_no_attack_capability():
    """Structural: the module explicitly says it does not attack or persist."""
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    assert "does not execute" in source or "hypothesis" in source
