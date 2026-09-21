"""Tests for teams/remediation/triage (`services/teams.py` + 4 new routes).

Help: uses FastAPI `TestClient` with an in-memory `StaticPool` SQLite DB
(single shared connection — plain `:memory:` would lose tables between sessions).
Covers: playbook matrix completeness, no-exploit-instruction guardrail on team
content, endpoint wiring, triage validation + brute-force recommendation.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.db import Base
from app.main import app
from app.services.teams import SEVERITY_PLAYBOOKS, CATEGORY_PLAYBOOKS, RED_TEAM, BLUE_TEAM


def test_playbook_matrix_complete():
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        p = SEVERITY_PLAYBOOKS[sev]
        assert p["answer"] and len(p["fix_steps"]) >= 2 and p["verify"]
    for cat in ("exposure", "kev", "privilege", "brute_force", "ai_internet", "eml", "pcap"):
        assert cat in CATEGORY_PLAYBOOKS


def test_teams_have_no_exploit_instructions():
    blob = str(RED_TEAM) + str(BLUE_TEAM)
    # Guardrail: content must not contain operational attack instructions
    for banned in ("msfconsole", "exploit/multi", "meterpreter>"):
        assert banned not in blob


import app.models as _models  # noqa: ensure all models registered on Base


def _client():
    import os
    from sqlalchemy.pool import StaticPool
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Testing = sessionmaker(bind=eng)
    assert hasattr(_models, "Device")
    Base.metadata.create_all(bind=eng)
    from app import db as dbmod
    dbmod.SessionLocal = Testing
    return TestClient(app)


def test_remediation_and_teams_endpoints():
    c = _client()
    r = c.get("/api/remediation?severity=CRITICAL&category=kev")
    assert r.status_code == 200 and "fix_steps" in r.json()
    assert c.get("/api/teams/red").status_code == 200
    assert c.get("/api/teams/blue").status_code == 200


def test_triage_requires_subject_and_correlates():
    c = _client()
    assert c.post("/api/session/triage", json={}).status_code == 400
    c.post("/api/ingest/logins", json=[{"username": "victim", "source_ip": "7.7.7.7",
                                        "success": False} for _ in range(6)])
    r = c.post("/api/session/triage", json={"ip": "7.7.7.7"})
    assert r.status_code == 200
    body = r.json()
    assert body["failed_logins"] == 6
    assert any("Brute-force" in s for s in body["recommendations"])
