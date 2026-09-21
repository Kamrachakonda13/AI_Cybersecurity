"""VEYRA source module `backend/tests/test_ai_security.py`. See `docs/CODEBASE_GUIDE_V27.md` for the module purpose, symbols, dependencies, and maintenance guidance."""
from fastapi.testclient import TestClient
from app.main import app


def test_ai_security_catalog_and_controls():
    c=TestClient(app)
    r=c.get('/api/ai-security/catalog')
    assert r.status_code==200
    names={x['name'] for x in r.json()['tools']}
    assert {'NeuralTrust','Lakera Guard / Check Point AI Guardrails','TrojAI','CalypsoAI / F5 AI Security','Garak'} <= names
    r=c.get('/api/ai-security/controls')
    assert r.status_code==200
    assert any('Agent Control Standard' in x for x in r.json()['frameworks'])


def test_agent_posture():
    c=TestClient(app)
    r=c.post('/api/ai-security/agent-posture',json={'name':'internal-agent','tool_allowlist':['search'],'approval_boundary':True})
    assert r.status_code==200
    body=r.json()
    assert body['risk_score'] > 0
    assert any(x['control']=='Tool allowlist' and x['pass'] for x in body['checks'])
