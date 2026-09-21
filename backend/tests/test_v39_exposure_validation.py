from app.db import SessionLocal, engine, Base
import app.models  # register tables
Base.metadata.create_all(bind=engine)
from app.models import AgentPolicy, AgentRuntimeEvent
from app.services.v39_autonomous_exposure_validation import exposure_overview, investigate_agent

def test_v39_overview_has_fabric():
    db=SessionLocal()
    try:
        out=exposure_overview(db)
        assert out["release"]=="3.9"
        assert "AI Agent" in out["platforms"]
        assert "rogue_agent_candidates" in out
    finally: db.close()

def test_v39_investigates_unregistered_agent():
    db=SessionLocal()
    try:
        aid="test-rogue-v39"
        db.query(AgentRuntimeEvent).filter(AgentRuntimeEvent.agent_id==aid).delete()
        db.add(AgentRuntimeEvent(trace_id="t-v39",agent_id=aid,operation="tool_call",provider="test",model="test",tool_name="unexpected-tool",policy_decision="allow",risk_score=85))
        db.commit()
        out=investigate_agent(db,aid)
        assert out["status"]=="investigating"
        assert out["case_id"].startswith("rag_")
        assert out["containment_plan"]
    finally: db.close()
