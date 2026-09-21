"""AegisX source module `backend/tests/test_intel_fusion_v23.py`. See `docs/CODEBASE_GUIDE_V27.md` for the module purpose, symbols, dependencies, and maintenance guidance."""
import os
from fastapi.testclient import TestClient
from app.main import app
from app.db import SessionLocal, Base, engine
from app.models import UnifiedSecurityEvent, ThreatIntel, InvestigationCase
os.environ.setdefault("VEYRA_ADMIN_TOKEN","test-admin")

def _seed_case():
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    import uuid
    event_id="v23-fusion-"+uuid.uuid4().hex
    ev=UnifiedSecurityEvent(event_id=event_id,trace_id="t-v23",plane="network",event_type="possible_exfiltration",actor="svc-admin",source="10.0.0.10",target="10.0.0.20",risk_score=88,severity="CRITICAL",payload='{"indicator":"evil.example","bytes_out":900000}',event_sha256="a"*64)
    db.add(ev); db.add(ThreatIntel(source="test-ti",indicator="evil.example",indicator_type="domain",title="Test IOC",severity="HIGH",exploited=True,description="fixture")); db.commit(); db.close()
    with TestClient(app) as c:
        r=c.post('/api/autonomous-soc/investigate',json={'event_id':event_id}); assert r.status_code==200, r.text; return r.json()['case_id']

def test_fusion_produces_intel_attack_mapping_and_hypotheses():
    case_id=_seed_case()
    with TestClient(app) as c:
        r=c.post(f'/api/intel-fusion/cases/{case_id}/enrich',headers={'X-AegisX-Admin-Token':'test-admin'}); assert r.status_code==200, r.text
        j=r.json(); assert j['intel_matches']; assert any(x['framework']=='MITRE ATT&CK' for x in j['techniques']); assert j['attribution_hypotheses']
        r=c.get('/api/intel-fusion/hypotheses',headers={'X-AegisX-Admin-Token':'test-admin'}); assert r.status_code==200; assert any(x['case_id']==case_id for x in r.json())

def test_fusion_is_hypothesis_only():
    with TestClient(app) as c:
        r=c.get('/api/intel-fusion/overview'); assert r.status_code==200; assert r.json()['attribution_mode']=='hypothesis_only'
