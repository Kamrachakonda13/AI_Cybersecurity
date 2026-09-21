"""AegisX source module `backend/tests/test_detection_mesh_v22.py`. See `docs/CODEBASE_GUIDE_V27.md` for the module purpose, symbols, dependencies, and maintenance guidance."""
import os
from fastapi.testclient import TestClient
from app.main import app
os.environ.setdefault("AEGISX_ADMIN_TOKEN","test-admin")
os.environ.setdefault("COLLECTOR_TOKEN","test-collector")

def test_detection_mesh_overview_and_rules():
    with TestClient(app) as client:
        r=client.get("/api/detection-mesh/overview"); assert r.status_code==200
        assert r.json()["rules"] >= 5
        r=client.get("/api/detection-mesh/rules"); assert r.status_code==200
        assert len(r.json()) >= 5

def test_alert_triggers_investigation():
    with TestClient(app) as client:
        # Keep the fixture idempotent across local runs that reuse the SQLite database.
        from app.db import SessionLocal
        from app.models import UnifiedSecurityEvent
        db=SessionLocal(); existing=db.query(UnifiedSecurityEvent).filter(UnifiedSecurityEvent.event_id=="mesh-test-v22-001").first()
        if existing: db.delete(existing); db.commit()
        db.close()
        r=client.post("/api/detection-mesh/alerts",headers={"X-Collector-Token":"test-collector"},json={
            "event_id":"mesh-test-v22-001","plane":"network","event_type":"network_anomaly","target":"srv-01","risk_score":85,"severity":"CRITICAL","payload":{"bytes":9999}})
        assert r.status_code==200, r.text
        j=r.json(); assert j["decision"]=="investigate"; assert j.get("case_id")

def test_duplicate_is_idempotent():
    with TestClient(app) as client:
        h={"X-Collector-Token":"test-collector"}
        body={"event_id":"mesh-test-v22-dup","event_type":"network_anomaly","risk_score":80,"target":"srv-02"}
        assert client.post("/api/detection-mesh/alerts",headers=h,json=body).status_code==200
        j=client.post("/api/detection-mesh/alerts",headers=h,json=body).json(); assert j["status"]=="duplicate"
