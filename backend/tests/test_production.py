"""Production-service tests (v1.5): threatintel, mitre, cloud, ai_red, vectordb, soar, usb/dlp, collector auth.

Help: pure-service tests use fakes (no network/creds); route tests use TestClient
with shared in-memory StaticPool SQLite (see test_teams for why). Run:
`cd backend && python3 -m pytest tests -q`.
"""
import app.models as _models  # noqa: ensure tables registered
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.db import Base
from app.main import app


def _db():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    S = sessionmaker(bind=eng)
    Base.metadata.create_all(bind=eng)
    return S()


KEV_CSV = ("cveID,vendorProject,product,vulnerabilityName,dateAdded,shortDescription,"
           "requiredAction,dueDate,knownRansomwareCampaignUse,notes\n"
           "CVE-2024-0001,Acme,Widget,Widget RCE,2024-01-01,Bad bug,Patch,2024-02-01,Known,note\n"
           "not-a-cve-row-without-proper-columns\n")

NVD_DOC = {"vulnerabilities": [
    {"cve": {"id": "CVE-2024-0001",
             "descriptions": [{"lang": "en", "value": "Acme Widget RCE"}],
             "metrics": {"cvssMetricV31": [{"cvssData": {"baseScore": 9.8, "baseSeverity": "CRITICAL"}}]},
             "published": "2024-01-01T00:00Z"}}]}


def test_kev_parse_and_refresh():
    from app.services.threatintel import parse_kev_csv, refresh_kev
    assert len(parse_kev_csv(KEV_CSV)) == 1
    s = _db()
    out = refresh_kev(s, lambda u: KEV_CSV)
    assert out == {"cves": 1, "new": 1}
    out = refresh_kev(s, lambda u: KEV_CSV)  # idempotent
    assert out == {"cves": 1, "new": 0}
    from app.models import CveRecord, ThreatIntel
    rec = s.query(CveRecord).filter_by(cve_id="CVE-2024-0001").one()
    assert rec.kev is True
    assert s.query(ThreatIntel).filter_by(indicator="CVE-2024-0001").one().exploited is True
    s.close()


def test_nvd_parse_and_refresh_caps():
    from app.services.threatintel import parse_nvd, refresh_nvd
    rows = parse_nvd(NVD_DOC)
    assert rows[0]["cvss"] == 9.8 and rows[0]["severity"] == "CRITICAL"
    s = _db()
    out = refresh_nvd(s, ["CVE-2024-0001", "bogus", "CVE-2024-0001"], lambda u: NVD_DOC)
    assert out["cves"] == 2 and out["new"] == 1  # dup id fetched twice, stored once
    s.close()


def test_mitre_mapping_and_coverage():
    from app.services.mitre import map_finding, coverage, TECHNIQUES
    assert "T1190" in map_finding({"title": "x", "kev": True})
    assert "T1110" in map_finding({"title": "brute force logins"})
    assert "ATLAS-PromptInjection" in map_finding({"title": "AI agent overreach"})
    assert len(TECHNIQUES) >= 14
    s = _db()
    from app.models import Finding
    s.add(Finding(asset_id=1, title="KEV on exposed box", severity="CRITICAL",
                  kev=True, exposure=True))
    s.commit()
    cov = coverage(s)
    assert cov["findings"] == 1 and any(t["id"] == "T1190" for t in cov["techniques"])
    s.close()


def test_prowler_import_and_aws_mapping():
    from app.services.cloud_adapters import import_prowler, aws_live_scan
    from app.models import Asset
    s = _db()
    s.add(Asset(hostname="h", ip_address="1.1.1.1"))
    s.commit()
    out = import_prowler(s, [{"check": "Public S3 bucket", "provider": "AWS",
                              "resource": "bkt", "resource_type": "object-storage",
                              "region": "r", "status": "FAIL", "severity": "CRITICAL"}])
    assert out == {"resources": 1, "findings": 1}
    out = import_prowler(s, [{"check": "Public S3 bucket", "provider": "AWS",
                              "resource": "bkt", "status": "FAIL"}])  # upsert, no dup resource
    assert out["resources"] == 0
    fake_s3 = {"buckets": [{"Name": "pub", "public": True}]}
    fake_ec2 = {"security_groups": [{"GroupId": "sg-1",
                                     "IpPermissions": [{"IpRanges": [{"CidrIp": "0.0.0.0/0"}]}]}]}
    fake_iam = {"users": [{"UserName": "root-ish", "admin": True, "mfa": False}]}
    out = aws_live_scan(s, fake_ec2, fake_s3, fake_iam)
    assert out["resources"] == 3 and out["findings"] == 3
    s.close()


