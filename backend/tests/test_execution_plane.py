"""VEYRA source module `backend/tests/test_execution_plane.py`. See `docs/CODEBASE_GUIDE_V27.md` for the module purpose, symbols, dependencies, and maintenance guidance."""
from fastapi.testclient import TestClient
from app.main import app


def test_execution_plane_admin_lifecycle(monkeypatch):
    monkeypatch.setenv("VEYRA_ADMIN_TOKEN", "secret")
    c = TestClient(app)
    h={"X-VEYRA-Admin-Token":"secret"}
    r=c.post('/api/admin/ethical-hacking/jobs',headers=h,json={
        "tool":"Nmap","target":"lab-vulnerable-web","scope":["lab-vulnerable-web"],
        "approval_ticket":"APP-100","environment":"lab","purpose":"authorized lab assessment"})
    assert r.status_code==200
    job=r.json(); jid=job["job_id"]
    assert job["execution"]=="not_started"
    assert c.post(f'/api/admin/ethical-hacking/jobs/{jid}/dispatch',headers=h).status_code==409
    assert c.post(f'/api/admin/ethical-hacking/jobs/{jid}/approve',headers=h).status_code==200
    assert c.post(f'/api/admin/ethical-hacking/jobs/{jid}/dispatch',headers=h).json()["status"]=="queued_for_isolated_worker"
    ev=c.post(f'/api/admin/ethical-hacking/jobs/{jid}/evidence',headers=h,json={"payload":{
        "source":"worker-01","result_type":"port_inventory","summary":"lab evidence","data":{"ports":[80]}}})
    assert ev.status_code==200 and len(ev.json()["sha256"])==64
    assert c.get(f'/api/admin/ethical-hacking/jobs/{jid}/evidence',headers=h).status_code==200


def test_execution_plane_non_admin(monkeypatch):
    monkeypatch.setenv("VEYRA_ADMIN_TOKEN", "secret")
    c=TestClient(app)
    assert c.get('/api/admin/ethical-hacking/jobs').status_code==403
