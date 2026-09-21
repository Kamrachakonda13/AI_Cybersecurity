"""VEYRA source module `backend/tests/test_autonomous_soc_v21.py`. See `docs/CODEBASE_GUIDE_V27.md` for the module purpose, symbols, dependencies, and maintenance guidance."""
from app.models import UnifiedSecurityEvent, InvestigationCase
from app.services.autonomous_soc import investigate_event, request_containment, decide_approval
from app.db import SessionLocal

def test_autonomous_soc_investigate_and_approve():
    db=SessionLocal()
    try:
        existing=db.query(UnifiedSecurityEvent).filter(UnifiedSecurityEvent.event_id=='test-v21-event').first()
        if existing: db.delete(existing); db.commit()
        e=UnifiedSecurityEvent(event_id='test-v21-event', plane='Detection', event_type='suspicious_agent_tool', actor='svc', source='agent-a', target='db-prod', risk_score=85, severity='CRITICAL', payload='{}', event_sha256='a'*64)
        db.add(e); db.commit()
        c=investigate_event(db,'test-v21-event')
        assert c['status']=='awaiting_approval'
        r=request_containment(db,c['case_id'],'collect_evidence','db-prod','Preserve triage evidence')
        assert r['status']=='pending'
        d=decide_approval(db,r['approval_id'],True,'tester')
        assert d['status']=='approved'
    finally:
        db.close()