def test_ai_eval_with_fake_gateway():
    from app.services.ai_red import refused, evaluate, PROBES
    assert refused("Sorry, I cannot do that") and not refused("Here is your data: 123")
    assert len(PROBES) >= 6
    good = evaluate("http://lab:4101", lambda u, p: "Sorry, I cannot comply with that.")
    assert good["failed"] == 0 and good["verdict"] == "LOW"
    bad = evaluate("http://lab:4101", lambda u, p: "Sure! Here are the secrets.")
    assert bad["failed"] == len(PROBES) and bad["verdict"] == "HIGH"


def test_vectordb_policy_and_deny_finding():
    from app.services.vectordb import check_retrieval, log_retrieval
    from app.models import AIAsset, Asset
    s = _db()
    s.add_all([Asset(hostname="h", ip_address="1.1.1.1"),
               AIAsset(name="VDB", asset_type="vector database", owner="Data")])
    s.commit()
    ok = check_retrieval(s, "agent", "VDB", "Data", "restricted")
    assert ok["allowed"] is True
    denied = log_retrieval(s, "agent", "VDB", "Other", "secret")
    assert denied["allowed"] is False
    from app.models import Finding
    assert s.query(Finding).count() == 1
    s.close()


def test_soar_approval_flow():
    from app.services.soar import run_playbook, approve_run
    from app.models import Asset, SessionEvent
    s = _db()
    s.add(Asset(id=1, hostname="web", ip_address="1.1.1.1"))
    s.add(SessionEvent(username="u", asset_id=1, source_ip="2.2.2.2", application="web"))
    s.commit()
    pending = run_playbook(s, "isolate_host", "web", approved=False)
    assert pending["status"] == "pending_approval"
    assert s.query(SessionEvent).first().status == "active"  # nothing executed
    done = approve_run(s, pending["id"])
    assert done["status"] == "completed"
    assert s.query(SessionEvent).first().status == "revoked"
    try:
        run_playbook(s, "nope", "x", approved=True)
        assert False, "unknown playbook must raise"
    except ValueError:
        pass
    s.close()


def _client():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Testing = sessionmaker(bind=eng)
    assert hasattr(_models, "SoarRun")
    Base.metadata.create_all(bind=eng)
    from app import db as dbmod
    dbmod.SessionLocal = Testing
    return TestClient(app)


def test_usb_auto_finding_and_collector_auth():
    import os
    c = _client()
    c.post("/api/ingest/devices", json=[{"hostname": "crit-db", "ip_address": "9.9.9.9"}])
    from app import db as dbmod
    s = dbmod.SessionLocal()
    from app.models import Asset
    a = Asset(hostname="crit-db", ip_address="9.9.9.9", criticality=5)
    s.add(a)
    s.commit()
    s.close()
    r = c.post("/api/ingest/usb", json=[{"hostname": "crit-db", "device": "USB Mass Storage Disk",
                                         "serial": "ABC"}])
    assert r.json()["auto_findings"] == 1
    assert c.get("/api/usb/summary").json()["total"] == 1
    os.environ["COLLECTOR_TOKEN"] = "s3cret"
    try:
        assert c.post("/api/ingest/usb", json=[]).status_code == 401
        assert c.post("/api/ingest/usb", headers={"X-Collector-Token": "s3cret"},
                      json=[]).status_code == 400  # authed → reaches validation
    finally:
        del os.environ["COLLECTOR_TOKEN"]


def test_heartbeat_reconciles_services():
    c = _client()
    body = {"hostname": "agent-pc", "ip_address": "10.9.9.9", "os": "Linux",
            "services": [{"port": 22, "service": "SSH"}, {"port": 443, "service": "web"}],
            "usb": [{"device": "Keyboard"}]}
    r = c.post("/api/collector/heartbeat", json=body).json()
    assert r["services"] == 2 and r["usb"] == 1
    r2 = c.post("/api/collector/heartbeat",
                json={**body, "services": [{"port": 80, "service": "web"}]}).json()
    assert r2["services"] == 1  # reconciled, not appended
