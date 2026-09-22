"""VEYRA SQLAlchemy entity models (table definitions).

Help — how this file fits together:
- Every class subclasses `Base` from `app.db`; `now()` stamps UTC datetimes.
- Importing this module REGISTERS all tables — `app.main.lifespan` relies on that
  for `Base.metadata.create_all()`, and `app.models/__init__.py` re-exports the
  class names used by `services/seed.py` and `api/routes.py`.
- Table groups: inventory (Asset, Service, CloudResource, AIAsset, Device),
  telemetry (SessionEvent, NetworkFlow, DnsQuery, LoginAttempt), security
  workflow (Finding, Incident, ThreatIntel, AuditEvent), identity (Identity).
- Adding a model? 1) define class here, 2) re-export in `models/__init__.py`,
  3) tables auto-create on next boot (no migrations in this POC).
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..db import Base

def now(): return datetime.now(timezone.utc)

class Asset(Base):
    """Monitored host/workload. `criticality` 1–5 feeds risk directly; `external_exposure` seeds graph attack paths."""
    __tablename__ = "assets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hostname: Mapped[str] = mapped_column(String(255), index=True)
    ip_address: Mapped[str] = mapped_column(String(64), index=True)
    asset_type: Mapped[str] = mapped_column(String(64), default="server")
    environment: Mapped[str] = mapped_column(String(64), default="lab")
    criticality: Mapped[int] = mapped_column(Integer, default=3)
    owner: Mapped[str] = mapped_column(String(255), default="Unassigned")
    external_exposure: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Service(Base):
    """Listening port on an asset with process/user attribution. `expected=False` means baseline drift (backdoor suspect)."""
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(Integer, index=True)
    port: Mapped[int] = mapped_column(Integer)
    protocol: Mapped[str] = mapped_column(String(16), default="TCP")
    service: Mapped[str] = mapped_column(String(128))
    process: Mapped[str] = mapped_column(String(128), default="unknown")
    pid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user: Mapped[str] = mapped_column(String(128), default="unknown")
    expected: Mapped[bool] = mapped_column(Boolean, default=True)

class Identity(Base):
    """Human/service account. `privilege` 4–5 = can reach sensitive workloads; `mfa_enabled=False` doubles takeover risk."""
    __tablename__ = "identities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), index=True)
    identity_type: Mapped[str] = mapped_column(String(64), default="user")
    privilege: Mapped[int] = mapped_column(Integer, default=1)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    owner: Mapped[str] = mapped_column(String(255), default="")

class SessionEvent(Base):
    """Authenticated session: who (`username`) reached which asset, how, and how anomalous (`anomaly_score` ≥ 0.7 = critical)."""
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), index=True)
    asset_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    source_ip: Mapped[str] = mapped_column(String(64))
    application: Mapped[str] = mapped_column(String(255))
    auth_method: Mapped[str] = mapped_column(String(64), default="SSO")
    privileged: Mapped[bool] = mapped_column(Boolean, default=False)
    anomaly_score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(32), default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class NetworkFlow(Base):
    """One observed connection. `risk_score` ≥ 70 = possible exfil/lateral movement; feeds graph `flow` edges."""
    __tablename__ = "network_flows"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    src_asset_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    dst_asset_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    src_ip: Mapped[str] = mapped_column(String(64))
    dst_ip: Mapped[str] = mapped_column(String(64))
    dst_port: Mapped[int] = mapped_column(Integer)
    protocol: Mapped[str] = mapped_column(String(16), default="TCP")
    bytes_out: Mapped[int] = mapped_column(Integer, default=0)
    action: Mapped[str] = mapped_column(String(32), default="allow")
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ThreatIntel(Base):
    """Intel record (CISA KEV CVE or MITRE ATT&CK technique). `exploited=True` raises the `threat` term in risk scoring."""
    __tablename__ = "threat_intel"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(64))
    indicator: Mapped[str] = mapped_column(String(255), index=True)
    indicator_type: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(255))
    severity: Mapped[str] = mapped_column(String(32), default="MEDIUM")
    exploited: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class CloudResource(Base):
    """Cloud inventory row (manual/API-ingested; live CSPM adapters are future work). `public_exposure` = directly reachable."""
    __tablename__ = "cloud_resources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(32))
    resource_id: Mapped[str] = mapped_column(String(255), index=True)
    resource_type: Mapped[str] = mapped_column(String(64))
    region: Mapped[str] = mapped_column(String(64), default="")
    public_exposure: Mapped[bool] = mapped_column(Boolean, default=False)
    misconfiguration: Mapped[str] = mapped_column(String(255), default="")
    risk_score: Mapped[float] = mapped_column(Float, default=0)

class AIAsset(Base):
    """AI app/agent/vector-DB. `exposure=internet` + tool permissions = prompt-injection/data-egress surface; graph links agents to vector stores via `retrieves` edges."""
    __tablename__ = "ai_assets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    asset_type: Mapped[str] = mapped_column(String(64))
    provider: Mapped[str] = mapped_column(String(128), default="")
    owner: Mapped[str] = mapped_column(String(255), default="")
    exposure: Mapped[str] = mapped_column(String(64), default="internal")
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    approval_boundary: Mapped[bool] = mapped_column(Boolean, default=True)

class Finding(Base):
    """Scored weakness on an asset. `severity`/`risk_score` come from `services/risk`; `kev`/`exposure` explain WHY it is critical."""
    __tablename__ = "findings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(255))
    severity: Mapped[str] = mapped_column(String(32))
    cvss: Mapped[float] = mapped_column(Float, default=0)
    kev: Mapped[bool] = mapped_column(Boolean, default=False)
    exposure: Mapped[bool] = mapped_column(Boolean, default=False)
    data_sensitivity: Mapped[int] = mapped_column(Integer, default=1)
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(32), default="open")
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Incident(Base):
    """SOC case needing a human decision. Status stays `open` until triaged; every response needs approval (Governance view)."""
    __tablename__ = "incidents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    severity: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="open")
    asset: Mapped[str] = mapped_column(String(255), default="Unknown")
    summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AuditEvent(Base):
    """Immutable audit trail: every ingestion, assessment, triage and analysis writes one row. Never delete in production."""
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor: Mapped[str] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(255))
    target: Mapped[str] = mapped_column(String(255), default="")
    outcome: Mapped[str] = mapped_column(String(32), default="success")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Device(Base):
    """Endpoint inventory heartbeat — YOUR OWN managed/lab devices only.

    Upserted by hostname (or mac when known). Never auto-scans; collectors
    push explicitly with operator consent + written scope.
    """
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hostname: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    ip_address: Mapped[str] = mapped_column(String(64), default="")
    mac: Mapped[str] = mapped_column(String(64), default="")
    os: Mapped[str] = mapped_column(String(128), default="")
    owner: Mapped[str] = mapped_column(String(255), default="")
    source: Mapped[str] = mapped_column(String(64), default="collector")
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class DnsQuery(Base):
    """DNS-metadata only (domain queried, NOT page content) — own network, consented."""
    __tablename__ = "dns_queries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hostname: Mapped[str] = mapped_column(String(255), index=True, default="")
    domain: Mapped[str] = mapped_column(String(255), index=True)
    query_type: Mapped[str] = mapped_column(String(16), default="A")
    hits: Mapped[int] = mapped_column(Integer, default=1)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class LoginAttempt(Base):
    """Auth outcomes on YOUR OWN systems — detects password-spray / brute force."""
    __tablename__ = "login_attempts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), index=True)
    source_ip: Mapped[str] = mapped_column(String(64), index=True)
    hostname: Mapped[str] = mapped_column(String(255), default="")
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    method: Mapped[str] = mapped_column(String(64), default="password")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class CveRecord(Base):
    """Normalized CVE from live CISA KEV / NVD feeds (`services/threatintel.py`).

    One row per `cve_id`; refresh upserts. `kev=True` means actively exploited —
    mirrors into a `ThreatIntel` row so graphs, investigations and KEV playbooks react.
    """
    __tablename__ = "cve_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cve_id: Mapped[str] = mapped_column(String(32), index=True, unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    cvss: Mapped[float] = mapped_column(Float, default=0)
    severity: Mapped[str] = mapped_column(String(16), default="")
    kev: Mapped[bool] = mapped_column(Boolean, default=False)
    published: Mapped[str] = mapped_column(String(32), default="")
    source: Mapped[str] = mapped_column(String(32), default="CISA/NVD")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class UsbEvent(Base):
    """USB device connect/block on a managed host (from endpoint agent heartbeat or ingest).

    Storage-class devices on criticality-5 assets auto-raise a HIGH finding in the ingest route.
    """
    __tablename__ = "usb_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hostname: Mapped[str] = mapped_column(String(255), index=True)
    device: Mapped[str] = mapped_column(String(255), default="")
    serial: Mapped[str] = mapped_column(String(128), default="")
    action: Mapped[str] = mapped_column(String(32), default="connect")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class DlpEvent(Base):
    """Data-loss-prevention signal: sensitive file observed leaving its boundary.

    `classification` in secret/restricted/internal/public; `action` in
    blocked/quarantined/allowed. An `allowed` secret is a policy gap → MEDIUM finding.
    """
    __tablename__ = "dlp_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hostname: Mapped[str] = mapped_column(String(255), default="")
    username: Mapped[str] = mapped_column(String(255), default="")
    filepath: Mapped[str] = mapped_column(String(512), default="")
    classification: Mapped[str] = mapped_column(String(32), default="internal")
    action: Mapped[str] = mapped_column(String(32), default="allowed")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class RetrievalEvent(Base):
    """AI retrieval audit: which agent read which vector store, for which tenant, and whether policy allowed it.

    Cross-tenant reads of non-public docs are denied by policy → HIGH finding (tenant-boundary enforcement).
    """
    __tablename__ = "retrieval_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent: Mapped[str] = mapped_column(String(255), index=True)
    vector_store: Mapped[str] = mapped_column(String(255), index=True)
    tenant: Mapped[str] = mapped_column(String(255), default="")
    doc_class: Mapped[str] = mapped_column(String(32), default="internal")
    allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class SoarRun(Base):
    """SOAR playbook execution with approval boundary.

    `pending_approval` until an operator approves; only then do the DB-safe actions
    (revoke sessions, raise incidents, record block indicators) run. Every step is audit-logged.
    """
    __tablename__ = "soar_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    playbook: Mapped[str] = mapped_column(String(64), index=True)
    target: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(32), default="pending_approval")
    actor: Mapped[str] = mapped_column(String(255), default="analyst")
    result: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class SecurityToolJob(Base):
    """Governed admin security-tool job contract. No browser command is stored/executed."""
    __tablename__ = "security_tool_jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    tool: Mapped[str] = mapped_column(String(128), index=True)
    target: Mapped[str] = mapped_column(String(512), default="")
    scope: Mapped[str] = mapped_column(Text, default="[]")
    approval_ticket: Mapped[str] = mapped_column(String(128), default="")
    environment: Mapped[str] = mapped_column(String(32), default="lab")
    purpose: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="pending_approval")
    contract_sha256: Mapped[str] = mapped_column(String(64), default="")
    actor: Mapped[str] = mapped_column(String(255), default="admin")
    params: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class SecurityEvidence(Base):
    """Normalized evidence returned by an isolated worker; preserves provenance/hash."""
    __tablename__ = "security_evidence"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    artifact_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    job_id: Mapped[str] = mapped_column(String(64), index=True)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    source: Mapped[str] = mapped_column(String(255), default="isolated-worker")
    collector: Mapped[str] = mapped_column(String(255), default="worker")
    collected_at: Mapped[str] = mapped_column(String(64), default="")
    classification: Mapped[str] = mapped_column(String(32), default="internal")
    result_type: Mapped[str] = mapped_column(String(64), default="normalized")
    summary: Mapped[str] = mapped_column(Text, default="")
    data: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class DiscoveredHost(Base):
    """Observed LAN/Wi-Fi neighbour (NOT an enrolled agent).

    Pushed by the endpoint agent (`--discover`) or `lab/collector.py` running on
    YOUR laptop, where the ARP table sees the real Wi-Fi neighbours (Docker
    containers cannot see host Wi-Fi). Upserted by MAC when known, else by IP.
    `vendor` is resolved server-side from the MAC OUI (`services/discovery.py`).
    Enrolled/managed machines live in `Device`; unknowns here are triaged first.
    """
    __tablename__ = "discovered_hosts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip_address: Mapped[str] = mapped_column(String(64), index=True)
    mac: Mapped[str] = mapped_column(String(64), default="", index=True)
    hostname: Mapped[str] = mapped_column(String(255), default="")
    vendor: Mapped[str] = mapped_column(String(128), default="Unknown")
    source: Mapped[str] = mapped_column(String(64), default="agent-discover")
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    trusted: Mapped[bool] = mapped_column(Boolean, default=False)

class AgentRuntimeEvent(Base):
    """Runtime telemetry/event envelope for internal agents, GenAI calls, MCP and A2A."""
    __tablename__ = "agent_runtime_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(128), index=True)
    agent_id: Mapped[str] = mapped_column(String(255), index=True)
    operation: Mapped[str] = mapped_column(String(64), index=True)
    provider: Mapped[str] = mapped_column(String(128), default="")
    model: Mapped[str] = mapped_column(String(255), default="")
    tool_name: Mapped[str] = mapped_column(String(255), default="")
    policy_decision: Mapped[str] = mapped_column(String(32), default="allow")
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    event_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AgentPolicy(Base):
    """Deterministic runtime policy for an internal agent; LLMs never author policy."""
    __tablename__ = "agent_policies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    allowed_tools: Mapped[str] = mapped_column(Text, default="[]")
    allowed_operations: Mapped[str] = mapped_column(Text, default='["chat","retrieval","plan"]')
    max_risk_score: Mapped[float] = mapped_column(Float, default=60)
    require_human_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class UnifiedSecurityEvent(Base):
    """Cross-plane normalized event used by the VEYRA Security Fabric."""
    __tablename__ = "unified_security_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    trace_id: Mapped[str] = mapped_column(String(128), index=True, default="")
    plane: Mapped[str] = mapped_column(String(64), index=True)
    event_type: Mapped[str] = mapped_column(String(128), index=True)
    actor: Mapped[str] = mapped_column(String(255), default="")
    source: Mapped[str] = mapped_column(String(255), default="")
    target: Mapped[str] = mapped_column(String(255), default="")
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    severity: Mapped[str] = mapped_column(String(32), default="INFO")
    payload: Mapped[str] = mapped_column(Text, default="{}")
    event_sha256: Mapped[str] = mapped_column(String(64), index=True, default="")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class InvestigationCase(Base):
    """AI-assisted investigation case. AI proposes reasoning; policy/approval remain authoritative."""
    __tablename__ = "investigation_cases"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    trigger_event_id: Mapped[str] = mapped_column(String(64), default="", index=True)
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="evidence_preserved")
    severity: Mapped[str] = mapped_column(String(32), default="MEDIUM")
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    target: Mapped[str] = mapped_column(String(255), default="")
    hypothesis: Mapped[str] = mapped_column(Text, default="")
    evidence_json: Mapped[str] = mapped_column(Text, default="[]")
    actions_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class InvestigationEvidence(Base):
    """Evidence reference attached to a case; content stays normalized/provenance-aware."""
    __tablename__ = "investigation_evidence"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evidence_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    case_id: Mapped[str] = mapped_column(String(64), index=True)
    source_type: Mapped[str] = mapped_column(String(64))
    source_ref: Mapped[str] = mapped_column(String(255), default="")
    sha256: Mapped[str] = mapped_column(String(64), default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    supports: Mapped[bool] = mapped_column(Boolean, default=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class InvestigationApproval(Base):
    """Human approval checkpoint before a consequential SOAR action."""
    __tablename__ = "investigation_approvals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(128))
    target: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(32), default="pending")
    actor: Mapped[str] = mapped_column(String(255), default="")
    reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class InvestigationStep(Base):
    """Deterministic state transition log for the autonomous SOC pipeline."""
    __tablename__ = "investigation_steps"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[str] = mapped_column(String(64), index=True)
    step: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="completed")
    summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class DetectionRule(Base):
    """Deterministic detection rule. LLMs may explain matches but never author enforcement."""
    __tablename__ = "detection_rules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(64), default="fabric")
    event_types: Mapped[str] = mapped_column(Text, default="[]")
    min_risk_score: Mapped[float] = mapped_column(Float, default=60)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    action: Mapped[str] = mapped_column(String(64), default="investigate")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ResponseAction(Base):
    """Governed response action request and verification state; no direct side effects in POC."""
    __tablename__ = "response_actions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    case_id: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(128))
    target: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(32), default="pending_approval")
    verification_status: Mapped[str] = mapped_column(String(32), default="not_started")
    approval_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evidence_sha256: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AttributionHypothesis(Base):
    """Evidence-backed attribution hypothesis; never an asserted actor identity."""
    __tablename__ = "attribution_hypotheses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hypothesis_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    case_id: Mapped[str] = mapped_column(String(64), index=True)
    label: Mapped[str] = mapped_column(String(128))
    confidence: Mapped[float] = mapped_column(Float, default=0)
    supporting_json: Mapped[str] = mapped_column(Text, default="[]")
    contradicting_json: Mapped[str] = mapped_column(Text, default="[]")
    assessment: Mapped[str] = mapped_column(String(64), default="hypothesis_only")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class IntelEnrichment(Base):
    """Immutable-ish summary of local TI/ATT&CK/ATLAS enrichment for a case."""
    __tablename__ = "intel_enrichments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    enrichment_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    case_id: Mapped[str] = mapped_column(String(64), index=True)
    framework: Mapped[str] = mapped_column(String(64))
    reference: Mapped[str] = mapped_column(String(128))
    summary: Mapped[str] = mapped_column(Text, default="")
    evidence_sha256: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class PentestAgentPlan(Base):
    """AI-generated, human-governed pentest plan. Stores plan/evidence metadata, not shell commands."""
    __tablename__ = "pentest_agent_plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    agent_id: Mapped[str] = mapped_column(String(255), index=True)
    objective: Mapped[str] = mapped_column(Text)
    target: Mapped[str] = mapped_column(String(255))
    scope_json: Mapped[str] = mapped_column(Text, default="[]")
    environment: Mapped[str] = mapped_column(String(32), default="lab")
    approval_ticket: Mapped[str] = mapped_column(String(128), default="")
    chain_json: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(64), default="awaiting_worker_approval")
    plan_sha256: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class UserAccount(Base):
    """Console login account. Exactly one account may have role='sudo'."""
    __tablename__ = "user_accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(32), default="viewer", index=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    mfa_required: Mapped[bool] = mapped_column(Boolean, default=True)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MfaChallenge(Base):
    """Short-lived OTP challenge for phone/email MFA. OTP hash, 5-min TTL, 3 attempts."""
    __tablename__ = "mfa_challenges"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    otp_hash: Mapped[str] = mapped_column(String(128))
    channel: Mapped[str] = mapped_column(String(16), default="phone")
    destination_masked: Mapped[str] = mapped_column(String(64), default="")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class UserToolPermission(Base):
    """Per-user tool entitlement: none, view, plan, or execute-request.

    Time-boxed grants carry `expires_at` (UTC); expired rows are treated as
    "none" by `services/auth.get_tool_level`. NULL expiry = no time limit
    (used for standing grants assigned at user creation).
    """
    __tablename__ = "user_tool_permissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    tool_id: Mapped[str] = mapped_column(String(255), index=True)
    level: Mapped[str] = mapped_column(String(32), default="none")
    granted_by: Mapped[str] = mapped_column(String(255), default="sudo")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class UserSession(Base):
    __tablename__ = "user_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ToolAccessRequest(Base):
    """Non-sudo request for tool rights. Sudo approves with a time-boxed grant
    (2h / 5h / 24h / custom hours) or denies. Expiry/cancellation is enforced
    server-side; every transition is audit-logged."""
    __tablename__ = "tool_access_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    username: Mapped[str] = mapped_column(String(255), default="", index=True)
    tool_id: Mapped[str] = mapped_column(String(255), index=True)
    tool_name: Mapped[str] = mapped_column(String(255), default="")
    level: Mapped[str] = mapped_column(String(32), default="plan")
    reason: Mapped[str] = mapped_column(Text, default="")
    duration_hours: Mapped[float] = mapped_column(Float, default=2.0)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    decided_by: Mapped[str] = mapped_column(String(255), default="")
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AdminNotification(Base):
    """In-app copy of every outbound admin email (approval requests, decisions).
    Guarantees the sudo inbox works even when no SMTP server is configured."""
    __tablename__ = "admin_notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    to_role: Mapped[str] = mapped_column(String(32), default="sudo", index=True)
    to_email: Mapped[str] = mapped_column(String(255), default="")
    subject: Mapped[str] = mapped_column(String(255), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    channel: Mapped[str] = mapped_column(String(32), default="log")
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    related_id: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class WifiNetwork(Base):
    """Observed nearby Wi-Fi network metadata from an enrolled local sensor."""
    __tablename__ = "wifi_networks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ssid: Mapped[str] = mapped_column(String(255), default="")
    bssid: Mapped[str] = mapped_column(String(64), default="", index=True)
    security: Mapped[str] = mapped_column(String(64), default="Unknown")
    channel: Mapped[str] = mapped_column(String(32), default="")
    band: Mapped[str] = mapped_column(String(32), default="")
    signal_dbm: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="local-sensor")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class WorkerNode(Base):
    """Managed security worker registered to an VEYRA tenant.

    A worker is the only place where third-party security binaries are installed or
    executed. The SaaS API exchanges signed job/install contracts with workers and
    never exposes arbitrary shell execution to customers.
    """
    __tablename__ = "worker_nodes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    worker_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    kind: Mapped[str] = mapped_column(String(64), default="kali")
    platform: Mapped[str] = mapped_column(String(128), default="kali-linux-amd64")
    status: Mapped[str] = mapped_column(String(32), default="pending")
    version: Mapped[str] = mapped_column(String(64), default="2.8.0")
    capabilities_json: Mapped[str] = mapped_column(Text, default="[]")
    last_heartbeat: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class WorkerToolInstall(Base):
    """Tool inventory reported by a managed worker.

    `state` is deliberately separate from the catalog status: a tool can be
    registered globally but absent, outdated, quarantined, or healthy on a worker.
    """
    __tablename__ = "worker_tool_installs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    worker_id: Mapped[str] = mapped_column(String(128), index=True)
    tool_id: Mapped[str] = mapped_column(String(255), index=True)
    version: Mapped[str] = mapped_column(String(128), default="unknown")
    state: Mapped[str] = mapped_column(String(32), default="requested")
    binary_path: Mapped[str] = mapped_column(String(512), default="")
    checksum: Mapped[str] = mapped_column(String(128), default="")
    sbom_ref: Mapped[str] = mapped_column(String(255), default="")
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class PostureSnapshot(Base):
    """Point-in-time posture snapshot for temporal drift and remediation proof."""
    __tablename__ = "posture_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    scope: Mapped[str] = mapped_column(String(128), default="tenant")
    posture_score: Mapped[float] = mapped_column(Float, default=0)
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    inventory_json: Mapped[str] = mapped_column(Text, default="{}")
    hash_sha256: Mapped[str] = mapped_column(String(64), index=True, default="")
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class PostureChange(Base):
    """Normalized before/after posture change with deterministic attribution."""
    __tablename__ = "posture_changes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    change_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    snapshot_before: Mapped[str] = mapped_column(String(64), default="")
    snapshot_after: Mapped[str] = mapped_column(String(64), default="")
    category: Mapped[str] = mapped_column(String(64), default="inventory")
    target: Mapped[str] = mapped_column(String(255), default="")
    change_type: Mapped[str] = mapped_column(String(64), default="changed")
    severity: Mapped[str] = mapped_column(String(32), default="INFO")
    summary: Mapped[str] = mapped_column(Text, default="")
    evidence_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class RogueAgentCase(Base):
    """Defensive rogue-agent investigation record.

    Stores hypotheses and evidence references only. It never executes containment
    itself; response remains approval-gated through the existing SOAR boundary.
    """
    __tablename__ = "rogue_agent_cases"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="investigating")
    confidence: Mapped[float] = mapped_column(Float, default=0)
    agent_identity: Mapped[str] = mapped_column(String(255), default="unknown")
    suspected_user: Mapped[str] = mapped_column(String(255), default="unknown")
    suspected_endpoint: Mapped[str] = mapped_column(String(255), default="unknown")
    suspected_provider: Mapped[str] = mapped_column(String(128), default="unknown")
    root_cause: Mapped[str] = mapped_column(Text, default="")
    first_seen: Mapped[str] = mapped_column(String(64), default="")
    last_seen: Mapped[str] = mapped_column(String(64), default="")
    evidence_json: Mapped[str] = mapped_column(Text, default="[]")
    timeline_json: Mapped[str] = mapped_column(Text, default="[]")
    recommended_actions_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ToolDefinition(Base):
    """Durable supply-chain identity for a catalog tool."""
    __tablename__ = "tool_definitions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tool_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    category: Mapped[str] = mapped_column(String(128), default="Security")
    purpose: Mapped[str] = mapped_column(Text, default="")
    upstream_source: Mapped[str] = mapped_column(String(128), default="approved-package-source")
    resolver_kind: Mapped[str] = mapped_column(String(64), default="package")
    maturity: Mapped[str] = mapped_column(String(32), default="stable")
    update_channel: Mapped[str] = mapped_column(String(32), default="stable")
    pin_mode: Mapped[str] = mapped_column(String(32), default="floating")
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class ToolRelease(Base):
    """Immutable release metadata; bytes are fetched only by managed workers/artifact infrastructure."""
    __tablename__ = "tool_releases"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    release_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    tool_id: Mapped[str] = mapped_column(String(255), index=True)
    version: Mapped[str] = mapped_column(String(128), default="")
    channel: Mapped[str] = mapped_column(String(32), default="candidate")
    artifact_uri: Mapped[str] = mapped_column(Text, default="")
    artifact_digest: Mapped[str] = mapped_column(String(160), default="")
    artifact_sha256: Mapped[str] = mapped_column(String(64), default="", index=True)
    signature: Mapped[str] = mapped_column(Text, default="")
    signature_required: Mapped[bool] = mapped_column(Boolean, default=True)
    provenance_uri: Mapped[str] = mapped_column(Text, default="")
    provenance_required: Mapped[bool] = mapped_column(Boolean, default=True)
    sbom_uri: Mapped[str] = mapped_column(Text, default="")
    sbom_required: Mapped[bool] = mapped_column(Boolean, default=True)
    license: Mapped[str] = mapped_column(String(128), default="unknown")
    source_commit: Mapped[str] = mapped_column(String(128), default="")
    verification_status: Mapped[str] = mapped_column(String(32), default="candidate", index=True)
    verification_errors: Mapped[str] = mapped_column(Text, default="[]")
    health_status: Mapped[str] = mapped_column(String(32), default="unknown", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ToolArtifact(Base):
    """Artifact Vault index. The production vault should be immutable object storage."""
    __tablename__ = "tool_artifacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    artifact_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    release_id: Mapped[str] = mapped_column(String(64), index=True)
    storage_uri: Mapped[str] = mapped_column(Text, default="")
    digest: Mapped[str] = mapped_column(String(160), default="")
    sha256: Mapped[str] = mapped_column(String(64), default="", index=True)
    signature_status: Mapped[str] = mapped_column(String(32), default="pending")
    provenance_status: Mapped[str] = mapped_column(String(32), default="pending")
    sbom_status: Mapped[str] = mapped_column(String(32), default="pending")
    immutable: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ToolUpdatePolicy(Base):
    __tablename__ = "tool_update_policies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    policy_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=lambda: "pol_"+uuid.uuid4().hex[:16])
    tool_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    channel: Mapped[str] = mapped_column(String(32), default="stable")
    pin_mode: Mapped[str] = mapped_column(String(32), default="floating")
    pinned_version: Mapped[str] = mapped_column(String(128), default="")
    pinned_digest: Mapped[str] = mapped_column(String(160), default="")
    auto_update: Mapped[bool] = mapped_column(Boolean, default=False)
    critical_override: Mapped[bool] = mapped_column(Boolean, default=True)
    require_canary: Mapped[bool] = mapped_column(Boolean, default=True)
    canary_percent: Mapped[int] = mapped_column(Integer, default=10)
    maintenance_window: Mapped[str] = mapped_column(String(128), default="weekly")
    freeze_reason: Mapped[str] = mapped_column(Text, default="")
    frozen_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class ToolDeployment(Base):
    __tablename__ = "tool_deployments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deployment_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    tool_id: Mapped[str] = mapped_column(String(255), index=True)
    release_id: Mapped[str] = mapped_column(String(64), index=True)
    worker_id: Mapped[str] = mapped_column(String(128), index=True)
    operation: Mapped[str] = mapped_column(String(32), default="install_or_update")
    target_version: Mapped[str] = mapped_column(String(128), default="")
    state: Mapped[str] = mapped_column(String(32), default="planned", index=True)
    force: Mapped[bool] = mapped_column(Boolean, default=False)
    manifest_json: Mapped[str] = mapped_column(Text, default="{}")
    manifest_sha256: Mapped[str] = mapped_column(String(64), default="", index=True)
    worker_receipt_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class ToolHealthCheck(Base):
    __tablename__ = "tool_health_checks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    check_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    release_id: Mapped[str] = mapped_column(String(64), index=True)
    worker_id: Mapped[str] = mapped_column(String(128), default="")
    status: Mapped[str] = mapped_column(String(32), default="pending")
    checks_json: Mapped[str] = mapped_column(Text, default="[]")
    evidence_sha256: Mapped[str] = mapped_column(String(64), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class SupplyChainAttestation(Base):
    __tablename__ = "supply_chain_attestations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attestation_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    release_id: Mapped[str] = mapped_column(String(64), index=True)
    kind: Mapped[str] = mapped_column(String(64), default="verification", index=True)
    predicate_type: Mapped[str] = mapped_column(Text, default="")
    subject_digest: Mapped[str] = mapped_column(String(160), default="")
    issuer: Mapped[str] = mapped_column(String(255), default="")
    evidence_sha256: Mapped[str] = mapped_column(String(64), default="", index=True)
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    verification_status: Mapped[str] = mapped_column(String(32), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ToolCanaryCohort(Base):
    __tablename__ = "tool_canary_cohorts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cohort_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    tool_id: Mapped[str] = mapped_column(String(255), index=True)
    release_id: Mapped[str] = mapped_column(String(64), index=True)
    worker_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    percent: Mapped[int] = mapped_column(Integer, default=10)
    state: Mapped[str] = mapped_column(String(32), default="planned")
    result_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class AISupplyChainAsset(Base):
    __tablename__ = "ai_supply_chain_assets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    asset_type: Mapped[str] = mapped_column(String(64), default="model", index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    version: Mapped[str] = mapped_column(String(128), default="")
    digest: Mapped[str] = mapped_column(String(160), default="")
    source_uri: Mapped[str] = mapped_column(Text, default="")
    provenance_uri: Mapped[str] = mapped_column(Text, default="")
    sbom_uri: Mapped[str] = mapped_column(Text, default="")
    policy_status: Mapped[str] = mapped_column(String(32), default="pending")
    trust_status: Mapped[str] = mapped_column(String(32), default="untrusted")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AgentCircuitBreaker(Base):
    __tablename__ = "agent_circuit_breakers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    breaker_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    agent_id: Mapped[str] = mapped_column(String(255), index=True)
    scope: Mapped[str] = mapped_column(String(64), default="agent")
    state: Mapped[str] = mapped_column(String(32), default="armed")
    reason: Mapped[str] = mapped_column(Text, default="")
    activated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class AgentContainmentPolicy(Base):
    """AI-swarm containment posture: egress, identity velocity and emergency stop controls."""
    __tablename__ = "agent_containment_policies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    policy_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), default="Default Agent Containment")
    egress_mode: Mapped[str] = mapped_column(String(32), default="deny_by_default")
    allowed_destinations_json: Mapped[str] = mapped_column(Text, default="[]")
    service_account_velocity_threshold: Mapped[int] = mapped_column(Integer, default=120)
    website_collaboration_detection: Mapped[bool] = mapped_column(Boolean, default=True)
    emergency_stop: Mapped[bool] = mapped_column(Boolean, default=False)
    require_human_approval_for_external_action: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class AIAssetTrustRecord(Base):
    __tablename__ = "ai_asset_trust_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    record_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=lambda: "ait_"+uuid.uuid4().hex[:16])
    asset_id: Mapped[str] = mapped_column(String(128), index=True)
    trust_score: Mapped[float] = mapped_column(Float, default=0)
    trust_status: Mapped[str] = mapped_column(String(32), default="untrusted")
    gates_json: Mapped[str] = mapped_column(Text, default="{}")
    missing_json: Mapped[str] = mapped_column(Text, default="[]")
    evidence_sha256: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AIBOMRecord(Base):
    __tablename__ = "ai_bom_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bom_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    root_asset_id: Mapped[str] = mapped_column(String(128), index=True)
    format: Mapped[str] = mapped_column(String(64), default="VEYRA-AIBOM-1.0")
    document_json: Mapped[str] = mapped_column(Text, default="{}")
    document_sha256: Mapped[str] = mapped_column(String(64), default="", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class TrustGraphNode(Base):
    __tablename__ = "trust_graph_nodes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    node_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    node_type: Mapped[str] = mapped_column(String(64), default="asset")
    label: Mapped[str] = mapped_column(String(255), default="")
    trust_status: Mapped[str] = mapped_column(String(32), default="untrusted")
    trust_score: Mapped[float] = mapped_column(Float, default=0)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class TrustGraphEdge(Base):
    __tablename__ = "trust_graph_edges"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    edge_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    source_id: Mapped[str] = mapped_column(String(128), index=True)
    target_id: Mapped[str] = mapped_column(String(128), index=True)
    relationship: Mapped[str] = mapped_column(String(64), default="depends_on")
    policy_status: Mapped[str] = mapped_column(String(32), default="pending")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AgentTrajectory(Base):
    __tablename__ = "agent_trajectories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trajectory_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    agent_id: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    score: Mapped[float] = mapped_column(Float, default=0)
    events_json: Mapped[str] = mapped_column(Text, default="[]")
    violations_json: Mapped[str] = mapped_column(Text, default="[]")
    evidence_sha256: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class TrustDecisionRecord(Base):
    __tablename__ = "trust_decision_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    decision_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    subject_id: Mapped[str] = mapped_column(String(255), index=True)
    decision: Mapped[str] = mapped_column(String(32), default="deny")
    reason: Mapped[str] = mapped_column(Text, default="")
    evidence_sha256: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class RuntimeAttestation(Base):
    __tablename__ = "runtime_attestations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attestation_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    subject_id: Mapped[str] = mapped_column(String(255), index=True)
    workload_identity: Mapped[str] = mapped_column(String(255), default="")
    artifact_digest: Mapped[str] = mapped_column(String(160), default="")
    policy_hash: Mapped[str] = mapped_column(String(64), default="")
    behavior_hash: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(32), default="pending")
    evidence_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class SignedMandate(Base):
    __tablename__ = "signed_mandates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mandate_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    principal: Mapped[str] = mapped_column(String(255), index=True)
    delegate: Mapped[str] = mapped_column(String(255), index=True)
    allowed_tools_json: Mapped[str] = mapped_column(Text, default="[]")
    constraints_json: Mapped[str] = mapped_column(Text, default="{}")
    signature: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="pending")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AgentIdentityAuthority(Base):
    __tablename__ = "agent_identity_authorities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    issuer: Mapped[str] = mapped_column(String(255), default="")
    owner: Mapped[str] = mapped_column(String(255), default="")
    credential_ref: Mapped[str] = mapped_column(String(512), default="")
    authority_json: Mapped[str] = mapped_column(Text, default="{}")
    delegation_chain_json: Mapped[str] = mapped_column(Text, default="[]")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    evidence_sha256: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AgentControlPolicy(Base):
    __tablename__ = "agent_control_policies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    policy_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    policy_json: Mapped[str] = mapped_column(Text, default="{}")
    policy_hash: Mapped[str] = mapped_column(String(64), default="")
    enforcement_mode: Mapped[str] = mapped_column(String(32), default="approval_required")
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AgentGatewayPolicy(Base):
    __tablename__ = "agent_gateway_policies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gateway_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    agent_id: Mapped[str] = mapped_column(String(255), index=True)
    allowed_tools_json: Mapped[str] = mapped_column(Text, default="[]")
    allowed_destinations_json: Mapped[str] = mapped_column(Text, default="[]")
    data_policy_json: Mapped[str] = mapped_column(Text, default="{}")
    rate_limit: Mapped[int] = mapped_column(Integer, default=60)
    transaction_limit: Mapped[float] = mapped_column(Float, default=0)
    require_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class MCPTrustFingerprint(Base):
    __tablename__ = "mcp_trust_fingerprints"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    server_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    version: Mapped[str] = mapped_column(String(128), default="")
    publisher: Mapped[str] = mapped_column(String(255), default="")
    fingerprint_sha256: Mapped[str] = mapped_column(String(64), default="")
    tools_hash: Mapped[str] = mapped_column(String(64), default="")
    permissions_hash: Mapped[str] = mapped_column(String(64), default="")
    endpoint_hash: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(32), default="trusted")
    drift_type: Mapped[str] = mapped_column(String(64), default="none")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AgentMemoryTrustRecord(Base):
    __tablename__ = "agent_memory_trust_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    memory_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    agent_id: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str] = mapped_column(String(255), default="")
    classification: Mapped[str] = mapped_column(String(64), default="internal")
    content_hash: Mapped[str] = mapped_column(String(64), default="")
    provenance: Mapped[str] = mapped_column(Text, default="")
    poisoning_score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AgentTransactionAssessment(Base):
    __tablename__ = "agent_transaction_assessments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    agent_id: Mapped[str] = mapped_column(String(255), index=True)
    target: Mapped[str] = mapped_column(String(512), default="")
    amount: Mapped[float] = mapped_column(Float, default=0)
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    decision: Mapped[str] = mapped_column(String(32), default="deny")
    reasons_json: Mapped[str] = mapped_column(Text, default="[]")
    evidence_sha256: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AgentBehaviorBaseline(Base):
    __tablename__ = "agent_behavior_baselines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    tools_json: Mapped[str] = mapped_column(Text, default="[]")
    destinations_json: Mapped[str] = mapped_column(Text, default="[]")
    delegation_depth: Mapped[int] = mapped_column(Integer, default=0)
    transaction_ceiling: Mapped[float] = mapped_column(Float, default=0)
    action_sequence_hash: Mapped[str] = mapped_column(String(64), default="")
    baseline_hash: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class DigitalTwinScenario(Base):
    __tablename__ = "digital_twin_scenarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    root_subject: Mapped[str] = mapped_column(String(255), index=True)
    nodes_json: Mapped[str] = mapped_column(Text, default="[]")
    edges_json: Mapped[str] = mapped_column(Text, default="[]")
    blast_radius: Mapped[int] = mapped_column(Integer, default=0)
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    containment_options_json: Mapped[str] = mapped_column(Text, default="[]")
    evidence_sha256: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ChecklistDefinition(Base):
    """Persisted mirror of a checklist registry entry — versioned, auditable.

    The registry (`checklist_registry.py`) remains the source of truth.
    This table materializes each entry so runs can FK to a stable definition
    and so drift between code and DB is detectable. Seed on startup.
    """
    __tablename__ = "checklist_definitions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    checklist_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    domain: Mapped[str] = mapped_column(String(64), index=True)
    category: Mapped[str] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(255))
    purpose: Mapped[str] = mapped_column(Text, default="")
    owner_role: Mapped[str] = mapped_column(String(32), default="analyst")
    cadence: Mapped[str] = mapped_column(String(32), default="daily")
    scope: Mapped[str] = mapped_column(String(255), default="")
    tier: Mapped[str] = mapped_column(String(32), default="recommended")
    evidence_json: Mapped[str] = mapped_column(Text, default="[]")
    remediation: Mapped[str] = mapped_column(Text, default="")
    status_chip_rule: Mapped[str] = mapped_column(Text, default="")
    boundary: Mapped[str] = mapped_column(Text, default="")
    version: Mapped[str] = mapped_column(String(32), default="1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class ChecklistRun(Base):
    """A single invocation of a checklist — governed, audit-logged.

    Status lifecycle: pending -> running -> completed | failed.
    P6-A runs are persisted as `completed` with stub evidence until real
    worker execution lands in P6-F. Every run FK's to ChecklistDefinition.
    """
    __tablename__ = "checklist_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    checklist_id: Mapped[str] = mapped_column(String(128), index=True)
    requested_by: Mapped[str] = mapped_column(String(255), default="console-user")
    parameters_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class ChecklistResult(Base):
    """Per-check evidence within a run.

    One row per logical check/evidence item. The worst `status` drives the
    status-chip colour (red > semi_red > yellow > amber > green).
    """
    __tablename__ = "checklist_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    result_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    run_id: Mapped[str] = mapped_column(String(64), index=True)
    checklist_id: Mapped[str] = mapped_column(String(128), index=True)
    check_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="pass", index=True)
    evidence_json: Mapped[str] = mapped_column(Text, default="{}")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ChecklistReceipt(Base):
    """Signed receipt for a completed run — integrity anchor.

    `payload_sha256` = SHA-256 of the canonical result payload.
    `signature` is HMAC with VEYRA_WORKER_SIGNING_SECRET when configured,
    otherwise the sha256 itself (still integrity-checked).
    """
    __tablename__ = "checklist_receipts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    run_id: Mapped[str] = mapped_column(String(64), index=True)
    checklist_id: Mapped[str] = mapped_column(String(128), index=True)
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    payload_sha256: Mapped[str] = mapped_column(String(64), index=True, default="")
    signature: Mapped[str] = mapped_column(String(128), default="")
    signer: Mapped[str] = mapped_column(String(255), default="veyra-control-plane")
    signed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


# ---------------------------------------------------------------------------
# P6-B — Live sensor telemetry
# ---------------------------------------------------------------------------
class LiveSensorEvent(Base):
    """Normalized event from any sensor (Wi-Fi, Ethernet, device join/drop).

    Every event has provenance + SHA-256 for audit. Token-gated ingest only.
    """
    __tablename__ = "live_sensor_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    sensor_type: Mapped[str] = mapped_column(String(32), index=True)
    sensor_id: Mapped[str] = mapped_column(String(128), default="unknown")
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[str] = mapped_column(String(32), default="INFO")
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    provenance: Mapped[str] = mapped_column(String(255), default="")
    event_sha256: Mapped[str] = mapped_column(String(64), index=True, default="")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)


class NetworkBaseline(Base):
    """Approved, versioned baseline for a scope (wifi_radio, switch_ports, etc).

    Only approved baselines are authoritative. Drift = current vs approved.
    """
    __tablename__ = "network_baselines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    baseline_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    scope: Mapped[str] = mapped_column(String(64), index=True)
    version: Mapped[str] = mapped_column(String(32), default="1.0")
    owner: Mapped[str] = mapped_column(String(255), default="security_operator")
    snapshot_json: Mapped[str] = mapped_column(Text, default="{}")
    snapshot_sha256: Mapped[str] = mapped_column(String(64), default="")
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DropEvent(Base):
    """Connection drop / link-down event with root-cause hypotheses."""
    __tablename__ = "drop_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    drop_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    link_id: Mapped[str] = mapped_column(String(255), index=True)
    link_type: Mapped[str] = mapped_column(String(32), default="wifi", index=True)
    drop_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    recovery_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    diagnosis_json: Mapped[str] = mapped_column(Text, default="{}")
    hypotheses_json: Mapped[str] = mapped_column(Text, default="[]")
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AIApplicationRun(Base):
    __tablename__ = "ai_application_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    application: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    request_json: Mapped[str] = mapped_column(Text, default="{}")
    result_json: Mapped[str] = mapped_column(Text, default="{}")
    evidence_sha256: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
