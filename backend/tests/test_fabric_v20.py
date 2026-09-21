"""AegisX source module `backend/tests/test_fabric_v20.py`. See `docs/CODEBASE_GUIDE_V27.md` for the module purpose, symbols, dependencies, and maintenance guidance."""
from fastapi.testclient import TestClient
from app.main import app

def test_fabric_overview():
    with TestClient(app) as c:
        r=c.get('/api/fabric/overview')
        assert r.status_code==200
        assert 'planes' in r.json()

def test_fabric_event_requires_collector_when_configured(monkeypatch):
    monkeypatch.setenv('COLLECTOR_TOKEN','secret')
    with TestClient(app) as c:
        r=c.post('/api/fabric/events',json={'plane':'ai','event_type':'agent.invoke','risk_score':20})
        assert r.status_code==401
        r=c.post('/api/fabric/events',headers={'X-Collector-Token':'secret'},json={'plane':'ai','event_type':'agent.invoke','risk_score':20})
        assert r.status_code==200
        assert r.json()['severity']=='LOW'
