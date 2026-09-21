"""AegisX demo-data seeder (idempotent).

Help — what it does and what it depends on:
- `seed(db)`: populates a fresh database with a coherent mini-enterprise
  (4 assets → services → 2 scored findings → incidents → identities/sessions →
  flows → threat-intel → cloud → AI assets → audit event). Skips entirely when
  any `Asset` row exists, so it never duplicates data on restart.
- Depends on: all model classes from `app.models`, `calculate_risk`/`severity`
  from `services/risk` (finding scores). Called once by `app.main.lifespan`
  after `create_all`. Tests must NOT call it against the real DB.
"""
from sqlalchemy.orm import Session
from ..models import Asset, Service, Finding, Incident, AuditEvent, Identity, SessionEvent, NetworkFlow, ThreatIntel, CloudResource, AIAsset
from .risk import calculate_risk, severity

def seed(db: Session):
    if db.query(Asset).count(): return
    assets = [
        Asset(hostname="web-prod-01", ip_address="10.10.20.17", asset_type="web-server", environment="production", criticality=5, owner="Web Platform", external_exposure=True),
        Asset(hostname="ai-gateway-01", ip_address="10.10.20.31", asset_type="ai-service", environment="production", criticality=5, owner="AI Platform", external_exposure=True),
        Asset(hostname="vector-db-01", ip_address="10.10.30.12", asset_type="vector-db", environment="production", criticality=5, owner="Data Platform", external_exposure=False),
        Asset(hostname="dev-jump-01", ip_address="10.10.40.8", asset_type="workstation", environment="development", criticality=2, owner="Engineering", external_exposure=False),
    ]
    db.add_all(assets); db.flush()
    db.add_all([
        Service(asset_id=assets[0].id, port=443, protocol="TCP", service="HTTPS", process="nginx", pid=4821, user="svc-web", expected=True),
        Service(asset_id=assets[0].id, port=22, protocol="TCP", service="SSH", process="sshd", pid=731, user="root", expected=False),
        Service(asset_id=assets[1].id, port=443, protocol="TCP", service="AI API", process="uvicorn", pid=9122, user="svc-ai", expected=True),
        Service(asset_id=assets[2].id, port=6333, protocol="TCP", service="Vector DB", process="qdrant", pid=3021, user="svc-vector", expected=True),
    ])
    r = calculate_risk(criticality=5, cvss=9.8, exploitability=1, exposure=True, privilege=3, data_sensitivity=5, threat=1)
    db.add(Finding(asset_id=assets[0].id, title="Known-exploited internet-facing service", severity=severity(r), cvss=9.8, kev=True, exposure=True, data_sensitivity=5, risk_score=r, description="POC finding representing correlation of exposure, vulnerability severity and known exploitation."))
    r2 = calculate_risk(criticality=5, cvss=7.5, exploitability=.8, exposure=True, privilege=4, data_sensitivity=5, threat=.5, anomaly=.3)
    db.add(Finding(asset_id=assets[1].id, title="AI gateway over-privileged tool access", severity=severity(r2), cvss=7.5, exposure=True, data_sensitivity=5, risk_score=r2, description="POC AI security finding: agent identity has broader tool access than required."))
    db.add_all([
        Incident(title="Internet-facing critical service requires investigation", severity="CRITICAL", asset="web-prod-01", summary="Correlate exposed service, known exploitation and business criticality."),
        Incident(title="AI agent privilege boundary review", severity="HIGH", asset="ai-gateway-01", summary="Review tool permissions, data paths and approval boundaries."),
    ])
    db.add_all([
        Identity(username="admin.ops", identity_type="human", privilege=5, mfa_enabled=True, owner="Security Operations"),
        Identity(username="svc-ai", identity_type="service", privilege=5, mfa_enabled=False, owner="AI Platform"),
        Identity(username="analyst", identity_type="human", privilege=3, mfa_enabled=True, owner="SOC"),
        Identity(username="backup.bot", identity_type="service", privilege=4, mfa_enabled=False, owner="Infrastructure"),
    ])
    db.add_all([
        SessionEvent(username="svc-ai", asset_id=assets[1].id, source_ip="10.10.20.31", application="AI Gateway", auth_method="service-token", privileged=True, anomaly_score=.82),
        SessionEvent(username="admin.ops", asset_id=assets[3].id, source_ip="10.10.40.8", application="Admin Console", auth_method="SSO+MFA", privileged=True, anomaly_score=.12),
        SessionEvent(username="analyst", asset_id=assets[3].id, source_ip="10.10.40.8", application="SOC Console", auth_method="SSO+MFA", privileged=False, anomaly_score=.05),
    ])
    db.add_all([
        NetworkFlow(src_asset_id=assets[0].id, dst_asset_id=assets[1].id, src_ip="10.10.20.17", dst_ip="10.10.20.31", dst_port=443, protocol="TCP", bytes_out=48120, risk_score=32),
        NetworkFlow(src_asset_id=assets[1].id, dst_asset_id=assets[2].id, src_ip="10.10.20.31", dst_ip="10.10.30.12", dst_port=6333, protocol="TCP", bytes_out=912000, risk_score=61),
        NetworkFlow(src_asset_id=assets[3].id, dst_asset_id=None, src_ip="10.10.40.8", dst_ip="203.0.113.50", dst_port=443, protocol="TCP", bytes_out=1840000, action="allow", risk_score=74),
    ])
    db.add_all([
        ThreatIntel(source="CISA KEV", indicator="CVE-2025-DEMO", indicator_type="CVE", title="Known exploited vulnerability affecting exposed service", severity="CRITICAL", exploited=True, description="Demo intelligence record for correlation workflow."),
        ThreatIntel(source="MITRE ATT&CK", indicator="T1046", indicator_type="TECHNIQUE", title="Network Service Scanning", severity="MEDIUM", exploited=False, description="Discovery technique used for attack-path context."),
        ThreatIntel(source="MITRE ATT&CK", indicator="T1078", indicator_type="TECHNIQUE", title="Valid Accounts", severity="HIGH", exploited=False, description="Identity context for suspicious authenticated activity."),
    ])
    db.add_all([
        CloudResource(provider="AWS", resource_id="prod-web-alb", resource_type="load-balancer", region="ap-south-1", public_exposure=True, misconfiguration="Internet-facing admin path", risk_score=78),
        CloudResource(provider="AWS", resource_id="prod-data-bucket", resource_type="object-storage", region="ap-south-1", public_exposure=False, misconfiguration="Missing retention policy", risk_score=44),
        CloudResource(provider="Azure", resource_id="ai-prod-kv", resource_type="key-vault", region="centralindia", public_exposure=False, misconfiguration="Excessive service principal access", risk_score=67),
    ])
    db.add_all([
        AIAsset(name="Aegis AI Gateway", asset_type="AI application", provider="Internal", owner="AI Platform", exposure="internet", risk_score=82, approval_boundary=True),
        AIAsset(name="Security Analyst Agent", asset_type="agent", provider="Internal", owner="SOC", exposure="internal", risk_score=58, approval_boundary=True),
        AIAsset(name="Production RAG Vector Store", asset_type="vector database", provider="Qdrant", owner="Data Platform", exposure="internal", risk_score=71, approval_boundary=True),
    ])
    db.add(AuditEvent(actor="system", action="seed_demo_environment", target="aegisx", outcome="success"))
    db.commit()

# v2.5 bootstrap: create the single sudo account from environment variables.
def seed_identity(db):
    import os
    from .auth import hash_password
    from ..models import UserAccount
    if db.query(UserAccount).count(): return
    username=os.getenv("VEYRA_SUDO_USERNAME", "").strip()
    password=os.getenv("VEYRA_SUDO_PASSWORD", "")
    if not username or not password:
        return
    if len(password) < 12:
        raise RuntimeError("VEYRA_SUDO_PASSWORD must be at least 12 characters")
    db.add(UserAccount(username=username, display_name="Sudo Administrator", password_hash=hash_password(password), role="sudo", status="active", mfa_required=True, must_change_password=True))
    db.add(AuditEvent(actor="system", action="bootstrap_sudo_account", target=username, outcome="success"))
    db.commit()
