"""AegisX source module `backend/tests/test_admin_tools.py`. See `docs/CODEBASE_GUIDE_V27.md` for the module purpose, symbols, dependencies, and maintenance guidance."""
from fastapi.testclient import TestClient
from app.main import app


def test_admin_tools_require_admin(monkeypatch):
    monkeypatch.setenv("VEYRA_ADMIN_TOKEN", "secret")
    c = TestClient(app)
    assert c.get("/api/admin/ethical-hacking/tools").status_code == 403
    r = c.get("/api/admin/ethical-hacking/tools", headers={"X-AegisX-Admin-Token":"secret"})
    assert r.status_code == 200
    body = r.json()
    assert body["admin_only"] is True
    assert len(body["tools"]) >= 70
    assert any(x["name"] == "Metasploit Framework" for x in body["tools"])
    assert all(x["admin_only"] for x in body["tools"])


def test_worker_requires_auth(monkeypatch):
    monkeypatch.setenv('VEYRA_WORKER_TOKEN','worker-secret')
    from app.db import Base, engine
    Base.metadata.create_all(bind=engine)
    c=TestClient(app)
    assert c.get('/api/worker/jobs/next').status_code == 403
    assert c.get('/api/worker/jobs/next',headers={'X-AegisX-Worker-Token':'worker-secret'}).status_code == 200


def test_privileged_tool_requires_second_admin_gate(monkeypatch):
    monkeypatch.setenv("VEYRA_ADMIN_TOKEN", "admin")
    monkeypatch.setenv("VEYRA_PRIVILEGED_ADMIN_TOKEN", "priv")
    from app.db import Base, engine
    Base.metadata.create_all(bind=engine)
    c = TestClient(app)
    payload = {"tool":"SQLMap","target":"lab-app","scope":["lab-app"],"approval_ticket":"APP-123","environment":"lab","purpose":"Authorized lab SQL injection assessment"}
    h = {"X-AegisX-Admin-Token":"admin"}
    assert c.post('/api/admin/ethical-hacking/jobs', headers=h, json=payload).status_code == 403
    h["X-AegisX-Privileged-Admin-Token"] = "priv"
    assert c.post('/api/admin/ethical-hacking/jobs', headers=h, json=payload).status_code == 200
