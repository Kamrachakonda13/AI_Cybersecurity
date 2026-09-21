from app.db import SessionLocal, Base, engine
import app.models
Base.metadata.create_all(bind=engine)
from app.models import ToolDefinition, ToolRelease, ToolDeployment
from app.services.v40_tool_supply_chain import register_release, deployment_plan
from app.services.v41_supply_chain_runtime import accept_verification_report, promote_release, rollback_on_failure

def _db(): return SessionLocal()

def _healthy_report(sha, deployment_id=None):
    checks={k:{"passed":True,"evidence":"fixture"} for k in ("artifact_digest","signature","provenance","sbom","vulnerability_scan","smoke_test","parser_regression","security_regression")}
    return {"worker_id":"v41-worker","artifact_sha256":sha,"checks":checks,"signature_status":"verified","provenance_status":"verified","sbom_status":"verified","deployment_id":deployment_id}

def test_v41_worker_verification_and_promotion():
    db=_db()
    try:
        tool="v41-test-tool-"+__import__("uuid").uuid4().hex[:8]; sha="a"*64
        if not db.query(ToolDefinition).filter(ToolDefinition.tool_id==tool).first():
            db.add(ToolDefinition(tool_id=tool,name="V41 Test",category="Test",purpose="test",upstream_source="test",resolver_kind="package")); db.commit()
        for x in db.query(ToolRelease).filter(ToolRelease.tool_id==tool).all(): db.delete(x)
        db.commit()
        r=register_release(db,{"tool_id":tool,"version":"2.0.0","artifact_uri":"vault://v41/test","artifact_sha256":sha,"signature_required":False,"provenance_required":False,"sbom_required":False,"channel":"candidate"})
        dep=deployment_plan(db,tool,r["release_id"],"v41-worker",force=True)
        result=accept_verification_report(db,r["release_id"],"v41-worker",_healthy_report(sha,dep["deployment_id"]))
        assert result["health_status"]=="healthy"
        promoted=promote_release(db,r["release_id"],"canary")
        assert promoted["channel"]=="canary"
    finally: db.close()

def test_v41_failed_verification_rejected():
    db=_db()
    try:
        tool="v41-fail-tool-"+__import__("uuid").uuid4().hex[:8]; sha="b"*64
        db.add(ToolDefinition(tool_id=tool,name="V41 Fail",category="Test",purpose="test",upstream_source="test",resolver_kind="package")); db.commit()
        r=register_release(db,{"tool_id":tool,"version":"1.0.0","artifact_uri":"vault://v41/fail","artifact_sha256":sha,"signature_required":False,"provenance_required":False,"sbom_required":False})
        report=_healthy_report(sha); report["checks"]["parser_regression"]["passed"]=False
        result=accept_verification_report(db,r["release_id"],"v41-worker",report)
        assert result["health_status"]=="failed"
    finally: db.close()
