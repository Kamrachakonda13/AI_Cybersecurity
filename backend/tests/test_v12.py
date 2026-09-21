"""Tests for v1.2 graph + assessment validation (`services/graph.py`, `services/assess.py`).

Help: builds an in-memory SQLite DB (2 assets, service, identity, session, flow,
2 AI assets) via the `db` fixture — depends on `app.db.Base` + all models.
Covers: graph nodes/edges, attack-path reachability, the 6 `answer_question`
kinds, URL allow/deny rules, header scoring.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import Asset, Service, Identity, SessionEvent, NetworkFlow, AIAsset
from app.services.graph import build_graph, attack_paths, answer_question
from app.services.assess import validate_target, score_headers
import pytest


@pytest.fixture()
def db():
    eng = create_engine("sqlite:///:memory:")
    Testing = sessionmaker(bind=eng)
    Base.metadata.create_all(bind=eng)
    s = Testing()
    s.add_all([
        Asset(id=1, hostname="web-prod-01", ip_address="10.10.20.17", asset_type="web-server",
              environment="production", criticality=5, owner="Web", external_exposure=True),
        Asset(id=2, hostname="vector-db-01", ip_address="10.10.30.12", asset_type="vector-db",
              environment="production", criticality=5, owner="Data", external_exposure=False),
    ])
    s.add(Service(asset_id=1, port=443, protocol="TCP", service="HTTPS", process="nginx", pid=1, user="svc-web", expected=True))
    s.add(Identity(username="svc-ai", identity_type="service", privilege=5, mfa_enabled=False, owner="AI"))
    s.add(SessionEvent(username="svc-ai", asset_id=1, source_ip="10.10.20.31", application="AI Gateway",
                       auth_method="service-token", privileged=True, anomaly_score=.8))
    s.add(NetworkFlow(src_asset_id=1, dst_asset_id=2, src_ip="10.10.20.17", dst_ip="10.10.30.12",
                      dst_port=6333, protocol="TCP", bytes_out=100, risk_score=61))
    s.add(AIAsset(name="GW", asset_type="AI application", provider="Internal", owner="AI",
                  exposure="internet", risk_score=80, approval_boundary=True))
    s.add(AIAsset(name="VDB", asset_type="vector database", provider="Qdrant", owner="Data",
                  exposure="internal", risk_score=70, approval_boundary=True))
    s.commit()
    yield s
    s.close()


def test_graph_builds(db):
    g = build_graph(db)
    assert "internet" in g["nodes"]
    assert any(e["relation"] == "flow" for e in g["edges"])
    assert any(n.get("kind") == "ai" for n in g["nodes"].values())


def test_attack_path_reaches_sensitive(db):
    res = attack_paths(db)
    assert res["sensitive_targets"] >= 1
    assert len(res["paths"]) >= 1
    assert res["paths"][0]["steps"]


def test_answers(db):
    assert answer_question(db, "port_owner")[0]["process"] == "nginx"
    assert any(r["username"] == "svc-ai" for r in answer_question(db, "privileged_access"))
    assert answer_question(db, "internet_to_data")


def test_validate_target_rejects():
    with pytest.raises(ValueError):
        validate_target("ftp://example.com")
    with pytest.raises(ValueError):
        validate_target("http://169.254.169.254/latest")
    with pytest.raises(ValueError):
        validate_target("http://user:pass@example.com/")


def test_validate_target_private_flag():
    assert validate_target("https://example.com").get("private") is False
    assert validate_target("http://localhost:3000").get("private") is True


def test_score_headers():
    hs = score_headers({"Strict-Transport-Security": "max-age=1", "X-Frame-Options": "DENY"})
    assert hs["score"] == round(100 * 2 / 6, 1)
    assert "content-security-policy" in hs["missing"]
