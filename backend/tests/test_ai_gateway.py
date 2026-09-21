"""AegisX source module `backend/tests/test_ai_gateway.py`. See `docs/CODEBASE_GUIDE_V27.md` for the module purpose, symbols, dependencies, and maintenance guidance."""
from fastapi.testclient import TestClient
import os
from app.main import app

os.environ["VEYRA_ADMIN_TOKEN"]="test-admin"
os.environ["VEYRA_AI_GATEWAY_TOKEN"]="test-ai"
client=TestClient(app)

def test_gateway_requires_token():
    r=client.post('/api/ai-gateway/evaluate',json={'agent_id':'agent-x','operation':'chat','input':'hello'})
    assert r.status_code==403

def test_gateway_enrollment_and_decision():
    r=client.put('/api/ai-gateway/policy',headers={'X-AegisX-Admin-Token':'test-admin'},json={'agent_id':'agent-x','allowed_tools':['search'],'allowed_operations':['chat','retrieval'],'max_risk_score':60,'require_human_approval':True,'enabled':True})
    assert r.status_code==200
    r=client.post('/api/ai-gateway/evaluate',headers={'X-AegisX-AI-Token':'test-ai'},json={'agent_id':'agent-x','operation':'chat','input':'hello','provider':'local','model':'internal-model'})
    assert r.status_code==200 and r.json()['decision']['decision']=='allow'

def test_gateway_blocks_unallowlisted_tool():
    r=client.post('/api/ai-gateway/evaluate',headers={'X-AegisX-AI-Token':'test-ai'},json={'agent_id':'agent-x','operation':'chat','tool_name':'shell','input':'do thing'})
    assert r.status_code==200 and r.json()['decision']['decision']=='deny'
