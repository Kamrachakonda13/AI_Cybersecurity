"""Tests for sudo one-click runs, time-boxed grants and access-request flow.

Covers: sudo bypasses per-tool approval (stage→approve→queue in one call),
non-sudo runs degrade to pending approval, expired grants read as "none",
access request → sudo inbox → timed approval, tool form schemas, and the
no-raw-shell guardrail on runner forms.
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.db import Base
from app.main import app
import app.models as _models  # noqa: ensure all models registered on Base
from app.models import UserAccount, UserToolPermission
from app.services.auth import hash_password, issue_session, get_tool_level


def _client():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Testing = sessionmaker(bind=eng)
    Base.metadata.create_all(bind=eng)
    from app import db as dbmod
    dbmod.SessionLocal = Testing
    # routes.py captured SessionLocal by direct import; rebind it too so
    # Bearer-session lookups hit the test database.
    import app.api.routes as routesmod
    routesmod.SessionLocal = Testing
    c = TestClient(app)
    db = Testing()
    sudo = UserAccount(username="sudo.t", display_name="S", password_hash=hash_password("sudo-password-12345"), role="sudo", status="active", mfa_required=False, must_change_password=False)
    analyst = UserAccount(username="analyst.t", display_name="A", password_hash=hash_password("analyst-password-12345"), role="analyst", status="active", mfa_required=False, must_change_password=False)
    viewer = UserAccount(username="viewer.t", display_name="V", password_hash=hash_password("viewer-password-12345"), role="viewer", status="active", mfa_required=False, must_change_password=False)
    db.add_all([sudo, analyst, viewer]); db.commit()
    toks = {u.username: issue_session(db, u) for u in (sudo, analyst, viewer)}
    ids = {u.username: u.id for u in (sudo, analyst, viewer)}
    db.close()
    return c, toks, ids


def _auth(tok):
    return {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}


def test_sudo_run_is_one_click_approved():
    c, toks, _ = _client()
    r = c.post("/api/admin/ethical-hacking/jobs/run", headers=_auth(toks["sudo.t"]), json={
        "tool": "Nmap", "target": "lab-web", "scope": ["lab-web"],
        "environment": "lab", "purpose": "Authorized assessment",
        "params": {"profile": "Quick port sweep", "ports": "80,443"}})
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["status"] == "queued_for_isolated_worker"
    assert j["execution"] == "queued"
    assert j["params"]["ports"] == "80,443"


def test_viewer_cannot_run_tools():
    c, toks, _ = _client()
    r = c.post("/api/admin/ethical-hacking/jobs/run", headers=_auth(toks["viewer.t"]), json={
        "tool": "Nmap", "target": "lab-web", "scope": ["lab-web"],
        "environment": "lab", "purpose": "x"})
    assert r.status_code == 403


def test_analyst_run_needs_grant_then_stays_pending():
    c, toks, ids = _client()
    body = {"tool": "Nmap", "target": "lab-web", "scope": ["lab-web"],
            "approval_ticket": "CHG-1", "environment": "lab", "purpose": "Authorized assessment"}
    assert c.post("/api/admin/ethical-hacking/jobs/run", headers=_auth(toks["analyst.t"]), json=body).status_code == 403
    # sudo grants execute_request for 5h
    from app import db as dbmod
    db = dbmod.SessionLocal()
    db.add(UserToolPermission(user_id=ids["analyst.t"], tool_id="nmap", level="execute_request",
                             granted_by="sudo.t",
                             expires_at=datetime.now(timezone.utc) + timedelta(hours=5)))
    db.commit(); db.close()
    r = c.post("/api/admin/ethical-hacking/jobs/run", headers=_auth(toks["analyst.t"]), json=body)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "pending_approval"


def test_expired_grant_reads_as_none():
    c, toks, ids = _client()
    from app import db as dbmod
    db = dbmod.SessionLocal()
    db.add(UserToolPermission(user_id=ids["analyst.t"], tool_id="nmap", level="execute_request",
                             granted_by="sudo.t",
                             expires_at=datetime.now(timezone.utc) - timedelta(minutes=1)))
    db.commit()
    assert get_tool_level(db, ids["analyst.t"], "nmap") == "none"
    db.close()
    r = c.get("/api/me/tool-permissions", headers=_auth(toks["analyst.t"]))
    assert r.status_code == 200


def test_access_request_to_approval_flow():
    c, toks, _ = _client()
    r = c.post("/api/tools/requests", headers=_auth(toks["analyst.t"]), json={
        "tool_id": "nmap", "level": "plan", "reason": "Lab exercise", "duration_hours": 2})
    assert r.status_code == 200, r.text
    rid = r.json()["request_id"]
    assert r.json()["notified"]["channel"] in {"email", "log"}
    mine = c.get("/api/tools/requests?status=all", headers=_auth(toks["analyst.t"])).json()
    assert any(x["request_id"] == rid for x in mine)
    inbox = c.get("/api/tools/requests?status=pending", headers=_auth(toks["sudo.t"])).json()
    assert any(x["request_id"] == rid for x in inbox)
    d = c.post(f"/api/tools/requests/{rid}/decide", headers=_auth(toks["sudo.t"]),
               json={"approve": True, "duration_hours": 5})
    assert d.status_code == 200, d.text
    assert d.json()["grant"]["level"] == "plan"
    assert d.json()["grant"]["expires_at"] is not None
    notes = c.get("/api/admin/notifications", headers=_auth(toks["sudo.t"]))
    assert notes.status_code == 200 and len(notes.json()) >= 1
    mynotes = c.get("/api/admin/notifications", headers=_auth(toks["analyst.t"]))
    assert mynotes.status_code == 200 and any(n["related_id"] == rid for n in mynotes.json())


def test_tool_form_schema_and_validation():
    c, toks, _ = _client()
    r = c.get("/api/admin/ethical-hacking/tools/nmap/form", headers=_auth(toks["sudo.t"]))
    assert r.status_code == 200, r.text
    names = [f["name"] for f in r.json()["fields"]]
    assert "target" in names and "profile" in names
    # guardrail: runner schemas carry named profiles, never raw shell
    blob = r.text
    for banned in ("msfconsole", "meterpreter>", "; rm ", "&&"):
        assert banned not in blob
    # metasploit refuses non-scanner modules
    bad = c.post("/api/admin/ethical-hacking/jobs/run", headers=_auth(toks["sudo.t"]), json={
        "tool": "Metasploit Framework", "target": "lab-web", "scope": ["lab-web"],
        "environment": "lab", "purpose": "Authorized assessment",
        "params": {"module": "exploit/multi/handler"}})
    assert bad.status_code == 400
