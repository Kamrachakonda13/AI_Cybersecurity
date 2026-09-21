from test_v12 import db
from app.services.v37_security_graph_intelligence import intelligence_overview, control_evidence

def test_v37_graph_intelligence(db):
    out=intelligence_overview(db)
    assert out["release"]=="3.7"
    assert "graph" in out and "controls" in out and "drift_signals" in out
    assert "control" in out["graph"]["node_types"]

def test_v37_control_evidence(db):
    out=control_evidence(db)
    assert "controls" in out and "evidence_receipts" in out
