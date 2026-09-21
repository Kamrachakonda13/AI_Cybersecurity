from app.db import SessionLocal, Base, engine
import app.models
Base.metadata.create_all(bind=engine)
from app.models import ToolDefinition, ToolRelease, ToolDeployment
from app.services.v40_tool_supply_chain import sync_catalog, register_release, deployment_plan, overview

def test_v40_catalog_and_overview():
    db=SessionLocal()
    try:
        assert sync_catalog(db) >= 0
        out=overview(db)
        assert out["release"]=="4.0"
        assert "candidate" in out["channels"]
        assert "tuf" or out["sources"]
    finally: db.close()

def test_v40_release_verify_and_manifest():
    db=SessionLocal()
    try:
        tool="v40-test-tool"
        if not db.query(ToolDefinition).filter(ToolDefinition.tool_id==tool).first():
            db.add(ToolDefinition(tool_id=tool,name="V40 Test Tool",category="Test",purpose="test",upstream_source="test",resolver_kind="package")); db.commit()
        old=db.query(ToolRelease).filter(ToolRelease.tool_id==tool).all()
        for r in old: db.delete(r)
        db.commit()
        out=register_release(db,{"tool_id":tool,"version":"1.2.3","artifact_uri":"vault://test/tool","artifact_sha256":"b"*64,"signature_required":False,"provenance_required":False,"sbom_required":False})
        assert out["verification_status"]=="verified"
        plan=deployment_plan(db,tool,out["release_id"],"worker-v40",force=True)
        assert plan["state"]=="planned"
        assert plan["manifest"]["artifact_sha256"]=="b"*64
    finally: db.close()
