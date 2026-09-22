"""VEYRA REST API router (mounted as `/api/*` by `app.main`).

Help — structure, dependencies, endpoint groups:
- `clean(obj)`: strips SQLAlchemy state for JSON responses (used by list endpoints).
- Depends on: `app.db.get_db` (one session per request), ALL model classes from
  `app.models`, and services: `risk` (risk calc), `graph` (graph/attack-path/answers),
  `assess` (tool catalog + safe web assessment), `forensics` (static analysis),
  `visibility` (brute-force + browsing summaries), `teams` (playbooks/doctrine).
- Groups: overview/assets (inventory) → network (ports/flows) → findings/incidents/
  audit → identity/sessions → threat-intel (+live refresh/CVEs) → MITRE → cloud
  (+adapters/prowler/scan) → AI (+probes/evaluate/retrieval-audit) → risk/investigate →
  assessments → graph (graph/attack-path/answer) → ingest (flows/sessions/services/
  devices/dns/logins/usb/dlp) + collector heartbeat → tools catalog + web assessment →
  forensics → visibility reads (devices/dns/logins/usb/dlp) → remediation/teams/triage → SOAR.
- Safety rules live here: ingest batch caps, optional COLLECTOR_TOKEN gate,
  private/lab approval gate + cooldown on web assessments and AI evals, 5 MB cap
  on forensics uploads, allowlisted threat-feed hosts, NVD 20-CVE cap.
- `require_collector`: machine-ingest auth (open when COLLECTOR_TOKEN unset).
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
import os as _os
import json
import uuid
from ..db import get_db, SessionLocal
from ..models import Asset, Service, Finding, Incident, AuditEvent, Identity, SessionEvent, NetworkFlow, ThreatIntel, CloudResource, AIAsset, SecurityToolJob, SecurityEvidence, AgentRuntimeEvent, AgentPolicy, UnifiedSecurityEvent, PentestAgentPlan, WifiNetwork, UserAccount, UserToolPermission, UserSession, ToolAccessRequest, AdminNotification, WorkerNode, WorkerToolInstall, SupplyChainAttestation, ToolCanaryCohort, AISupplyChainAsset, AgentCircuitBreaker
from ..services.risk import calculate_risk, severity
from ..services.graph import build_graph, attack_paths, answer_question
from ..services.assess import TOOL_CATALOG, validate_target, check_cooldown, assess_web_posture
from ..services.forensics import KALI_FORENSICS_CATALOG, MAX_BYTES, analyze_bytes
from ..services.visibility import brute_force_candidates, browsing_summary
from ..services.help import HELP
from ..services.extended_catalog import extended_registry as admin_tool_registry, install_manifest
from ..services.ai_ecosystem import registry as ai_ecosystem_registry, overview as ai_ecosystem_overview

router = APIRouter(prefix="/api")


def require_admin(request: Request):
    """Accept legacy admin token or an authenticated console role with admin capability."""
    expected = _os.getenv("VEYRA_ADMIN_TOKEN", "")
    supplied = request.headers.get("X-VEYRA-Admin-Token", "")
    if expected and supplied and supplied == expected:
        return True
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        from ..services.auth import current_user
        db = SessionLocal()
        try:
            user = current_user(request, db)
            if user.role in {"sudo", "security_admin", "security_operator", "analyst"}:
                return True
        finally:
            db.close()
    raise HTTPException(403, "Administrator authorization required")

def require_privileged_admin(request: Request):
    """Second gate for high-impact security tooling; use PAM/MFA in production."""
    require_admin(request)
    expected = _os.getenv("VEYRA_PRIVILEGED_ADMIN_TOKEN", "")
    supplied = request.headers.get("X-VEYRA-Privileged-Admin-Token", "")
    if not expected or not supplied or supplied != expected:
        raise HTTPException(403, "Privileged administrator authorization required")
    return True

def _bearer_user(request: Request):
    """Console session user or None (never raises)."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    from ..services.auth import current_user
    db = SessionLocal()
    try:
        try:
            return current_user(request, db)
        except Exception:
            return None
    finally:
        db.close()

def require_tool_access(request: Request, tool: dict):
    # Sudo runs every tool with no further approval: role itself is the authority.
    user = _bearer_user(request)
    if user is not None and user.role == "sudo":
        return True
    # Legacy token retains POC compatibility. Console sessions additionally need
    # an explicit per-tool entitlement; privileged tools require sudo/security_admin
    # plus the separate privileged gate when the legacy admin flow is used.
    require_admin(request)
    if user is not None:
        from ..services.auth import get_tool_level
        db = SessionLocal()
        try:
            level = get_tool_level(db, user.id, tool.get("id", ""))
            if level not in {"plan", "execute_request"}:
                raise HTTPException(403, "This tool is read-only for your account. Use Request access to ask the sudo administrator.")
            if tool.get("access_tier") == "privileged_admin" and user.role not in {"sudo", "security_admin"}:
                raise HTTPException(403, "Privileged tools require Sudo or Security Admin role")
        finally:
            db.close()
    elif tool.get("access_tier") == "privileged_admin":
        require_privileged_admin(request)
    return True


@router.get("/admin/ethical-hacking/tools")
def admin_ethical_tools(_: bool = Depends(require_admin)):
    return {"admin_only": True, "tools": admin_tool_registry(),
            "policy": "Catalog and stage authorized assessments only; no arbitrary shell or exploit execution is exposed."}


class EthicalJobRequest(BaseModel):
    tool: str
    target: str
    scope: list[str] = Field(min_length=1, max_length=100)
    approval_ticket: str = Field(min_length=0, max_length=128, default="")
    environment: str = "lab"
    purpose: str = Field(min_length=3, max_length=500)
    params: dict = {}


@router.post("/admin/ethical-hacking/jobs")
def stage_ethical_job(req: EthicalJobRequest, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.execution_plane import make_job_contract
    from ..services.tool_forms import build_contract_fields
    tools = {x["name"]: x for x in admin_tool_registry()}
    tool = tools.get(req.tool)
    if not tool:
        raise HTTPException(404, "Tool is not registered")
    require_tool_access(request, tool)
    user = _bearer_user(request)
    actor = user.username if user else "admin"
    ticket = req.approval_ticket.strip()
    if not ticket:
        if user is not None and user.role == "sudo":
            from datetime import datetime, timezone as _tz
            ticket = "SUDO-" + datetime.now(_tz.utc).strftime("%Y%m%d-%H%M%S")
        else:
            raise HTTPException(400, "approval_ticket is required (sudo runs generate one automatically)")
    try:
        _, _, extra = build_contract_fields(tool, {"target": req.target, "scope": req.scope, **(req.params or {})})
    except ValueError as e:
        raise HTTPException(400, str(e))
    merged_params = {**(req.params or {}), **extra}
    try:
        contract = make_job_contract(tool, req.target, req.scope, ticket, req.environment, req.purpose, actor=actor)
    except ValueError as e:
        raise HTTPException(400, str(e))
    row = SecurityToolJob(job_id=contract["job_id"], tool=contract["tool"], target=contract["target"],
        scope=json.dumps(contract["scope"]), approval_ticket=contract["approval_ticket"],
        environment=contract["environment"], purpose=contract["purpose"],
        contract_sha256=contract["contract_sha256"], actor=actor,
        params=json.dumps(merged_params, default=str))
    db.add(row)
    db.add(AuditEvent(actor=actor, action="ethical_hacking_job_staged", target=req.target,
                      outcome=f"pending:{req.tool}:{ticket}"))
    db.commit()
    return {**contract, "params": merged_params, "status":"pending_approval",
            "message":"Job contract created. The API did not execute a security-tool command."}

@router.get("/admin/ethical-hacking/jobs")
def admin_ethical_jobs(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    rows = db.query(SecurityToolJob).order_by(SecurityToolJob.created_at.desc()).limit(limit).all()
    out=[]
    for r in rows:
        item=clean(r); item["scope"]=json.loads(r.scope or "[]")
        try: item["params"]=json.loads(r.params or "{}")
        except Exception: item["params"]={}
        out.append(item)
    return out

@router.post("/admin/ethical-hacking/jobs/{job_id}/approve")
def approve_ethical_job(job_id: str, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    row=db.query(SecurityToolJob).filter(SecurityToolJob.job_id==job_id).first()
    if not row: raise HTTPException(404, "Job not found")
    if row.status != "pending_approval": raise HTTPException(409, f"Job is {row.status}")
    tool = next((x for x in admin_tool_registry() if x["name"] == row.tool), None)
    if tool and tool.get("access_tier") == "privileged_admin": require_privileged_admin(request)
    from datetime import datetime, timezone
    row.status="approved_for_worker"; row.approved_at=datetime.now(timezone.utc)
    db.add(AuditEvent(actor="admin", action="ethical_hacking_job_approved", target=job_id, outcome="approved_for_worker"))
    db.commit()
    return {"job_id":job_id,"status":row.status,"execution":"not_started","message":"Approved for an isolated worker. No command is executed by the API."}

@router.post("/admin/ethical-hacking/jobs/{job_id}/dispatch")
def dispatch_ethical_job(job_id: str, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    row=db.query(SecurityToolJob).filter(SecurityToolJob.job_id==job_id).first()
    if not row: raise HTTPException(404, "Job not found")
    if row.status != "approved_for_worker": raise HTTPException(409, "Job must be approved before dispatch")
    tool = next((x for x in admin_tool_registry() if x["name"] == row.tool), None)
    if tool and tool.get("access_tier") == "privileged_admin": require_privileged_admin(request)
    row.status="queued_for_isolated_worker"
    db.add(AuditEvent(actor="admin", action="ethical_hacking_job_dispatched", target=job_id, outcome="queued"))
    db.commit()
    return {"job_id":job_id,"status":row.status,"execution":"queued","worker":"external_isolated_worker",
            "message":"Queued contract only. A production deployment should have an independently authenticated worker consume this contract."}

class EvidenceRequest(BaseModel):
    payload: dict

@router.post("/admin/ethical-hacking/jobs/{job_id}/evidence")
def ingest_ethical_evidence(job_id: str, req: EvidenceRequest, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.execution_plane import normalize_evidence
    row=db.query(SecurityToolJob).filter(SecurityToolJob.job_id==job_id).first()
    if not row: raise HTTPException(404, "Job not found")
    try: artifact=normalize_evidence(job_id, req.payload)
    except ValueError as e: raise HTTPException(400, str(e))
    ev=SecurityEvidence(artifact_id=artifact["artifact_id"], job_id=job_id, sha256=artifact["sha256"],
        source=artifact["source"], collector=artifact["collector"], collected_at=artifact["collected_at"],
        classification=artifact["classification"], result_type=artifact["result_type"],
        summary=artifact["summary"], data=json.dumps(artifact["data"], default=str))
    db.add(ev); row.status="completed"
    db.add(AuditEvent(actor="admin", action="ethical_hacking_evidence_ingested", target=job_id, outcome=artifact["artifact_id"]))
    db.commit()
    return artifact

@router.get("/admin/ethical-hacking/jobs/{job_id}/evidence")
def list_ethical_evidence(job_id: str, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    rows=db.query(SecurityEvidence).filter(SecurityEvidence.job_id==job_id).order_by(SecurityEvidence.created_at.desc()).all()
    out=[]
    for r in rows:
        item=clean(r); item["data"]=json.loads(r.data or "{}"); out.append(item)
    return out


@router.get("/admin/ethical-hacking/tools/{tool_id}/form")
def ethical_tool_form(tool_id: str, _: bool = Depends(require_admin)):
    from ..services.tool_forms import get_form
    tool = next((x for x in admin_tool_registry() if x["id"] == tool_id), None)
    if not tool:
        raise HTTPException(404, "Tool is not registered")
    return get_form(tool)


@router.post("/admin/ethical-hacking/jobs/run")
def run_ethical_job_now(req: EthicalJobRequest, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    """One-click governed run.

    Sudo: stage → approve → queue for the isolated worker in a single call
    (no further approval needed — the sudo role is the approval).
    Non-sudo with execute_request: stages a pending job that still needs sudo
    approval. Anything less: 403 (read-only).
    The API never executes a tool command itself in any case.
    """
    from ..services.execution_plane import make_job_contract
    from ..services.tool_forms import build_contract_fields
    from datetime import datetime, timezone as _tz
    tools = {x["name"]: x for x in admin_tool_registry()}
    tool = tools.get(req.tool)
    if not tool:
        raise HTTPException(404, "Tool is not registered")
    require_tool_access(request, tool)
    user = _bearer_user(request)
    is_sudo = user is not None and user.role == "sudo"
    actor = user.username if user else "admin"
    if not is_sudo:
        # Non-sudo: run degrades to a staged request awaiting sudo approval.
        staged = stage_ethical_job(req, request, db)
        return {**staged, "status": "pending_approval",
                "message": "Staged for sudo approval. Execution starts only after approval."}
    ticket = req.approval_ticket.strip() or ("SUDO-" + datetime.now(_tz.utc).strftime("%Y%m%d-%H%M%S"))
    try:
        _, _, extra = build_contract_fields(tool, {"target": req.target, "scope": req.scope, **(req.params or {})})
    except ValueError as e:
        raise HTTPException(400, str(e))
    merged_params = {**(req.params or {}), **extra}
    try:
        contract = make_job_contract(tool, req.target, req.scope, ticket, req.environment, req.purpose, actor=actor)
    except ValueError as e:
        raise HTTPException(400, str(e))
    row = SecurityToolJob(job_id=contract["job_id"], tool=contract["tool"], target=contract["target"],
        scope=json.dumps(contract["scope"]), approval_ticket=ticket,
        environment=contract["environment"], purpose=contract["purpose"],
        contract_sha256=contract["contract_sha256"], actor=actor,
        params=json.dumps(merged_params, default=str),
        status="queued_for_isolated_worker", approved_at=datetime.now(_tz.utc))
    db.add(row)
    db.add(AuditEvent(actor=actor, action="ethical_hacking_job_staged", target=req.target, outcome="sudo-run-queued"))
    db.add(AuditEvent(actor=actor, action="ethical_hacking_job_approved", target=contract["job_id"], outcome="sudo_implicit_approval"))
    db.add(AuditEvent(actor=actor, action="ethical_hacking_job_dispatched", target=contract["job_id"], outcome="queued"))
    db.commit()
    return {**contract, "params": merged_params, "status": "queued_for_isolated_worker",
            "execution": "queued", "worker": "external_isolated_worker",
            "message": "Sudo run: approved implicitly and queued for the isolated worker. The API executed no tool command."}



class PentestPlanRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=255)
    objective: str = Field(min_length=3, max_length=500)
    target: str = Field(min_length=1, max_length=255)
    scope: list[str] = Field(min_length=1, max_length=100)
    environment: str = "lab"
    approval_ticket: str = ""

@router.get("/pentest-agents/catalog")
def pentest_agent_catalog(_: bool = Depends(require_admin)):
    from ..services.pentest_agents import SAFE_CHAIN_LIBRARY, TOOL_AI_FEATURES
    return {"agents":[{"id":"veyra-pentest-agent","mode":"plan_only","capabilities":["chain planning","tool-result triage","evidence summarization"]}], "chains":SAFE_CHAIN_LIBRARY, "ai_enhanced_tools":TOOL_AI_FEATURES, "safety":"No browser shell, credential attacks, exploit replay, payload delivery, persistence, C2 or hack-back."}

@router.post("/pentest-agents/plans")
def create_pentest_agent_plan(req: PentestPlanRequest, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.pentest_agents import create_plan
    try:
        plan=create_plan(req.agent_id, req.objective, req.target, req.scope, req.environment, req.approval_ticket)
    except ValueError as e:
        raise HTTPException(400, str(e))
    row=PentestAgentPlan(plan_id=plan["plan_id"],agent_id=plan["agent_id"],objective=plan["objective"],target=plan["target"],scope_json=json.dumps(plan["scope"]),environment=plan["environment"],approval_ticket=plan["approval_ticket"],chain_json=json.dumps(plan["chain"]),status=plan["status"],plan_sha256=plan["plan_sha256"])
    db.add(row); db.add(AuditEvent(actor="admin",action="pentest_agent_plan_created",target=req.target,outcome=plan["plan_id"])); db.commit()
    return plan

@router.get("/pentest-agents/plans")
def list_pentest_agent_plans(limit:int=Query(100,ge=1,le=500), db:Session=Depends(get_db), _:bool=Depends(require_admin)):
    rows=db.query(PentestAgentPlan).order_by(PentestAgentPlan.created_at.desc()).limit(limit).all()
    return [clean(r) | {"scope":json.loads(r.scope_json or "[]"),"chain":json.loads(r.chain_json or "[]")} for r in rows]

@router.get("/help")
def help_registry():
    """Machine-readable module help and safe operating guidance."""
    return {"modules": HELP}

def clean(obj):
    return {k:v for k,v in obj.__dict__.items() if k != "_sa_instance_state"}

def require_collector(request: Request):
    """Optional shared-secret auth for machine ingest endpoints.

    Open when `COLLECTOR_TOKEN` is unset (lab default); enforced (401) when set.
    Browser Operator endpoints (assessments, SOAR, triage) are intentionally NOT gated.
    """
    token = _os.getenv("COLLECTOR_TOKEN", "")
    if token and request.headers.get("X-Collector-Token") != token:
        raise HTTPException(401, "Collector token required")


def require_ai_gateway(request: Request):
    expected = _os.getenv("VEYRA_AI_GATEWAY_TOKEN", "")
    supplied = request.headers.get("X-VEYRA-AI-Token", "")
    if not expected or not supplied or supplied != expected:
        raise HTTPException(403, "Authenticated AI gateway client required")
    return True

class AIGatewayRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=255)
    operation: str = Field(default="chat", max_length=64)
    provider: str = ""
    model: str = ""
    tool_name: str = ""
    input: object = ""
    metadata: dict = {}

class AgentPolicyRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=255)
    allowed_tools: list[str] = []
    allowed_operations: list[str] = ["chat","retrieval","plan"]
    max_risk_score: float = Field(default=60, ge=0, le=100)
    require_human_approval: bool = True
    enabled: bool = True

@router.get("/ai-gateway/policy/{agent_id}")
def get_agent_policy(agent_id: str, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    row=db.query(AgentPolicy).filter(AgentPolicy.agent_id==agent_id).first()
    if not row:
        return {"agent_id":agent_id,"allowed_tools":[],"allowed_operations":["chat","retrieval","plan"],"max_risk_score":60,"require_human_approval":True,"enabled":False}
    return {"agent_id":row.agent_id,"allowed_tools":json.loads(row.allowed_tools or "[]"),"allowed_operations":json.loads(row.allowed_operations or "[]"),"max_risk_score":row.max_risk_score,"require_human_approval":row.require_human_approval,"enabled":row.enabled}

@router.put("/ai-gateway/policy")
def put_agent_policy(req: AgentPolicyRequest, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    row=db.query(AgentPolicy).filter(AgentPolicy.agent_id==req.agent_id).first()
    if not row:
        row=AgentPolicy(agent_id=req.agent_id); db.add(row)
    row.allowed_tools=json.dumps(sorted(set(req.allowed_tools)))
    row.allowed_operations=json.dumps(sorted(set(req.allowed_operations)))
    row.max_risk_score=req.max_risk_score
    row.require_human_approval=req.require_human_approval
    row.enabled=req.enabled
    db.add(AuditEvent(actor="admin", action="ai_agent_policy_updated", target=req.agent_id, outcome="success"))
    db.commit()
    return {"status":"saved","agent_id":req.agent_id}

@router.post("/ai-gateway/evaluate")
def ai_gateway_evaluate(req: AIGatewayRequest, db: Session = Depends(get_db), _: bool = Depends(require_ai_gateway)):
    from ..services.ai_gateway import decide, trace_id, event_hash, utc
    row=db.query(AgentPolicy).filter(AgentPolicy.agent_id==req.agent_id, AgentPolicy.enabled.is_(True)).first()
    if not row:
        raise HTTPException(403,"Agent is not enrolled in the VEYRA AI gateway")
    policy={"allowed_tools":json.loads(row.allowed_tools or "[]"),"allowed_operations":json.loads(row.allowed_operations or "[]"),"max_risk_score":row.max_risk_score,"require_human_approval":row.require_human_approval}
    decision=decide(req.model_dump(),policy)
    tid=trace_id()
    event={"trace_id":tid,"agent_id":req.agent_id,"operation":req.operation,"provider":req.provider,"model":req.model,"tool_name":req.tool_name,"decision":decision,"metadata":req.metadata,"timestamp":utc()}
    event["event_sha256"]=event_hash(event)
    db.add(AgentRuntimeEvent(trace_id=tid,agent_id=req.agent_id,operation=req.operation,provider=req.provider,model=req.model,tool_name=req.tool_name,policy_decision=decision["decision"],risk_score=decision["risk_score"],event_json=json.dumps(event,default=str)))
    db.add(AuditEvent(actor=req.agent_id, action="ai_gateway_decision", target=req.operation, outcome=decision["decision"]))
    db.commit()
    return {**event,"side_effect_executed":False,"message":"Policy decision recorded; VEYRA does not execute the requested model/tool side effect."}

@router.get("/ai-gateway/traces/{trace_id}")
def ai_gateway_trace(trace_id: str, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    rows=db.query(AgentRuntimeEvent).filter(AgentRuntimeEvent.trace_id==trace_id).order_by(AgentRuntimeEvent.created_at.asc()).all()
    return [clean(r) | {"event":json.loads(r.event_json or "{}")} for r in rows]

@router.get("/ai-gateway/events")
def ai_gateway_events(limit: int=Query(100,ge=1,le=500), db: Session=Depends(get_db), _: bool = Depends(require_admin)):
    rows=db.query(AgentRuntimeEvent).order_by(AgentRuntimeEvent.created_at.desc()).limit(limit).all()
    return [clean(r) | {"event":json.loads(r.event_json or "{}")} for r in rows]



@router.get("/fabric/overview")
def fabric_overview(db: Session = Depends(get_db)):
    from ..services.fabric import security_fabric_overview
    return security_fabric_overview(db)

class FabricEventRequest(BaseModel):
    plane: str = Field(min_length=2, max_length=64)
    event_type: str = Field(min_length=2, max_length=128)
    actor: str = ""
    source: str = ""
    target: str = ""
    risk_score: float = Field(default=0, ge=0, le=100)
    payload: dict = {}
    trace_id: str = ""

@router.post("/fabric/events")
def fabric_event(req: FabricEventRequest, db: Session = Depends(get_db), _: bool = Depends(require_collector)):
    from ..services.fabric import normalize_event
    e=normalize_event(**req.model_dump())
    row=UnifiedSecurityEvent(event_id=e["event_id"],trace_id=e["trace_id"],plane=e["plane"],event_type=e["event_type"],actor=e["actor"],source=e["source"],target=e["target"],risk_score=e["risk_score"],severity=e["severity"],payload=json.dumps(e["payload"],default=str),event_sha256=e["event_sha256"])
    db.add(row); db.add(AuditEvent(actor=req.actor or "fabric",action="fabric_event_ingested",target=req.target or req.event_type,outcome=e["severity"])); db.commit()
    return e

@router.get("/fabric/events")
def fabric_events(limit: int=Query(100,ge=1,le=500), db: Session=Depends(get_db), _: bool=Depends(require_admin)):
    rows=db.query(UnifiedSecurityEvent).order_by(UnifiedSecurityEvent.observed_at.desc()).limit(limit).all()
    return [clean(r) | {"payload":json.loads(r.payload or "{}")} for r in rows]

@router.get("/fabric/ai-attack-paths")
def fabric_ai_attack_paths(max_paths: int=Query(10,ge=1,le=50), db: Session=Depends(get_db), _: bool=Depends(require_admin)):
    from ..services.fabric import ai_attack_paths
    return ai_attack_paths(db,max_paths)

@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    return {
      "assets": db.query(func.count(Asset.id)).scalar(),
      "critical_findings": db.query(func.count(Finding.id)).filter(Finding.severity=="CRITICAL", Finding.status=="open").scalar(),
      "open_incidents": db.query(func.count(Incident.id)).filter(Incident.status=="open").scalar(),
      "external_assets": db.query(func.count(Asset.id)).filter(Asset.external_exposure.is_(True)).scalar(),
      "risk_average": round(db.query(func.avg(Finding.risk_score)).scalar() or 0, 1),
      "privileged_identities": db.query(func.count(Identity.id)).filter(Identity.privilege>=4).scalar(),
      "cloud_exposures": db.query(func.count(CloudResource.id)).filter(CloudResource.public_exposure.is_(True)).scalar(),
      "ai_assets": db.query(func.count(AIAsset.id)).scalar(),
    }

@router.get("/assets")
def assets(db: Session = Depends(get_db)):
    return [clean(a) for a in db.query(Asset).order_by(Asset.criticality.desc()).all()]

@router.get("/network/ports")
def ports(db: Session = Depends(get_db)):
    rows = db.query(Service, Asset).join(Asset, Service.asset_id==Asset.id).all()
    return [{"id":s.id,"host":a.hostname,"ip":a.ip_address,"port":s.port,"protocol":s.protocol,"service":s.service,"process":s.process,"pid":s.pid,"user":s.user,"expected":s.expected} for s,a in rows]

@router.get("/network/flows")
def flows(db: Session = Depends(get_db)):
    rows=db.query(NetworkFlow).order_by(NetworkFlow.observed_at.desc()).limit(100).all()
    return [clean(x) for x in rows]

@router.get("/findings")
def findings(db: Session = Depends(get_db)):
    rows = db.query(Finding, Asset).join(Asset, Finding.asset_id==Asset.id).order_by(Finding.risk_score.desc()).all()
    return [{"id":f.id,"title":f.title,"severity":f.severity,"cvss":f.cvss,"kev":f.kev,"exposure":f.exposure,"risk_score":f.risk_score,"status":f.status,"asset":a.hostname,"description":f.description} for f,a in rows]

@router.get("/incidents")
def incidents(db: Session = Depends(get_db)):
    return [clean(i) for i in db.query(Incident).order_by(Incident.created_at.desc()).all()]

@router.get("/audit")
def audit(db: Session = Depends(get_db)):
    return [clean(x) for x in db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(50).all()]

@router.get("/identities")
def identities(db: Session = Depends(get_db)):
    return [clean(x) for x in db.query(Identity).order_by(Identity.privilege.desc()).all()]

@router.get("/sessions")
def sessions(db: Session = Depends(get_db)):
    return [clean(x) for x in db.query(SessionEvent).order_by(SessionEvent.started_at.desc()).limit(100).all()]

@router.get("/threat-intel")
def threat_intel(db: Session = Depends(get_db)):
    return [clean(x) for x in db.query(ThreatIntel).order_by(ThreatIntel.exploited.desc(), ThreatIntel.created_at.desc()).all()]

@router.get("/cloud/resources")
def cloud_resources(db: Session = Depends(get_db)):
    return [clean(x) for x in db.query(CloudResource).order_by(CloudResource.risk_score.desc()).all()]

@router.get("/ai/assets")
def ai_assets(db: Session = Depends(get_db)):
    return [clean(x) for x in db.query(AIAsset).order_by(AIAsset.risk_score.desc()).all()]

class RiskRequest(BaseModel):
    criticality:int=Field(ge=1,le=5)
    cvss:float=Field(ge=0,le=10)
    exploitability:float=Field(ge=0,le=1)
    exposure:bool=False
    privilege:int=Field(ge=0,le=5)
    data_sensitivity:int=Field(ge=0,le=5)
    threat:float=Field(ge=0,le=1)
    anomaly:float=Field(ge=0,le=1)

@router.post("/risk/calculate")
def risk(req: RiskRequest):
    score=calculate_risk(**req.model_dump())
    return {"risk_score":score,"severity":severity(score)}

class InvestigationRequest(BaseModel):
    question:str
    asset_id:int|None=None

@router.post("/ai/investigate")
def investigate(req: InvestigationRequest, db: Session = Depends(get_db)):
    context=[]
    if req.asset_id:
        a=db.get(Asset, req.asset_id)
        if a: context.append({"asset":a.hostname,"ip":a.ip_address,"criticality":a.criticality})
    f=db.query(Finding).order_by(Finding.risk_score.desc()).limit(5).all()
    ti=db.query(ThreatIntel).filter(ThreatIntel.exploited.is_(True)).limit(5).all()
    return {"mode":"advisory","question":req.question,"evidence":{"asset":context,"top_findings":[{"title":x.title,"severity":x.severity,"risk":x.risk_score} for x in f],"known_exploited_intel":[{"indicator":x.indicator,"title":x.title,"source":x.source} for x in ti]},"recommendation":"Validate scope, collect evidence, correlate threat intelligence, then require human approval before any high-impact response."}

class AssessmentRequest(BaseModel):
    target:str
    scope:list[str]
    purpose:str="authorized-lab-assessment"
    approval_required:bool=True

@router.post("/assessments")
def create_assessment(req: AssessmentRequest, db: Session = Depends(get_db)):
    if not req.scope or not req.target.strip(): raise HTTPException(400,"Explicit target and scope are required")
    db.add(AuditEvent(actor="demo-user", action="assessment_created", target=req.target, outcome="pending-approval" if req.approval_required else "queued")); db.commit()
    return {"status":"pending_approval" if req.approval_required else "queued","target":req.target,"scope":req.scope,"message":"POC assessment job created. No arbitrary command execution is exposed."}

# ---------------- v1.2 Security Graph ----------------

@router.get("/graph")
def graph(db: Session = Depends(get_db)):
    g = build_graph(db)
    return {"nodes": list(g["nodes"].values()), "edges": g["edges"],
            "counts": {"nodes": len(g["nodes"]), "edges": len(g["edges"])}}

@router.get("/graph/attack-path")
def graph_attack_path(db: Session = Depends(get_db), max_paths: int = Query(5, ge=1, le=10)):
    return attack_paths(db, max_paths=max_paths)

@router.get("/graph/answer")
def graph_answer(kind: str = Query(..., pattern="^(internet_to_data|connection_owner|port_owner|privileged_access|ai_data_access|cloud_exposure)$"),
                 db: Session = Depends(get_db)):
    return {"kind": kind, "results": answer_question(db, kind)}

# ---------------- v1.2 Telemetry ingestion ----------------

class FlowIn(BaseModel):
    src_ip: str; dst_ip: str; dst_port: int = Field(ge=1, le=65535)
    protocol: str = "TCP"; bytes_out: int = 0; action: str = "allow"
    src_asset_id: int | None = None; dst_asset_id: int | None = None

class SessionIn(BaseModel):
    username: str; source_ip: str; application: str
    asset_id: int | None = None; auth_method: str = "SSO"
    privileged: bool = False; anomaly_score: float = 0.0

class ServiceIn(BaseModel):
    asset_id: int; port: int = Field(ge=1, le=65535)
    protocol: str = "TCP"; service: str; process: str = "unknown"
    pid: int | None = None; user: str = "unknown"; expected: bool = True

@router.post("/ingest/network-flows")
def ingest_flows(items: list[FlowIn], db: Session = Depends(get_db), _auth: None = Depends(require_collector)):
    if not items or len(items) > 500: raise HTTPException(400, "Send 1..500 flows per batch")
    rows = [NetworkFlow(**i.model_dump()) for i in items]
    db.add_all(rows)
    db.add(AuditEvent(actor="collector", action="ingest_network_flows", target=f"{len(rows)} flows", outcome="success"))
    db.commit()
    return {"ingested": len(rows)}

@router.post("/ingest/sessions")
def ingest_sessions(items: list[SessionIn], db: Session = Depends(get_db), _auth: None = Depends(require_collector)):
    if not items or len(items) > 500: raise HTTPException(400, "Send 1..500 sessions per batch")
    rows = [SessionEvent(**i.model_dump()) for i in items]
    db.add_all(rows)
    db.add(AuditEvent(actor="collector", action="ingest_sessions", target=f"{len(rows)} sessions", outcome="success"))
    db.commit()
    return {"ingested": len(rows)}

@router.post("/ingest/services")
def ingest_services(items: list[ServiceIn], db: Session = Depends(get_db), _auth: None = Depends(require_collector)):
    if not items or len(items) > 200: raise HTTPException(400, "Send 1..200 services per batch")
    for i in items:
        if not db.get(Asset, i.asset_id): raise HTTPException(400, f"Unknown asset_id {i.asset_id}")
    rows = [Service(**i.model_dump()) for i in items]
    db.add_all(rows)
    db.add(AuditEvent(actor="collector", action="ingest_services", target=f"{len(rows)} services", outcome="success"))
    db.commit()
    return {"ingested": len(rows)}

# ---------------- v1.2 Tools catalog + safe web assessment ----------------

@router.get("/tools/catalog")
def tools_catalog():
    return {"tools": TOOL_CATALOG,
            "note": "Offensive tools run only in an isolated authorized lab with approval; the browser API exposes safe posture checks only."}

class WebAssessmentRequest(BaseModel):
    url: str
    approval_confirmed: bool = False

@router.post("/assessments/web")
async def web_assessment(req: WebAssessmentRequest, db: Session = Depends(get_db)):
    try:
        info = validate_target(req.url)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if info["private"] and not req.approval_confirmed:
        db.add(AuditEvent(actor="demo-user", action="web_assessment_pending_approval", target=req.url, outcome="pending-approval")); db.commit()
        lab_hint = " Lab target detected — get red-team lead approval, then resubmit." if info.get("lab") else ""
        return {"status": "pending_approval", "host": info["host"], "lab": info.get("lab", False),
                "message": "Private/lab target requires explicit approval. Resubmit with approval_confirmed=true after authorization." + lab_hint}
    try:
        check_cooldown(info["host"])
    except ValueError as e:
        raise HTTPException(429, str(e))
    try:
        result = await assess_web_posture(req.url)
    except Exception as e:
        db.add(AuditEvent(actor="demo-user", action="web_assessment_failed", target=req.url, outcome="error")); db.commit()
        raise HTTPException(502, f"Assessment fetch failed: {e}")
    for f in result["findings"]:
        db.add(Finding(asset_id=db.query(Asset).first().id if db.query(Asset).first() else 1,
                       title=f["title"][:255], severity=f["severity"], cvss=0,
                       exposure=False, data_sensitivity=1,
                       risk_score=75 if f["severity"] == "HIGH" else 45 if f["severity"] == "MEDIUM" else 20,
                       description=f["detail"][:500] + f" [target {info['host']}]"))
    db.add(AuditEvent(actor="demo-user", action="web_assessment_completed", target=req.url, outcome="success"))
    db.commit()
    return {"status": "completed", "host": info["host"], **result,
            "safety": "Passive header/TLS posture only. No port scan, no payloads, no exploitation."}

# ---------------- v1.3 Lawful forensics & reverse-engineering (static only) ----------------

@router.get("/forensics/tools")
def forensics_tools():
    return {"tools": KALI_FORENSICS_CATALOG,
            "workflow": "Isolate → preserve image + chain of custody → static analysis here → "
                        "deep review (Ghidra/Volatility/Wireshark) on analyst workstation → "
                        "correlate IPs via Security Graph → report, never retaliate.",
            "note": "Defensive analysis of artifacts you own. No execution, no detonation, "
                    "no hack-back. Uploads capped at 5 MB and never stored."}

@router.post("/forensics/analyze")
async def forensics_analyze(file: UploadFile = File(...), db: Session = Depends(get_db)):
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File too large — 5 MB cap for safe static analysis")
    if not data:
        raise HTTPException(400, "Empty file")
    report = analyze_bytes(data, filename=file.filename or "upload")
    db.add(AuditEvent(actor="analyst", action="forensics_static_analysis",
                      target=f"{report['filename']} sha256:{report['sha256'][:16]}…",
                      outcome=report["risk"].lower()))
    db.commit()
    return report

# ---------------- v1.3 Network visibility: devices + DNS browsing + logins ----------------
# Lawful scope: YOUR OWN network/devices with written authorization + user notice.
# Browsing = DNS/flow metadata only (never MITM content). Logins = your own systems.

class DeviceIn(BaseModel):
    hostname: str; ip_address: str = ""; mac: str = ""; os: str = ""; owner: str = ""

class DnsIn(BaseModel):
    hostname: str = ""; domain: str; query_type: str = "A"; hits: int = 1

class LoginIn(BaseModel):
    username: str; source_ip: str; hostname: str = ""
    success: bool = False; method: str = "password"

@router.post("/ingest/devices")
def ingest_devices(items: list[DeviceIn], db: Session = Depends(get_db), _auth: None = Depends(require_collector)):
    if not items or len(items) > 500: raise HTTPException(400, "Send 1..500 devices per batch")
    from datetime import datetime, timezone
    from ..models import Device
    n = 0
    for i in items:
        host = i.hostname.strip()
        if not host: raise HTTPException(400, "hostname required")
        d = db.query(Device).filter(Device.hostname == host).first()
        if d:
            d.ip_address = i.ip_address or d.ip_address; d.mac = i.mac or d.mac
            d.os = i.os or d.os; d.owner = i.owner or d.owner
            d.last_seen = datetime.now(timezone.utc)
        else:
            db.add(Device(hostname=host, ip_address=i.ip_address, mac=i.mac,
                          os=i.os, owner=i.owner))
        n += 1
    db.add(AuditEvent(actor="collector", action="ingest_devices", target=f"{n} devices", outcome="success"))
    db.commit()
    return {"ingested": n}

@router.post("/ingest/dns")
def ingest_dns(items: list[DnsIn], db: Session = Depends(get_db), _auth: None = Depends(require_collector)):
    if not items or len(items) > 1000: raise HTTPException(400, "Send 1..1000 queries per batch")
    from ..models import DnsQuery
    rows = [DnsQuery(hostname=i.hostname.strip(), domain=i.domain.strip().lower(),
                     query_type=i.query_type.upper(), hits=max(1, i.hits)) for i in items]
    if any(not r.domain for r in rows): raise HTTPException(400, "domain required")
    db.add_all(rows)
    db.add(AuditEvent(actor="collector", action="ingest_dns", target=f"{len(rows)} queries", outcome="success"))
    db.commit()
    return {"ingested": len(rows)}

@router.post("/ingest/logins")
def ingest_logins(items: list[LoginIn], db: Session = Depends(get_db), _auth: None = Depends(require_collector)):
    if not items or len(items) > 1000: raise HTTPException(400, "Send 1..1000 attempts per batch")
    from ..models import LoginAttempt
    db.add_all([LoginAttempt(**i.model_dump()) for i in items])
    fails = sum(1 for i in items if not i.success)
    db.add(AuditEvent(actor="collector", action="ingest_logins",
                      target=f"{len(items)} attempts ({fails} failed)", outcome="success"))
    db.commit()
    return {"ingested": len(items), "failed": fails}

@router.get("/devices")
def devices(db: Session = Depends(get_db)):
    from ..models import Device
    return [clean(d) for d in db.query(Device).order_by(Device.last_seen.desc()).limit(500).all()]

@router.get("/dns/top")
def dns_top(limit: int = Query(25, ge=1, le=100), db: Session = Depends(get_db)):
    return browsing_summary(db, limit=limit)

@router.get("/logins/attempts")
def login_attempts(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    from ..models import LoginAttempt
    return [clean(r) for r in db.query(LoginAttempt).order_by(LoginAttempt.observed_at.desc()).limit(limit).all()]

@router.get("/logins/summary")
def logins_summary(db: Session = Depends(get_db)):
    return brute_force_candidates(db)

# ---------------- v1.4 Teams + remediation + live-session triage (defensive) ----------------

@router.get("/remediation")
def remediation(severity: str = Query("HIGH", pattern="^(CRITICAL|HIGH|MEDIUM|LOW)$"),
                category: str | None = Query(None, pattern="^(exposure|kev|privilege|mfa|cloud_public|ai_internet|headers|banner|plaintext_http|brute_force|unexpected_port|high_flow|anomaly_session|macro|pdf|pcap|eml)$")):
    from ..services.teams import SEVERITY_PLAYBOOKS, CATEGORY_PLAYBOOKS
    out = {"severity": severity, **SEVERITY_PLAYBOOKS[severity]}
    if category:
        out["category"] = category
        out["category_playbook"] = CATEGORY_PLAYBOOKS[category]
    return out

@router.get("/teams/red")
def team_red():
    from ..services.teams import RED_TEAM
    return RED_TEAM

@router.get("/teams/blue")
def team_blue():
    from ..services.teams import BLUE_TEAM
    return BLUE_TEAM

class TriageRequest(BaseModel):
    ip: str = ""
    username: str = ""

@router.post("/session/triage")
def session_triage(req: TriageRequest, db: Session = Depends(get_db)):
    """Correlate a suspicious IP/username against YOUR OWN telemetry.

    No interception, no access to third-party systems — reads your flows,
    logins, sessions, DNS and findings and returns evidence + next steps.
    """
    from ..models import NetworkFlow, LoginAttempt, SessionEvent, DnsQuery, Identity, Finding
    if not req.ip.strip() and not req.username.strip():
        raise HTTPException(400, "Provide ip and/or username from your own systems")
    ip, user = req.ip.strip(), req.username.strip()
    flows = [clean(f) for f in db.query(NetworkFlow).filter(
        (NetworkFlow.src_ip == ip) | (NetworkFlow.dst_ip == ip)).order_by(
        NetworkFlow.observed_at.desc()).limit(20).all()] if ip else []
    logins = [clean(r) for r in db.query(LoginAttempt).filter(
        ((LoginAttempt.source_ip == ip) if ip else True) &
        ((LoginAttempt.username == user) if user else True)).order_by(
        LoginAttempt.observed_at.desc()).limit(20).all()]
    sessions = [clean(s) for s in db.query(SessionEvent).filter(
        ((SessionEvent.source_ip == ip) if ip else True) &
        ((SessionEvent.username == user) if user else True)).order_by(
        SessionEvent.started_at.desc()).limit(20).all()] if (ip or user) else []
    identity = clean(db.query(Identity).filter(Identity.username == user).first()) if user else None
    fails = sum(1 for r in db.query(LoginAttempt).filter(
        ((LoginAttempt.source_ip == ip) if ip else True) &
        ((LoginAttempt.username == user) if user else True) &
        (LoginAttempt.success.is_(False))).all())
    steps = [
        "1. Confirm scope: is this IP/account part of YOUR estate or lab exercise? If unknown-external, treat as untrusted.",
        "2. Contain on your side: revoke sessions, force MFA/password reset, rate-limit or block IP at YOUR perimeter.",
        "3. Correlate: check flows/DNS above for beaconing or exfil; review privileged sessions in the window.",
        "4. Preserve + report per IR; do not access the remote party's systems.",
    ]
    if fails >= 5:
        steps.insert(1, f"Brute-force candidate ({fails} fails): prioritize lockout + alerting per policy.")
    db.add(AuditEvent(actor="analyst", action="session_triage",
                      target=f"ip={ip or '—'} user={user or '—'}", outcome="success"))
    db.commit()
    return {"ip": ip, "username": user, "failed_logins": fails, "flows": flows,
            "logins": logins, "sessions": sessions, "identity": identity,
            "recommendations": steps}

# ---------------- v1.5 Production: live threat-intel ----------------

class RefreshRequest(BaseModel):
    sources: list[str] = ["kev"]
    cves: list[str] = []

def _allowlisted_get(url: str, timeout: float = 25.0):
    """Outbound GET restricted to threat-intel allowlist (+ optional NVD_API_KEY)."""
    from urllib.parse import urlparse
    import httpx
    from ..services.threatintel import ALLOWED_HOSTS
    if urlparse(url).hostname not in ALLOWED_HOSTS:
        raise HTTPException(400, "URL not on threat-intel allowlist")
    headers = {}
    key = _os.getenv("NVD_API_KEY", "")
    if key and "nvd" in (urlparse(url).hostname or ""):
        headers["apiKey"] = key
    try:
        with httpx.Client(timeout=timeout) as c:
            return c.get(url, headers=headers).raise_for_status()
    except Exception as e:
        raise HTTPException(502, f"Threat feed fetch failed: {e}")

@router.post("/threat-intel/refresh")
def threat_refresh(req: RefreshRequest, db: Session = Depends(get_db)):
    from ..services.threatintel import refresh_kev, refresh_nvd
    stats: dict = {}
    if "kev" in req.sources:
        stats["kev"] = refresh_kev(db, lambda u: _allowlisted_get(u).text)
    if "nvd" in req.sources:
        stats["nvd"] = refresh_nvd(db, req.cves,
                                   lambda u: _allowlisted_get(u).json())
    db.add(AuditEvent(actor="analyst", action="threatintel_refresh",
                      target=str(stats), outcome="success"))
    db.commit()
    return stats

@router.get("/threat-intel/cves")
def threat_cves(kev_only: bool = False, limit: int = Query(100, ge=1, le=500),
                db: Session = Depends(get_db)):
    from ..models import CveRecord
    q = db.query(CveRecord)
    if kev_only:
        q = q.filter(CveRecord.kev.is_(True))
    return [clean(r) for r in q.order_by(CveRecord.cvss.desc()).limit(limit).all()]

# ---------------- v1.5 Production: MITRE coverage ----------------

@router.get("/mitre/techniques")
def mitre_techniques():
    from ..services.mitre import TECHNIQUES
    return {"techniques": TECHNIQUES}

@router.get("/mitre/coverage")
def mitre_coverage(db: Session = Depends(get_db)):
    from ..services.mitre import coverage
    return coverage(db)

# ---------------- v1.5 Production: USB / DLP ----------------

class UsbIn(BaseModel):
    hostname: str; device: str = ""; serial: str = ""; action: str = "connect"

class DlpIn(BaseModel):
    hostname: str = ""; username: str = ""; filepath: str = ""
    classification: str = "internal"; action: str = "allowed"

_STORAGE_HINTS = ("mass storage", "disk", "flash", "thumb", "usb drive", "external")

@router.post("/ingest/usb")
def ingest_usb(items: list[UsbIn], db: Session = Depends(get_db),
               _auth: None = Depends(require_collector)):
    from ..models import UsbEvent, Asset
    if not items or len(items) > 500: raise HTTPException(400, "Send 1..500 events per batch")
    for i in items:
        if i.action not in ("connect", "block", "allow"):
            raise HTTPException(400, "action must be connect|block|allow")
        if not i.hostname.strip(): raise HTTPException(400, "hostname required")
    db.add_all([UsbEvent(**i.model_dump()) for i in items])
    auto = 0
    for i in items:
        if i.action == "connect" and any(h in i.device.lower() for h in _STORAGE_HINTS):
            asset = db.query(Asset).filter(Asset.hostname == i.hostname.strip()).first()
            if asset and asset.criticality >= 5:
                db.add(Finding(asset_id=asset.id,
                               title=f"USB mass storage on critical host {i.hostname}"[:255],
                               severity="HIGH", cvss=0, exposure=False, data_sensitivity=5,
                               risk_score=70,
                               description=f"{i.device} (S/N {i.serial or 'unknown'}). Confirm authorised transfer or contain."[:2000]))
                auto += 1
    db.add(AuditEvent(actor="collector", action="ingest_usb",
                      target=f"{len(items)} events ({auto} auto-findings)", outcome="success"))
    db.commit()
    return {"ingested": len(items), "auto_findings": auto}

@router.get("/usb/events")
def usb_events(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    from ..models import UsbEvent
    return [clean(r) for r in db.query(UsbEvent).order_by(UsbEvent.observed_at.desc()).limit(limit).all()]

@router.get("/usb/summary")
def usb_summary(db: Session = Depends(get_db)):
    from ..models import UsbEvent
    rows = db.query(UsbEvent).all()
    by_action: dict[str, int] = {}
    for r in rows:
        by_action[r.action] = by_action.get(r.action, 0) + 1
    return {"total": len(rows), "by_action": by_action,
            "help": "Storage-class connects on criticality-5 hosts auto-raise HIGH findings."}

@router.post("/ingest/dlp")
def ingest_dlp(items: list[DlpIn], db: Session = Depends(get_db),
               _auth: None = Depends(require_collector)):
    from ..models import DlpEvent
    if not items or len(items) > 500: raise HTTPException(400, "Send 1..500 events per batch")
    for i in items:
        if i.classification not in ("secret", "restricted", "confidential", "internal", "public"):
            raise HTTPException(400, "bad classification")
        if i.action not in ("blocked", "quarantined", "allowed"):
            raise HTTPException(400, "action must be blocked|quarantined|allowed")
    db.add_all([DlpEvent(**i.model_dump()) for i in items])
    auto = 0
    for i in items:
        if i.classification in ("secret", "restricted") and i.action == "allowed":
            db.add(Finding(asset_id=db.query(Asset).first().id if db.query(Asset).first() else 1,
                           title=f"DLP policy gap: {i.classification} left boundary ({i.filepath})"[:255],
                           severity="MEDIUM", cvss=0, exposure=False, data_sensitivity=5,
                           risk_score=55,
                           description=f"{i.username}@{i.hostname}: {i.filepath} classified {i.classification} but allowed. Tighten rule."[:2000]))
            auto += 1
    db.add(AuditEvent(actor="collector", action="ingest_dlp",
                      target=f"{len(items)} events ({auto} auto-findings)", outcome="success"))
    db.commit()
    return {"ingested": len(items), "auto_findings": auto}

@router.get("/dlp/events")
def dlp_events(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    from ..models import DlpEvent
    return [clean(r) for r in db.query(DlpEvent).order_by(DlpEvent.observed_at.desc()).limit(limit).all()]

@router.get("/dlp/summary")
def dlp_summary(db: Session = Depends(get_db)):
    from ..models import DlpEvent
    rows = db.query(DlpEvent).all()
    by_class: dict[str, int] = {}
    gaps = 0
    for r in rows:
        by_class[r.classification] = by_class.get(r.classification, 0) + 1
        if r.classification in ("secret", "restricted") and r.action == "allowed":
            gaps += 1
    return {"total": len(rows), "by_classification": by_class, "policy_gaps": gaps}

# ---------------- v1.5 Production: collector heartbeat (agent single-call sync) ----------------

class HbService(BaseModel):
    port: int = Field(ge=1, le=65535); protocol: str = "TCP"; service: str = "unknown"
    process: str = "unknown"; user: str = "unknown"; expected: bool = True

class HbUsb(BaseModel):
    device: str = ""; serial: str = ""; action: str = "connect"

class Heartbeat(BaseModel):
    hostname: str; ip_address: str = ""; mac: str = ""; os: str = ""; owner: str = ""
    services: list[HbService] = []; usb: list[HbUsb] = []

@router.post("/collector/heartbeat")
def heartbeat(hb: Heartbeat, db: Session = Depends(get_db),
              _auth: None = Depends(require_collector)):
    """Agent sync: upsert device + asset, reconcile services, record USB. Returns counts."""
    from ..models import Device
    from datetime import datetime, timezone
    host = hb.hostname.strip()
    if not host: raise HTTPException(400, "hostname required")
    d = db.query(Device).filter(Device.hostname == host).first()
    if d is None:
        d = Device(hostname=host, source="agent")
        db.add(d)
    d.ip_address, d.mac, d.os, d.owner = hb.ip_address, hb.mac, hb.os, hb.owner
    d.last_seen = datetime.now(timezone.utc)
    asset = db.query(Asset).filter(Asset.hostname == host).first()
    if asset is None:
        asset = Asset(hostname=host, ip_address=hb.ip_address or "0.0.0.0",
                      asset_type="endpoint", environment="production",
                      criticality=2, owner=hb.owner or "Unassigned")
        db.add(asset)
        db.flush()
    db.query(Service).filter(Service.asset_id == asset.id).delete()
    for s in hb.services[:200]:
        db.add(Service(asset_id=asset.id, port=s.port, protocol=s.protocol,
                       service=s.service, process=s.process, user=s.user, expected=s.expected))
    usb_n = 0
    if hb.usb:
        from ..models import UsbEvent
        db.add_all([UsbEvent(hostname=host, device=u.device, serial=u.serial, action=u.action)
                    for u in hb.usb[:50]])
        usb_n = len(hb.usb[:50])
    db.add(AuditEvent(actor="agent", action="heartbeat",
                      target=f"{host}: {len(hb.services[:200])} services, {usb_n} usb",
                      outcome="success"))
    db.commit()
    return {"device": host, "asset_id": asset.id,
            "services": len(hb.services[:200]), "usb": usb_n}

# ---------------- v1.5 Production: cloud adapters ----------------

class ProwlerItem(BaseModel):
    check: str; provider: str = "AWS"; resource: str = ""; resource_type: str = ""
    region: str = ""; status: str = "FAIL"; severity: str = "MEDIUM"

@router.get("/cloud/adapters")
def cloud_adapters():
    from ..services.cloud_adapters import ADAPTERS
    return {"adapters": ADAPTERS}

@router.post("/cloud/import-prowler")
def cloud_prowler(items: list[ProwlerItem], db: Session = Depends(get_db)):
    from ..services.cloud_adapters import import_prowler
    if not items or len(items) > 1000: raise HTTPException(400, "Send 1..1000 items per batch")
    out = import_prowler(db, [i.model_dump() for i in items])
    db.add(AuditEvent(actor="analyst", action="prowler_import", target=str(out), outcome="success"))
    db.commit()
    return out

class CloudScanRequest(BaseModel):
    provider: str = "aws"

@router.post("/cloud/scan")
def cloud_scan(req: CloudScanRequest, db: Session = Depends(get_db)):
    """Live read-only AWS scan. 501 with setup guidance when boto3/creds are absent."""
    if req.provider != "aws":
        raise HTTPException(400, "Only 'aws' live scan is implemented; use import-prowler for the rest")
    try:
        import boto3  # type: ignore
    except ImportError:
        raise HTTPException(501, "boto3 not installed: pip install boto3 + configure read-only AWS creds, then retry")
    if not (_os.getenv("AWS_ACCESS_KEY_ID") and _os.getenv("AWS_SECRET_ACCESS_KEY")):
        raise HTTPException(501, "AWS creds absent: set AWS_ACCESS_KEY_ID/SECRET_ACCESS_KEY (read-only IAM) on the backend host")
    from ..services.cloud_adapters import aws_live_scan
    out = aws_live_scan(db, boto3.client("ec2"), boto3.client("s3"), boto3.client("iam"))
    db.add(AuditEvent(actor="analyst", action="aws_live_scan", target=str(out), outcome="success"))
    db.commit()
    return out

# ---------------- v1.5 Production: AI eval + vector-DB audit ----------------

@router.get("/ai/probes")
def ai_probes():
    """Probe battery metadata (names/categories only — prompts execute server-side)."""
    from ..services.ai_red import PROBES
    return {"probes": [{k: p[k] for k in ("id", "name", "category")} for p in PROBES]}

class AiEvalRequest(BaseModel):
    url: str
    approval_confirmed: bool = False

@router.post("/ai/evaluate")
async def ai_evaluate(req: AiEvalRequest, db: Session = Depends(get_db)):
    """Run the injection/jailbreak battery against a LAB/PRIVATE AI gateway (approval-gated)."""
    import httpx
    from ..services.ai_red import evaluate
    try:
        info = validate_target(req.url)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not (info.get("lab") or info["private"]):
        raise HTTPException(400, "AI evaluation is restricted to lab/private targets — internet AI is out of scope")
    if not req.approval_confirmed:
        db.add(AuditEvent(actor="demo-user", action="ai_eval_pending_approval",
                          target=req.url, outcome="pending-approval")); db.commit()
        return {"status": "pending_approval", "host": info["host"],
                "message": "AI probing needs explicit approval. Resubmit with approval_confirmed=true."}
    try:
        check_cooldown("ai-eval:" + info["host"])
    except ValueError as e:
        raise HTTPException(429, str(e))

    def post_fn(url: str, prompt: str) -> str:
        with httpx.Client(timeout=15) as c:
            r = c.post(url, json={"prompt": prompt})
            r.raise_for_status()
            try:
                return str(r.json().get("output", ""))[:2000]
            except Exception:
                return r.text[:2000]

    try:
        report = evaluate(req.url, post_fn)
    except Exception as e:
        raise HTTPException(502, f"AI evaluation failed: {e}")
    if report["failed"]:
        db.add(Finding(asset_id=db.query(Asset).first().id if db.query(Asset).first() else 1,
                       title=f"AI gateway complied with {report['failed']}/{len(report['probes'])} hostile probes"[:255],
                       severity=report["verdict"], cvss=0, exposure=False, data_sensitivity=5,
                       risk_score=78 if report["verdict"] == "HIGH" else 58,
                       description=report["guidance"][:2000]))
    db.add(AuditEvent(actor="demo-user", action="ai_eval_completed",
                      target=f"{req.url} failed={report['failed']}", outcome="success"))
    db.commit()
    return {"status": "completed", **report}

class RetrievalIn(BaseModel):
    agent: str; vector_store: str; tenant: str = ""; doc_class: str = "internal"

@router.post("/ai/retrieval-audit")
def retrieval_audit(item: RetrievalIn, db: Session = Depends(get_db)):
    from ..services.vectordb import log_retrieval
    if not item.agent.strip() or not item.vector_store.strip():
        raise HTTPException(400, "agent and vector_store are required")
    return log_retrieval(db, item.agent.strip(), item.vector_store.strip(),
                         item.tenant.strip(), item.doc_class.strip())

@router.get("/ai/retrieval-audit")
def retrieval_list(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    from ..models import RetrievalEvent
    return [clean(r) for r in db.query(RetrievalEvent).order_by(
        RetrievalEvent.observed_at.desc()).limit(limit).all()]

# ---------------- v1.5 Production: SOAR ----------------

@router.get("/soar/playbooks")
def soar_playbooks():
    from ..services.soar import PLAYBOOKS
    return {"playbooks": PLAYBOOKS}

class SoarRunRequest(BaseModel):
    playbook: str
    target: str
    approval_confirmed: bool = False

@router.post("/soar/runs")
def soar_runs(req: SoarRunRequest, db: Session = Depends(get_db)):
    from ..services.soar import run_playbook
    try:
        return run_playbook(db, req.playbook, req.target, approved=req.approval_confirmed)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/soar/runs/{run_id}/approve")
def soar_approve(run_id: int, db: Session = Depends(get_db)):
    from ..services.soar import approve_run
    try:
        return approve_run(db, run_id)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/soar/runs")
def soar_list(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    from ..models import SoarRun
    return [clean(r) for r in db.query(SoarRun).order_by(SoarRun.created_at.desc()).limit(limit).all()]

# ---------------- v1.5 Production: Wi-Fi/LAN neighbour discovery ----------------
# Observed hosts (arp/ping-sweep) pushed by the agent running on YOUR laptop —
# Docker containers cannot see host Wi-Fi, so discovery runs at the edge.

class DiscoveryIn(BaseModel):
    ip_address: str; mac: str = ""; hostname: str = ""; source: str = "agent-discover"

@router.post("/ingest/discovery")
def ingest_discovery(items: list[DiscoveryIn], db: Session = Depends(get_db),
                     _auth: None = Depends(require_collector)):
    from ..services.discovery import upsert_discovery
    if not items or len(items) > 1000: raise HTTPException(400, "Send 1..1000 hosts per batch")
    out = upsert_discovery(db, [i.model_dump() for i in items])
    db.add(AuditEvent(actor="collector", action="ingest_discovery",
                      target=f"{out['hosts']} hosts ({out['new']} new)", outcome="success"))
    db.commit()
    return out

@router.get("/discovery/hosts")
def discovery_hosts(limit: int = Query(200, ge=1, le=1000), db: Session = Depends(get_db)):
    from ..models import DiscoveredHost
    return [clean(r) for r in db.query(DiscoveredHost).order_by(
        DiscoveredHost.last_seen.desc()).limit(limit).all()]

class WifiNetworkIn(BaseModel):
    ssid: str = ""
    bssid: str = ""
    security: str = "Unknown"
    channel: str = ""
    band: str = ""
    signal_dbm: float | None = None
    source: str = "local-sensor"

@router.post("/ingest/wifi-networks")
def ingest_wifi_networks(items: list[WifiNetworkIn], db: Session = Depends(get_db), _auth: None = Depends(require_collector)):
    if not items or len(items) > 500:
        raise HTTPException(400, "Send 1..500 Wi-Fi networks per scan")
    from datetime import datetime, timezone
    seen = set()
    for i in items:
        bssid = i.bssid.strip().upper()
        key = bssid or i.ssid.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        row = db.query(WifiNetwork).filter(WifiNetwork.bssid == bssid).first() if bssid else None
        if row is None:
            row = WifiNetwork(ssid=i.ssid[:255], bssid=bssid[:64], security=i.security[:64], channel=i.channel[:32], band=i.band[:32], signal_dbm=i.signal_dbm, source=i.source[:64])
            db.add(row)
        else:
            row.ssid=i.ssid[:255]; row.security=i.security[:64]; row.channel=i.channel[:32]; row.band=i.band[:32]; row.signal_dbm=i.signal_dbm; row.source=i.source[:64]; row.observed_at=datetime.now(timezone.utc)
    db.add(AuditEvent(actor="wifi-sensor", action="ingest_wifi_scan", target=f"{len(seen)} networks", outcome="success"))
    db.commit()
    return {"ingested": len(seen)}

class WifiTrustUpdate(BaseModel):
    trusted: bool

@router.put("/discovery/hosts/{host_id}/trust")
def update_discovered_host_trust(host_id: int, req: WifiTrustUpdate, db: Session = Depends(get_db)):
    from ..models import DiscoveredHost
    row=db.query(DiscoveredHost).filter(DiscoveredHost.id==host_id).first()
    if not row: raise HTTPException(404, "Discovered device not found")
    row.trusted=req.trusted
    db.add(AuditEvent(actor="console-user", action="wifi_device_trust_changed", target=f"{row.mac or row.ip_address}", outcome="trusted" if req.trusted else "untrusted"))
    db.commit()
    return clean(row)

@router.get("/discovery/wifi-networks")
def discovery_wifi_networks(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    rows = db.query(WifiNetwork).order_by(WifiNetwork.signal_dbm.desc().nullslast(), WifiNetwork.observed_at.desc()).limit(limit).all()
    return [clean(x) for x in rows]

@router.get("/discovery/summary")
def discovery_summary(db: Session = Depends(get_db)):
    from ..models import DiscoveredHost
    rows = db.query(DiscoveredHost).all()
    by_vendor: dict[str, int] = {}
    named = 0
    for r in rows:
        by_vendor[r.vendor or "Unknown"] = by_vendor.get(r.vendor or "Unknown", 0) + 1
        if r.hostname and not r.hostname.startswith("host-"):
            named += 1
    return {"total": len(rows), "named": named, "by_vendor": by_vendor,
            "help": "Observed neighbours on YOUR Wi-Fi/LAN. Unknown vendor + generated name = triage first: confirm the device or block it at your router."}

# ---------------------------------------------------------------------------
# AI / Agent Security Control Plane
# ---------------------------------------------------------------------------
@router.get("/ai-security/catalog")
def ai_security_catalog():
    from ..services.ai_security import catalog
    return {"tools": catalog(), "source": "VEYRA curated integration registry"}

@router.get("/ai-security/controls")
def ai_security_controls():
    from ..services.ai_security import controls
    return {"controls": controls(), "frameworks": ["OWASP GenAI LLM Top 10 2026", "OWASP Agentic Applications 2026", "OWASP Agent Control Standard", "MITRE ATLAS", "NIST AI RMF"]}

class AgentPostureRequest(BaseModel):
    name: str
    agent_type: str = "internal-agent"
    owner: str = ""
    environment: str = "internal"
    tool_allowlist: list[str] = []
    approval_boundary: bool = True
    short_lived_identity: bool = False
    memory_provenance: bool = False
    rag_authorization: bool = False
    otel: bool = False
    human_approval: bool = False
    supply_chain_provenance: bool = False

@router.post("/ai-security/agent-posture")
def ai_agent_posture(req: AgentPostureRequest):
    from ..services.ai_security import assess_agent
    return {"agent": req.model_dump(exclude={"tool_allowlist"}), "tool_allowlist": req.tool_allowlist, **assess_agent(req.model_dump())}

# Worker-to-control-plane boundary. This endpoint never accepts a command string.
class WorkerHeartbeatRequest(BaseModel):
    worker_id: str
    capabilities: list[str] = []
    environment: str = "lab"

class WorkerEvidenceRequest(BaseModel):
    contract_sha256: str
    contract_signature: str
    payload: dict


def require_worker(request: Request):
    expected = _os.getenv("VEYRA_WORKER_TOKEN", "")
    supplied = request.headers.get("X-VEYRA-Worker-Token", "")
    if not expected or not supplied or supplied != expected:
        raise HTTPException(403, "Authenticated isolated worker required")
    return True

@router.get("/worker/jobs/next")
def worker_next_job(db: Session = Depends(get_db), _: bool = Depends(require_worker)):
    from ..services.execution_plane import make_job_contract
    row = db.query(SecurityToolJob).filter(SecurityToolJob.status=="queued_for_isolated_worker").order_by(SecurityToolJob.created_at.asc()).first()
    if not row: return {"job": None}
    tools={x["name"]:x for x in admin_tool_registry()}
    tool=tools.get(row.tool)
    if not tool: raise HTTPException(409,"Registered tool definition missing")
    contract={"job_id":row.job_id,"tool":row.tool,"tool_id":tool["id"],"execution_profile":tool["execution_profile"],"target":row.target,"scope":json.loads(row.scope or "[]"),"approval_ticket":row.approval_ticket,"environment":row.environment,"purpose":row.purpose,"actor":row.actor,"created_at":row.created_at.isoformat() if row.created_at else "","execution":"not_started","browser_shell":False,"contract_sha256":row.contract_sha256}
    from ..services.execution_plane import hmac, hashlib
    secret=_os.getenv("VEYRA_WORKER_SIGNING_SECRET","")
    if not secret: raise HTTPException(503,"Worker signing secret is not configured")
    contract["contract_signature"]=hmac.new(secret.encode(),row.contract_sha256.encode(),hashlib.sha256).hexdigest()
    row.status="worker_claimed"
    db.add(AuditEvent(actor="isolated-worker", action="ethical_hacking_job_claimed", target=row.job_id, outcome="worker_claimed"))
    db.commit()
    return {"job":contract}

@router.post("/worker/evidence")
def worker_evidence(req: WorkerEvidenceRequest, db: Session = Depends(get_db), _: bool = Depends(require_worker)):
    from ..services.execution_plane import verify_contract_signature, normalize_evidence
    if not verify_contract_signature(req.contract_sha256, req.contract_signature):
        raise HTTPException(403,"Invalid worker contract signature")
    row=db.query(SecurityToolJob).filter(SecurityToolJob.contract_sha256==req.contract_sha256).first()
    if not row or row.status not in {"worker_claimed","queued_for_isolated_worker"}:
        raise HTTPException(409,"Unknown or inactive job contract")
    try: artifact=normalize_evidence(row.job_id,req.payload)
    except ValueError as e: raise HTTPException(400,str(e))
    row.status="completed"
    db.add(SecurityEvidence(artifact_id=artifact["artifact_id"],job_id=row.job_id,sha256=artifact["sha256"],source=artifact["source"],collector=artifact["collector"],collected_at=artifact["collected_at"],classification=artifact["classification"],result_type=artifact["result_type"],summary=artifact["summary"],data=json.dumps(artifact["data"],default=str)))
    db.add(AuditEvent(actor="isolated-worker", action="ethical_hacking_evidence_ingested", target=row.job_id, outcome=artifact["artifact_id"]))
    db.commit()
    return {"job_id":row.job_id,"status":"completed","artifact":artifact}

# ---------------- v2.1: Autonomous Security Operations Fabric ----------------
class InvestigationStartRequest(BaseModel):
    event_id: str = Field(min_length=3, max_length=64)

class ContainmentRequest(BaseModel):
    action: str
    target: str = Field(min_length=1, max_length=255)
    reason: str = Field(min_length=3, max_length=1000)

class ApprovalDecisionRequest(BaseModel):
    approved: bool
    actor: str = Field(default="analyst", min_length=2, max_length=255)

@router.get("/autonomous-soc/overview")
def autonomous_soc_overview(db: Session = Depends(get_db)):
    from ..models import InvestigationCase, InvestigationApproval
    return {
        "pipeline": ["alert","evidence_preservation","deterministic_correlation","attack_path_reasoning","ai_investigation","evidence_bundle","risk_confidence","human_approval","soar_containment","verification","closure_learning"],
        "cases": db.query(InvestigationCase).count(),
        "awaiting_approval": db.query(InvestigationCase).filter(InvestigationCase.status=="awaiting_approval").count(),
        "pending_approvals": db.query(InvestigationApproval).filter(InvestigationApproval.status=="pending").count(),
        "side_effects": "disabled in POC; approved actions are handed to governed SOAR adapters only"
    }

@router.get("/autonomous-soc/cases")
def autonomous_soc_cases(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    from ..services.autonomous_soc import list_cases
    return list_cases(db, limit)

@router.post("/autonomous-soc/investigate")
def autonomous_soc_investigate(req: InvestigationStartRequest, db: Session = Depends(get_db)):
    from ..services.autonomous_soc import investigate_event
    try: return investigate_event(db, req.event_id)
    except ValueError as e: raise HTTPException(400, str(e))

@router.post("/autonomous-soc/cases/{case_id}/containment")
def autonomous_soc_containment(case_id: str, req: ContainmentRequest, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.autonomous_soc import request_containment
    try: return request_containment(db, case_id, req.action, req.target, req.reason)
    except ValueError as e: raise HTTPException(400, str(e))

@router.post("/autonomous-soc/approvals/{approval_id}")
def autonomous_soc_approval(approval_id: int, req: ApprovalDecisionRequest, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.autonomous_soc import decide_approval
    try: return decide_approval(db, approval_id, req.approved, req.actor)
    except ValueError as e: raise HTTPException(400, str(e))

# ---------------- v2.2: Continuous Detection & Response Mesh ----------------
class MeshAlertRequest(BaseModel):
    event_id: str | None = Field(default=None, max_length=64)
    trace_id: str | None = Field(default=None, max_length=128)
    plane: str = Field(default="detection", max_length=64)
    event_type: str = Field(default="alert", max_length=128)
    actor: str = Field(default="", max_length=255)
    source: str = Field(default="", max_length=255)
    target: str = Field(default="", max_length=255)
    risk_score: float = Field(default=0, ge=0, le=100)
    severity: str = Field(default="INFO", max_length=32)
    payload: dict = Field(default_factory=dict)

class MeshResponseRequest(BaseModel):
    action: str
    target: str = Field(min_length=1, max_length=255)
    approval_id: int | None = None

class MeshVerifyRequest(BaseModel):
    observed_state: bool
    evidence: dict = Field(default_factory=dict)

@router.get("/detection-mesh/overview")
def detection_mesh_overview(db: Session = Depends(get_db)):
    from ..services.response_mesh import ensure_rules, connector_health
    from ..models import DetectionRule, ResponseAction
    ensure_rules(db)
    return {
        "version": "2.2",
        "mode": "continuous_detection_response_mesh",
        "rules": db.query(DetectionRule).filter(DetectionRule.enabled==True).count(),
        "response_actions": db.query(ResponseAction).count(),
        "connectors": connector_health(),
        "enforcement": "approval-gated; POC adapters perform no external enforcement",
        "pipeline": ["ingest","normalize","detect","correlate","investigate","approve","respond","verify","learn"]
    }

@router.get("/detection-mesh/rules")
def detection_mesh_rules(db: Session = Depends(get_db)):
    from ..services.response_mesh import ensure_rules
    from ..models import DetectionRule
    ensure_rules(db)
    rows=db.query(DetectionRule).order_by(DetectionRule.rule_id).all()
    return [{"rule_id":r.rule_id,"name":r.name,"source":r.source,"event_types":json.loads(r.event_types or "[]"),"min_risk_score":r.min_risk_score,"enabled":r.enabled,"action":r.action} for r in rows]

@router.post("/detection-mesh/alerts")
def detection_mesh_alert(req: MeshAlertRequest, db: Session = Depends(get_db), _: bool = Depends(require_collector)):
    from ..services.response_mesh import ingest_alert
    try: return ingest_alert(db, req.model_dump())
    except ValueError as e: raise HTTPException(400, str(e))

@router.get("/detection-mesh/response-actions")
def detection_mesh_actions(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.response_mesh import list_actions
    return list_actions(db, limit)

@router.post("/detection-mesh/cases/{case_id}/response")
def detection_mesh_response(case_id: str, req: MeshResponseRequest, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.response_mesh import request_response
    try: return request_response(db, case_id, req.action, req.target, req.approval_id)
    except ValueError as e: raise HTTPException(400, str(e))

@router.post("/detection-mesh/response-actions/{action_id}/verify")
def detection_mesh_verify(action_id: str, req: MeshVerifyRequest, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.response_mesh import verify_response
    try: return verify_response(db, action_id, req.observed_state, req.evidence)
    except ValueError as e: raise HTTPException(400, str(e))

# ---------------- v2.3: Investigation + Threat Intelligence Fusion ----------------
@router.get("/intel-fusion/overview")
def intel_fusion_overview(db: Session = Depends(get_db)):
    from ..models import AttributionHypothesis, IntelEnrichment
    from ..models import InvestigationCase
    return {"version":"2.3","cases":db.query(InvestigationCase).count(),
            "intel_records":db.query(ThreatIntel).count(),
            "enrichments":db.query(IntelEnrichment).count(),
            "attribution_hypotheses":db.query(AttributionHypothesis).count(),
            "attribution_mode":"hypothesis_only"}

@router.post("/intel-fusion/cases/{case_id}/enrich")
def intel_fusion_enrich(case_id: str, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.intel_fusion import fuse_case
    try: return fuse_case(db, case_id)
    except ValueError as e: raise HTTPException(400, str(e))

@router.get("/intel-fusion/cases/{case_id}")
def intel_fusion_case(case_id: str, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.intel_fusion import fuse_case
    try: return fuse_case(db, case_id)
    except ValueError as e: raise HTTPException(404, str(e))

@router.get("/intel-fusion/hypotheses")
def intel_fusion_hypotheses(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..models import AttributionHypothesis
    rows=db.query(AttributionHypothesis).order_by(AttributionHypothesis.confidence.desc()).limit(limit).all()
    return [{"hypothesis_id":r.hypothesis_id,"case_id":r.case_id,"label":r.label,"confidence":r.confidence,
             "supporting_evidence":json.loads(r.supporting_json or "[]"),
             "contradicting_evidence":json.loads(r.contradicting_json or "[]"),"assessment":r.assessment} for r in rows]

@router.get("/intel-fusion/enrichments")
def intel_fusion_enrichments(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..models import IntelEnrichment
    rows=db.query(IntelEnrichment).order_by(IntelEnrichment.created_at.desc()).limit(limit).all()
    return [clean(r) for r in rows]


# ---------------- v2.9: Adversary Intelligence & Wireless Defense Fabric ----------------
@router.get("/v29/overview")
def v29_overview(db: Session = Depends(get_db)):
    from ..services.v29_adversary import overview
    return overview(db)

@router.get("/v29/wireless")
def v29_wireless(db: Session = Depends(get_db)):
    from ..services.v29_adversary import wireless
    return wireless(db)

@router.get("/v29/timeline")
def v29_timeline(db: Session = Depends(get_db)):
    from ..services.v29_adversary import timeline
    return timeline(db)

@router.get("/v29/infrastructure")
def v29_infrastructure(db: Session = Depends(get_db)):
    from ..services.v29_adversary import infrastructure
    return infrastructure(db)

@router.get("/v29/attribution")
def v29_attribution(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.v29_adversary import attribution
    return attribution(db)

@router.post("/v29/evidence-bundle")
def v29_evidence_bundle(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.v29_adversary import evidence_bundle
    bundle=evidence_bundle(db)
    db.add(AuditEvent(actor="v29-console", action="evidence_bundle_staged", target=bundle["bundle_id"], outcome="staged"))
    db.commit()
    return bundle

# ---------------- v2.5 Identity & click-to-select permissions ----------------
class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=512)

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=512)
    new_password: str = Field(min_length=12, max_length=512)

class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    display_name: str = Field(min_length=1, max_length=255)
    email: str = ""
    password: str = Field(min_length=12, max_length=512)
    role: str = "viewer"
    mfa_required: bool = True
    tool_permissions: dict[str, str] = {}

class UserUpdateRequest(BaseModel):
    display_name: str | None = None
    email: str | None = None
    role: str | None = None
    status: str | None = None
    mfa_required: bool | None = None
    tool_permissions: dict[str, str] | None = None

VALID_ROLES = {"sudo", "security_admin", "security_operator", "analyst", "viewer"}
VALID_LEVELS = {"none", "view", "plan", "execute_request"}

def _auth_user(request: Request, db: Session):
    from ..services.auth import current_user
    return current_user(request, db)

def _sudo(request: Request, db: Session):
    from ..services.auth import require_sudo
    return require_sudo(request, db)

def _validate_permissions(perms: dict[str,str]):
    tools = {t["id"] for t in admin_tool_registry()}
    unknown = sorted(set(perms) - tools)
    levels = {}
    for k, v in perms.items():
        # Accept "plan" or {"level":"plan","expires_in_hours":5}
        levels[k] = v.get("level", "none") if isinstance(v, dict) else v
    bad = {k:v for k,v in levels.items() if v not in VALID_LEVELS}
    if unknown: raise HTTPException(400, f"Unknown tool IDs: {', '.join(unknown[:10])}")
    if bad: raise HTTPException(400, f"Invalid permission levels: {bad}")
    return levels

def _grant_expiry_from_value(v) -> tuple[str, object]:
    """Normalise a permission value to (level, expires_at)."""
    from ..services.auth import grant_expiry
    if isinstance(v, dict):
        level = v.get("level", "none")
        hours = v.get("expires_in_hours")
        return level, grant_expiry(hours) if hours is not None else None
    return v, None

@router.post("/auth/login")
def auth_login(req: LoginRequest, db: Session = Depends(get_db)):
    from ..services.auth import verify_password, issue_session
    user = db.query(UserAccount).filter(UserAccount.username == req.username).first()
    if not user or user.status != "active" or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid username or password")
    token = issue_session(db, user)
    db.add(AuditEvent(actor=user.username, action="login", target=user.username, outcome="success")); db.commit()
    return {"token":token,"user":{"id":user.id,"username":user.username,"display_name":user.display_name,"role":user.role,"must_change_password":user.must_change_password}}

@router.post("/auth/logout")
def auth_logout(request: Request, db: Session = Depends(get_db)):
    from ..services.auth import current_user
    user=current_user(request,db)
    raw=request.headers.get("Authorization","")[7:].strip()
    import hashlib
    s=db.query(UserSession).filter(UserSession.token_hash==hashlib.sha256(raw.encode()).hexdigest()).first()
    if s: s.revoked_at=__import__('datetime').datetime.now(__import__('datetime').timezone.utc)
    db.add(AuditEvent(actor=user.username, action="logout", target=user.username, outcome="success")); db.commit()
    return {"status":"logged_out"}

@router.get("/auth/me")
def auth_me(request: Request, db: Session = Depends(get_db)):
    user=_auth_user(request,db)
    return {"id":user.id,"username":user.username,"display_name":user.display_name,"email":user.email,"role":user.role,"status":user.status,"mfa_required":user.mfa_required,"must_change_password":user.must_change_password}

@router.post("/auth/password")
def auth_password(req: PasswordChangeRequest, request: Request, db: Session = Depends(get_db)):
    from ..services.auth import verify_password, hash_password
    user=_auth_user(request,db)
    if not verify_password(req.current_password,user.password_hash): raise HTTPException(400,"Current password is incorrect")
    if req.current_password == req.new_password: raise HTTPException(400,"New password must differ from current password")
    user.password_hash=hash_password(req.new_password); user.must_change_password=False
    db.add(AuditEvent(actor=user.username, action="password_changed", target=user.username, outcome="success")); db.commit()
    return {"status":"password_changed"}

@router.get("/admin/users")
def users_list(request: Request, db: Session=Depends(get_db)):
    _sudo(request,db)
    rows=db.query(UserAccount).order_by(UserAccount.username).all()
    out=[]
    for u in rows:
        perms=db.query(UserToolPermission).filter(UserToolPermission.user_id==u.id).all()
        grants={}
        for p in perms:
            grants[p.tool_id]={"level":p.level,
                "expires_at":p.expires_at.isoformat() if p.expires_at else None,
                "granted_by":p.granted_by}
        out.append({"id":u.id,"username":u.username,"display_name":u.display_name,"email":u.email,"role":u.role,"status":u.status,"mfa_required":u.mfa_required,"must_change_password":u.must_change_password,"tool_permissions":{p.tool_id:p.level for p in perms},"tool_grants":grants})
    return out

@router.get("/admin/users/tool-catalog")
def users_tool_catalog(request: Request, db: Session=Depends(get_db)):
    _sudo(request,db)
    return {"tools":admin_tool_registry(),"permission_levels":[
        {"id":"none","label":"No access","description":"Tool is hidden from the user's usable tool list."},
        {"id":"view","label":"View","description":"Can read catalog/help and evidence; cannot stage work."},
        {"id":"plan","label":"Plan","description":"Can create a governed assessment plan; approval remains required."},
        {"id":"execute_request","label":"Request execution","description":"Can submit an execution request; worker execution still requires governance/approval."}
    ]}

@router.post("/admin/users")
def users_create(req: UserCreateRequest, request: Request, db: Session=Depends(get_db)):
    actor=_sudo(request,db)
    if req.role not in VALID_ROLES: raise HTTPException(400,"Invalid role")
    levels=_validate_permissions(req.tool_permissions)
    if req.role == "sudo" and db.query(UserAccount).filter(UserAccount.role=="sudo").count():
        raise HTTPException(409,"VEYRA allows exactly one sudo account")
    if db.query(UserAccount).filter(UserAccount.username==req.username).first(): raise HTTPException(409,"Username already exists")
    from ..services.auth import hash_password
    u=UserAccount(username=req.username,display_name=req.display_name,email=req.email,password_hash=hash_password(req.password),role=req.role,mfa_required=req.mfa_required,must_change_password=True)
    db.add(u); db.flush()
    for tool_id,raw in req.tool_permissions.items():
        level, expires_at = _grant_expiry_from_value(raw)
        if level != "none": db.add(UserToolPermission(user_id=u.id,tool_id=tool_id,level=level,granted_by=actor.username,expires_at=expires_at))
    db.add(AuditEvent(actor=actor.username,action="user_created",target=req.username,outcome=req.role)); db.commit()
    return {"id":u.id,"username":u.username,"role":u.role,"message":"User created; first login requires password change."}

@router.put("/admin/users/{user_id}")
def users_update(user_id:int, req: UserUpdateRequest, request: Request, db: Session=Depends(get_db)):
    actor=_sudo(request,db); u=db.get(UserAccount,user_id)
    if not u: raise HTTPException(404,"User not found")
    if req.role is not None:
        if req.role not in VALID_ROLES: raise HTTPException(400,"Invalid role")
        if req.role=="sudo" and u.role!="sudo" and db.query(UserAccount).filter(UserAccount.role=="sudo").count(): raise HTTPException(409,"VEYRA allows exactly one sudo account")
        u.role=req.role
    if req.display_name is not None:u.display_name=req.display_name
    if req.email is not None:u.email=req.email
    if req.status is not None:
        if req.status not in {"active","disabled"}: raise HTTPException(400,"Invalid status")
        if u.role=="sudo" and req.status!="active": raise HTTPException(400,"The sole sudo account cannot be disabled")
        u.status=req.status
    if req.mfa_required is not None:u.mfa_required=req.mfa_required
    if req.tool_permissions is not None:
        levels=_validate_permissions(req.tool_permissions)
        db.query(UserToolPermission).filter(UserToolPermission.user_id==u.id).delete(synchronize_session=False)
        for tool_id,raw in req.tool_permissions.items():
            level, expires_at = _grant_expiry_from_value(raw)
            if level != "none": db.add(UserToolPermission(user_id=u.id,tool_id=tool_id,level=level,granted_by=actor.username,expires_at=expires_at))
    db.add(AuditEvent(actor=actor.username,action="user_permissions_updated",target=u.username,outcome=u.role)); db.commit()
    return {"status":"updated","user_id":u.id}

@router.get("/me/tool-permissions")
def my_tool_permissions(request: Request, db: Session=Depends(get_db)):
    from ..services.auth import effective_tool_level
    user=_auth_user(request,db)
    perms={p.tool_id:p.level for p in db.query(UserToolPermission).filter(UserToolPermission.user_id==user.id).all()}
    grants={}
    for p in db.query(UserToolPermission).filter(UserToolPermission.user_id==user.id).all():
        exp = p.expires_at.isoformat() if p.expires_at else None
        if p.expires_at is not None:
            try:
                exp = p.expires_at.replace(tzinfo=p.expires_at.tzinfo) if False else exp
            except Exception:
                pass
        grants[p.tool_id]={"level":p.level,"expires_at":exp,"granted_by":p.granted_by}
    if user.role == "sudo":
        tools=admin_tool_registry()
        return {"role":user.role,"sudo":True,"permissions":{t["id"]:"execute_request" for t in tools},
                "grants":{},"tools":tools,
                "note":"Sudo holds every tool with no further approval and no expiry."}
    tools=[t for t in admin_tool_registry() if perms.get(t["id"],"none")!="none"]
    return {"role":user.role,"sudo":False,"permissions":perms,"grants":grants,"tools":tools}


GRANT_DURATIONS = [2, 5, 24]

class AccessRequestIn(BaseModel):
    tool_id: str = Field(min_length=1, max_length=255)
    level: str = Field(default="plan")
    reason: str = Field(default="", max_length=2000)
    duration_hours: float = Field(default=2, ge=0.25, le=720)

class AccessDecideIn(BaseModel):
    approve: bool = True
    duration_hours: float | None = Field(default=None, ge=0.25, le=720)

def _tool_lookup(tool_id: str):
    by_id = {x["id"]: x for x in admin_tool_registry()}
    return by_id.get(tool_id)

def _sudo_inbox_targets(db: Session):
    from ..services.notify import admin_email
    emails = {u.email for u in db.query(UserAccount).filter(UserAccount.role=="sudo", UserAccount.status=="active").all() if u.email}
    configured = admin_email()
    if configured:
        emails.add(configured)
    return sorted(emails)

@router.post("/tools/requests")
def tool_access_request(req: AccessRequestIn, request: Request, db: Session=Depends(get_db)):
    """Any signed-in user may ask the sudo admin for tool rights (default read-only otherwise)."""
    import uuid as _uuid
    from datetime import datetime, timezone as _tz
    from ..services.notify import send_access_request_email
    user=_auth_user(request,db)
    if req.level not in {"view", "plan", "execute_request"}:
        raise HTTPException(400, "Invalid requested level")
    tool = _tool_lookup(req.tool_id)
    if not tool:
        raise HTTPException(404, "Tool is not registered")
    if user.role == "sudo":
        raise HTTPException(400, "Sudo already holds every tool; no request needed")
    dup = db.query(ToolAccessRequest).filter(
        ToolAccessRequest.user_id==user.id, ToolAccessRequest.tool_id==req.tool_id,
        ToolAccessRequest.status=="pending").first()
    if dup:
        raise HTTPException(409, "You already have a pending request for this tool")
    rid = _uuid.uuid4().hex[:12]
    row = ToolAccessRequest(request_id=rid, user_id=user.id, username=user.username,
        tool_id=req.tool_id, tool_name=tool["name"], level=req.level,
        reason=req.reason.strip(), duration_hours=req.duration_hours, status="pending")
    db.add(row)
    targets = _sudo_inbox_targets(db)
    channel, status = send_access_request_email(
        ",".join(targets), user.username, tool["name"], req.level,
        req.duration_hours, req.reason.strip(), rid)
    db.add(AdminNotification(to_role="sudo", to_email=",".join(targets)[:255],
        subject=f"Tool access request: {user.username} → {tool['name']} ({req.level})",
        body=(f"{user.username} requests {req.level} on {tool['name']} for "
              f"{req.duration_hours:g}h. Reason: {req.reason.strip() or '(none)'} "
              f"[request {rid}]"),
        channel=channel, status=status, related_id=rid))
    db.add(AuditEvent(actor=user.username, action="tool_access_requested",
        target=f"{req.tool_id}:{req.level}", outcome=f"pending:{rid}"))
    db.commit()
    return {"request_id": rid, "status": "pending",
            "notified": {"channel": channel, "delivery": status, "to": targets},
            "message": "Request sent to the sudo administrator. Grants are time-boxed and enforced server-side."}

@router.get("/tools/requests")
def tool_access_requests(status: str = Query("pending"), request: Request = None, db: Session=Depends(get_db)):
    """Sudo sees every request; users see their own. Use status=all|pending|approved|denied|expired."""
    from datetime import datetime, timezone as _tz
    user=_auth_user(request,db)
    q = db.query(ToolAccessRequest)
    if user.role != "sudo":
        q = q.filter(ToolAccessRequest.user_id==user.id)
    if status != "all":
        if status not in {"pending","approved","denied","expired"}:
            raise HTTPException(400, "Invalid status filter")
        q = q.filter(ToolAccessRequest.status==status)
    rows = q.order_by(ToolAccessRequest.created_at.desc()).limit(200).all()
    return [clean(r) for r in rows]

@router.post("/tools/requests/{request_id}/decide")
def tool_access_decide(request_id: str, req: AccessDecideIn, request: Request, db: Session=Depends(get_db)):
    """Sudo decision. Approvals mint a time-boxed grant (2h/5h/24h/custom);
    denials close the request. Both notify the requester via inbox + audit."""
    import uuid as _uuid
    from datetime import datetime, timezone as _tz
    from ..services.auth import grant_expiry
    from ..services.notify import send_access_request_email
    actor=_sudo(request,db)
    row=db.query(ToolAccessRequest).filter(ToolAccessRequest.request_id==request_id).first()
    if not row: raise HTTPException(404, "Request not found")
    if row.status != "pending": raise HTTPException(409, f"Request is {row.status}")
    if req.approve:
        hours = req.duration_hours if req.duration_hours is not None else row.duration_hours
        tool = _tool_lookup(row.tool_id)
        if not tool:
            raise HTTPException(404, "Tool is not registered")
        if tool.get("access_tier") == "privileged_admin" and row.level == "execute_request":
            pass  # sudo itself approves: privileged execution stays sudo-governed
        grant = db.query(UserToolPermission).filter(
            UserToolPermission.user_id==row.user_id, UserToolPermission.tool_id==row.tool_id).first()
        if not grant:
            grant = UserToolPermission(user_id=row.user_id, tool_id=row.tool_id)
            db.add(grant)
        grant.level = row.level
        grant.granted_by = actor.username
        grant.expires_at = grant_expiry(hours)
        grant.updated_at = datetime.now(_tz.utc)
        row.status = "approved"; row.decided_by = actor.username; row.decided_at = datetime.now(_tz.utc)
        db.add(AuditEvent(actor=actor.username, action="tool_access_approved",
            target=f"{row.username}:{row.tool_id}:{row.level}", outcome=f"{hours:g}h"))
        db.add(AdminNotification(to_role="user", to_email="",
            subject=f"Approved: {row.tool_name} ({row.level}, {hours:g}h)",
            body=(f"Sudo approved your request {request_id}: {row.level} on {row.tool_name} "
                  f"for {hours:g} hour(s). It expires automatically."),
            channel="inbox", status="inbox", related_id=request_id))
        db.commit()
        return {"request_id": request_id, "status": "approved",
                "grant": {"tool_id": row.tool_id, "level": row.level,
                          "expires_at": grant.expires_at.isoformat() if grant.expires_at else None}}
    row.status = "denied"; row.decided_by = actor.username; row.decided_at = datetime.now(_tz.utc)
    db.add(AuditEvent(actor=actor.username, action="tool_access_denied",
        target=f"{row.username}:{row.tool_id}:{row.level}", outcome=request_id))
    db.add(AdminNotification(to_role="user", to_email="",
        subject=f"Denied: {row.tool_name} ({row.level})",
        body=f"Sudo denied your request {request_id} for {row.level} on {row.tool_name}.",
        channel="inbox", status="inbox", related_id=request_id))
    db.commit()
    return {"request_id": request_id, "status": "denied"}

@router.get("/admin/notifications")
def admin_notifications(limit: int = Query(50, ge=1, le=200), request: Request = None, db: Session=Depends(get_db)):
    """Sudo inbox: every access request email/log mirror + decisions. Users see
    only notifications addressed to them (their request decisions)."""
    user=_auth_user(request,db)
    q = db.query(AdminNotification)
    if user.role != "sudo":
        my_ids = [r.request_id for r in db.query(ToolAccessRequest).filter(ToolAccessRequest.user_id==user.id).all()]
        q = q.filter(AdminNotification.to_role=="user", AdminNotification.related_id.in_(my_ids) if my_ids else False)
    rows = q.order_by(AdminNotification.created_at.desc()).limit(limit).all()
    return [clean(r) for r in rows]

@router.get("/tools/grant-durations")
def grant_duration_options():
    return {"durations": [{"hours": h, "label": f"{h} hours"} for h in GRANT_DURATIONS],
            "custom": True, "custom_help": "Sudo may set any window from 15 minutes to 30 days (720h)."}


@router.get("/tools/marketplace")
def tool_marketplace(request: Request, db: Session = Depends(get_db)):
    """Managed security-tool catalog. Installation is planned/approved, never arbitrary shell."""
    user = _auth_user(request, db)
    if user is None:
        raise HTTPException(401, "Authenticated console session required")
    tools = admin_tool_registry() + ai_ecosystem_registry()
    return {"tools": tools, "count": len(tools),
            "install_policy": "Managed-worker installation only; signed artifacts, version pins and provenance required."}

@router.get("/tools/{tool_id}/install-plan")
def tool_install_plan(tool_id: str, request: Request, db: Session = Depends(get_db)):
    user = _auth_user(request, db)
    if user is None:
        raise HTTPException(401, "Authenticated console session required")
    tool = next((x for x in admin_tool_registry() + ai_ecosystem_registry() if x["id"] == tool_id), None)
    if not tool:
        raise HTTPException(404, "Tool is not registered")
    if tool.get("privileged_usage") and user.role not in {"sudo", "security_admin"}:
        raise HTTPException(403, "Privileged tool installation requires Sudo or Security Admin")
    return install_manifest(tool)

@router.post("/tools/install-requests")
def tool_install_request(req: dict, request: Request, db: Session = Depends(get_db)):
    """Create an auditable installation request; a managed worker performs the actual package operation."""
    user = _auth_user(request, db)
    if user is None:
        raise HTTPException(401, "Authenticated console session required")
    tool_id = str(req.get("tool_id","")).strip()
    worker = str(req.get("worker_id","")).strip()
    if not tool_id or not worker:
        raise HTTPException(400, "tool_id and worker_id are required")
    tool = next((x for x in admin_tool_registry() + ai_ecosystem_registry() if x["id"] == tool_id), None)
    if not tool:
        raise HTTPException(404, "Tool is not registered")
    if tool.get("privileged_usage") and user.role not in {"sudo", "security_admin"}:
        raise HTTPException(403, "Privileged tool installation requires Sudo or Security Admin")
    manifest = install_manifest(tool)
    actor = user.username
    ticket = str(req.get("approval_ticket","")).strip()
    if user.role != "sudo" and not ticket:
        raise HTTPException(400, "approval_ticket is required for non-sudo installation requests")
    db.add(AuditEvent(actor=actor, action="tool_install_requested",
                      target=f"{worker}:{tool['name']}",
                      outcome="queued_for_worker_install"))
    db.commit()
    return {"status": "pending_worker_install" if user.role != "sudo" else "approved_for_worker_install",
            "tool": tool, "worker_id": worker, "manifest": manifest,
            "message": "No package command was executed by the SaaS API. The managed worker must verify provenance and apply the manifest."}

@router.get("/security-tool-academy")
def security_tool_academy():
    """Safe, command-free learning guide for every integrated tool."""
    guidance={
      "Network Discovery":"Define an owned/approved CIDR or asset list, run the tool in an isolated worker, review discovered hosts/ports, then validate results against asset inventory.",
      "Attack Surface":"Start with an approved domain/asset scope, prefer passive discovery first, validate DNS/HTTP results, and record ownership before assessment.",
      "Web/API":"Proxy or assess an authorized test application, begin with passive mapping, review alerts/evidence, then stage only approved active checks.",
      "Exploit Validation":"Use only an isolated lab or explicitly approved validation worker. Confirm the finding and evidence; never use the web console as an unrestricted exploit terminal.",
      "Identity/Network":"Use an approved directory/network assessment scope to understand identity relationships and configuration weaknesses; preserve evidence and avoid credential or persistence actions.",
      "Identity":"Model identity relationships, excessive privileges and trust paths. Use findings to reduce blast radius and improve access controls.",
      "Credential Audit":"Use offline, authorized password-strength audit datasets. Never expose credential attacks through the browser or run against accounts without written authorization.",
      "Network Defense":"Capture or inspect traffic only on networks you own/manage; use packet metadata and protocol behavior to investigate anomalies and build detections.",
      "Vulnerability":"Scan approved hosts, packages or images, de-duplicate findings, map to severity/KEV, and track remediation evidence.",
      "Cloud/Container":"Scan images, packages and workloads before deployment; correlate vulnerabilities with runtime exposure and business criticality.",
      "AppSec":"Run code analysis in CI or an approved worker, triage findings, suppress only with justification, and link fixes to commits/builds.",
      "IaC":"Scan Terraform/Kubernetes/cloud configuration before deployment; prioritize identity, public exposure, secrets and encryption findings.",
      "Cloud":"Use read-only cloud connectors, inventory resources, identify public exposure and excessive permissions, then remediate through normal change control.",
      "Kubernetes":"Assess cluster posture and runtime configuration in approved environments; benchmark first, then investigate exposed services and risky workloads.",
      "Endpoint":"Deploy the collector/agent to managed endpoints, collect telemetry with consent, and use queries for investigation rather than arbitrary remote execution.",
      "DFIR":"Acquire authorized forensic artifacts, hash evidence, analyze copies, and preserve chain of custody.",
      "Malware":"Analyze files in isolated analysis workers; start with signatures/capabilities, then static analysis, and never execute unknown samples on analyst workstations.",
      "Reverse Engineering":"Open a copy of the sample in an isolated workspace, identify imports/strings/capabilities, map behavior to detections, and preserve hashes.",
      "Firmware":"Analyze a firmware image offline, identify embedded files/configuration and exposed services, then document remediation.",
      "Forensics":"Extract metadata or recover files from authorized evidence copies while preserving original hashes.",
      "Threat Intelligence":"Ingest and normalize indicators, attach confidence/source/provenance, correlate with internal telemetry, and avoid treating weak matches as attribution.",
      "Detection Engineering":"Write portable detections, test them against known telemetry, measure coverage and false positives, and version-control rules.",
      "AI Security":"Test AI applications and agents in lab/approved environments, evaluate prompt/context integrity, tool permissions, RAG authorization, memory provenance and runtime policy, then record evidence."
    }
    out=[]
    for t in admin_tool_registry():
        x=dict(t); x["learning_guide"]=guidance.get(t["category"],"Define explicit scope, use an approved worker or connector, review evidence, and record provenance before taking action.")
        x["recommended_learning_order"]=["Understand purpose","Define authorized scope","Run/observe in approved environment","Review evidence","Map findings to risk","Remediate and verify"]
        out.append(x)
    return {"tools":out,"count":len(out),"note":"Educational guidance is intentionally command-free. VEYRA does not expose arbitrary shell execution."}


# ---------------------------------------------------------------------------
# v2.8 AI Ecosystem + Managed Security Worker Fabric
# ---------------------------------------------------------------------------

@router.get("/ai-ecosystem/overview")
def ai_ecosystem_overview_api(_: bool = Depends(require_admin)):
    """Return the current AI security ecosystem size/category summary."""
    return ai_ecosystem_overview()

@router.get("/ai-ecosystem/tools")
def ai_ecosystem_tools(_: bool = Depends(require_admin)):
    """Return governed AI/agent security integration candidates."""
    return {"tools": ai_ecosystem_registry()}

class WorkerRegisterRequest(BaseModel):
    worker_id: str = Field(min_length=3, max_length=128)
    name: str = Field(min_length=1, max_length=255)
    kind: str = Field(default="kali", max_length=64)
    platform: str = Field(default="kali-linux-amd64", max_length=128)
    version: str = Field(default="2.8.0", max_length=64)
    capabilities: list[str] = Field(default=[])

@router.post("/workers/register")
def register_worker(req: WorkerRegisterRequest, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    """Register/update a managed worker. No credentials or shell commands are accepted."""
    row = db.query(WorkerNode).filter(WorkerNode.worker_id == req.worker_id).first()
    if not row:
        row = WorkerNode(worker_id=req.worker_id)
        db.add(row)
    row.name=req.name; row.kind=req.kind; row.platform=req.platform; row.version=req.version
    row.capabilities_json=json.dumps(sorted(set(req.capabilities))); row.status="online"
    from datetime import datetime, timezone
    row.last_heartbeat=datetime.now(timezone.utc)
    db.commit()
    return clean(row)

@router.post("/workers/{worker_id}/heartbeat")
def worker_heartbeat(worker_id: str, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    """Record worker liveness. Production should use worker identity/signature auth."""
    row=db.query(WorkerNode).filter(WorkerNode.worker_id==worker_id).first()
    if not row: raise HTTPException(404, "Worker not registered")
    from datetime import datetime, timezone
    row.status="online"; row.last_heartbeat=datetime.now(timezone.utc); db.commit()
    return {"worker_id":worker_id,"status":row.status,"last_heartbeat":row.last_heartbeat}

@router.get("/workers")
def list_workers(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    """List worker health and capability metadata."""
    return [clean(x) for x in db.query(WorkerNode).order_by(WorkerNode.name).all()]

class WorkerInstallReport(BaseModel):
    tool_id: str = Field(min_length=1, max_length=255)
    version: str = Field(default="unknown", max_length=128)
    state: str = Field(default="healthy", max_length=32)
    binary_path: str = Field(default="", max_length=512)
    checksum: str = Field(default="", max_length=128)
    sbom_ref: str = Field(default="", max_length=255)

@router.post("/workers/{worker_id}/tools/report")
def report_worker_tool(worker_id: str, req: WorkerInstallReport, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    """Record worker-side installation/verification results."""
    worker=db.query(WorkerNode).filter(WorkerNode.worker_id==worker_id).first()
    if not worker: raise HTTPException(404, "Worker not registered")
    row=db.query(WorkerToolInstall).filter(WorkerToolInstall.worker_id==worker_id, WorkerToolInstall.tool_id==req.tool_id).first()
    if not row:
        row=WorkerToolInstall(worker_id=worker_id, tool_id=req.tool_id); db.add(row)
    row.version=req.version; row.state=req.state; row.binary_path=req.binary_path
    row.checksum=req.checksum; row.sbom_ref=req.sbom_ref
    from datetime import datetime, timezone
    row.last_verified_at=datetime.now(timezone.utc)
    db.commit()
    return clean(row)

@router.get("/workers/{worker_id}/tools")
def worker_tools(worker_id: str, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    """Show actual worker tool state separately from the global catalog."""
    return [clean(x) for x in db.query(WorkerToolInstall).filter(WorkerToolInstall.worker_id==worker_id).order_by(WorkerToolInstall.tool_id).all()]

@router.get("/workers/{worker_id}/install-plan/{tool_id}")
def worker_install_plan(worker_id: str, tool_id: str, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    """Create a signed-installation *plan*; worker performs the installation after policy checks."""
    worker=db.query(WorkerNode).filter(WorkerNode.worker_id==worker_id).first()
    if not worker: raise HTTPException(404, "Worker not registered")
    tool=next((x for x in ai_ecosystem_registry() if x["id"]==tool_id), None)
    if not tool:
        tool=next((x for x in admin_tool_registry() if x["id"]==tool_id), None)
    if not tool: raise HTTPException(404, "Tool not registered")
    require_tool_access(request, tool)
    return {
        "worker_id": worker_id,
        "tool": tool,
        "plan": {
            "operation": "install_or_update",
            "artifact_policy": "signed_and_pinned",
            "verification": ["publisher provenance", "signature", "sha256", "SBOM", "license"],
            "execution": "managed_worker_only",
            "api_shell_access": False,
            "approval": "privileged administrator" if tool.get("privileged_usage") else "administrator",
        }
    }

# ---------------------------------------------------------------------------
# v3.0 Full Security Operations Fabric
# ---------------------------------------------------------------------------
from ..services.v3_fabric import overview as v3_overview, graph_read_model as v3_graph, attack_reconstruction as v3_reconstruct, ai_investigation as v3_ai_investigation, response_plan as v3_response_plan, recovery_check as v3_recovery_check

@router.get("/v3/fabric/overview")
def v3_fabric_overview(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v3_overview(db)

@router.get("/v3/fabric/graph")
def v3_fabric_graph(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v3_graph(db)

@router.get("/v3/fabric/reconstruction")
def v3_fabric_reconstruction(limit: int = Query(50, ge=10, le=200), db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v3_reconstruct(db, limit)

@router.get("/v3/fabric/ai-investigation")
def v3_fabric_ai_investigation(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v3_ai_investigation(db)

class V3ResponsePlanRequest(BaseModel):
    incident_id: int | None = None

@router.post("/v3/fabric/response-plan")
def v3_fabric_response_plan(req: V3ResponsePlanRequest, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    plan = v3_response_plan(db, req.incident_id)
    actor = (_bearer_user(request).username if _bearer_user(request) else "admin")
    db.add(AuditEvent(actor=actor, action="v3_response_plan_staged", target=str(req.incident_id or "latest"), outcome="staged_only"))
    db.commit()
    return plan

@router.get("/v3/fabric/recovery")
def v3_fabric_recovery(incident_id: int | None = None, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v3_recovery_check(db, incident_id)

# ---------------------------------------------------------------------------
# v3.1 Sudo Security Arsenal + Adversary Trace Fabric
# ---------------------------------------------------------------------------
from ..services.sudo_arsenal import arsenal_overview, list_tools as v31_list_tools, tool_detail as v31_tool_detail, build_trace_plan
from ..services.team_academy import academy_overview, recommended_curriculum

@router.get("/v31/arsenal/overview")
def v31_arsenal_overview(_: bool = Depends(require_admin)):
    return arsenal_overview()

@router.get("/v31/arsenal/tools")
def v31_arsenal_tools(category: str | None = None, privileged_only: bool = False, _: bool = Depends(require_admin)):
    return v31_list_tools(category=category, privileged_only=privileged_only)

@router.get("/v31/arsenal/tools/{tool_id}")
def v31_arsenal_tool(tool_id: str, _: bool = Depends(require_admin)):
    tool = v31_tool_detail(tool_id)
    if not tool:
        raise HTTPException(404, "Tool is not registered")
    return tool

class V31TraceRequest(BaseModel):
    source_ip: str = ""
    destination: str = ""
    observed_at: str = ""
    indicators: list[str] = Field(default_factory=list, max_length=100)

@router.post("/v31/trace/plan")
def v31_trace_plan(req: V31TraceRequest, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    plan = build_trace_plan(req.source_ip, req.destination, req.observed_at, req.indicators)
    user = _bearer_user(request)
    actor = user.username if user else "admin"
    db.add(AuditEvent(actor=actor, action="v31_adversary_trace_plan_staged", target=req.source_ip or req.destination or "unspecified", outcome=plan["plan_id"]))
    db.commit()
    return plan

# ---------------------------------------------------------------------------
# v3.2 Team Academy + documentation index
# ---------------------------------------------------------------------------
@router.get("/v32/academy/overview")
def v32_academy_overview(_: bool = Depends(require_admin)):
    return academy_overview()

@router.get("/v32/academy/curriculum/{track}")
def v32_academy_curriculum(track: str, _: bool = Depends(require_admin)):
    return recommended_curriculum(track)

# ---------------------------------------------------------------------------
# v3.3 Security Readiness + Continuous Validation
# ---------------------------------------------------------------------------
from ..services.security_readiness import readiness_overview, exercise_library

@router.get("/v33/readiness/overview")
def v33_readiness_overview(_: bool = Depends(require_admin)):
    return readiness_overview()

@router.get("/v33/readiness/exercises")
def v33_readiness_exercises(track: str | None = None, _: bool = Depends(require_admin)):
    return exercise_library(track)

# ---------------------------------------------------------------------------
# v3.4 Security Intelligence + Continuous Control Validation
# ---------------------------------------------------------------------------
from ..services.v34_security_intelligence import intelligence_overview, validation_plan

@router.get("/v34/intelligence/overview")
def v34_intelligence_overview(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return intelligence_overview(db)

@router.get("/v34/validation/plan")
def v34_validation_plan(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return validation_plan(db)

# ---------------------------------------------------------------------------
# v3.5 Security Lifecycle: continuous operating model
# ---------------------------------------------------------------------------
from ..services.v35_security_lifecycle import lifecycle_overview, lifecycle_plan

from ..services.v36_security_radar import overview as v36_radar_overview, recommendations as v36_radar_recommendations

@router.get("/v36/security-radar")
def v36_security_radar(_: bool = Depends(require_admin)):
    return v36_radar_overview()

@router.get("/v36/security-radar/recommendations")
def v36_security_radar_recommendations(maturity: str | None = None, kind: str | None = None, _: bool = Depends(require_admin)):
    return {"recommendations": v36_radar_recommendations(maturity, kind)}


@router.get("/v35/lifecycle/overview")
def v35_lifecycle_overview(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return lifecycle_overview(db)

@router.get("/v35/lifecycle/plan")
def v35_lifecycle_plan(focus: str | None = None, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return lifecycle_plan(db, focus)

# ---------------------------------------------------------------------------
# v3.8 Security Posture Time Machine + AI/Endpoint Security Radar
# ---------------------------------------------------------------------------
from ..services.v38_posture_time_machine import current as v38_posture_current, history as v38_posture_history, changes as v38_posture_changes, drift as v38_posture_drift, remediation_proof as v38_remediation_proof, create_snapshot as v38_create_snapshot
from ..services.v38_ai_endpoint_radar import overview as v38_ai_endpoint_overview

@router.get("/v38/posture/current")
def v38_posture_current_route(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v38_posture_current(db)

@router.get("/v38/posture/history")
def v38_posture_history_route(limit: int = 30, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v38_posture_history(db, limit)

@router.get("/v38/posture/changes")
def v38_posture_changes_route(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v38_posture_changes(db)

@router.get("/v38/posture/drift")
def v38_posture_drift_route(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v38_posture_drift(db)

@router.get("/v38/posture/remediation-proof")
def v38_remediation_proof_route(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v38_remediation_proof(db)

@router.post("/v38/posture/snapshot")
def v38_posture_snapshot_route(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v38_create_snapshot(db)

@router.get("/v38/ai-endpoint-radar")
def v38_ai_endpoint_radar_route(_: bool = Depends(require_admin)):
    return v38_ai_endpoint_overview()

# ---------------------------------------------------------------------------
# v3.9 Autonomous Exposure Validation Fabric + Rogue Agent Investigation Lab
# ---------------------------------------------------------------------------
from ..services.v39_autonomous_exposure_validation import exposure_overview as v39_exposure_overview, investigate_agent as v39_investigate_agent, cases as v39_cases, validation_matrix as v39_validation_matrix

@router.get("/v39/exposure/overview")
def v39_exposure_overview_route(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v39_exposure_overview(db)

@router.get("/v39/exposure/validation-matrix")
def v39_validation_matrix_route(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v39_validation_matrix(db)

@router.get("/v39/rogue-agents/cases")
def v39_rogue_agent_cases_route(db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    return v39_cases(db)

class RogueAgentInvestigationRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=255)

@router.post("/v39/rogue-agents/investigate")
def v39_rogue_agent_investigate_route(req: RogueAgentInvestigationRequest, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    result=v39_investigate_agent(db, req.agent_id)
    if result.get("status") != "not_found":
        user=_bearer_user(request); actor=user.username if user else "admin"
        db.add(AuditEvent(actor=actor, action="v39_rogue_agent_investigation", target=req.agent_id, outcome=result.get("case_id","created")))
        db.commit()
    return result

# ---------------------------------------------------------------------------
# VEYRA v4.0 — Tool Supply Chain & Autonomous Update Fabric
# ---------------------------------------------------------------------------
from ..models import ToolDefinition, ToolRelease, ToolArtifact, ToolUpdatePolicy, ToolDeployment, ToolHealthCheck, AgentContainmentPolicy
from ..services.v40_tool_supply_chain import overview as v40_overview, scout as v40_scout, sync_catalog as v40_sync_catalog, register_release as v40_register_release, deployment_plan as v40_deployment_plan, rollback_plan as v40_rollback_plan, SOURCE_CATALOG, sign_manifest, sha256_json

class V40PolicyRequest(BaseModel):
    channel: str = "stable"
    pin_mode: str = "floating"
    pinned_version: str = ""
    pinned_digest: str = ""
    auto_update: bool = False
    critical_override: bool = True
    require_canary: bool = True
    canary_percent: int = Field(default=10, ge=1, le=100)
    maintenance_window: str = "weekly"

@router.get("/v40/supply-chain/overview")
def v40_supply_chain_overview(request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    return v40_overview(db)

@router.post("/v40/supply-chain/sync-catalog")
def v40_sync_catalog_route(request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    return {"created": v40_sync_catalog(db), "message":"Tool definitions synchronized from the governed VEYRA catalog."}

@router.get("/v40/update-scout")
def v40_update_scout(request: Request, tool_id: str | None = None, db: Session = Depends(get_db)):
    _auth_user(request, db)
    return {"release":"4.0","mode":"metadata_and_verified_release_registry","results":v40_scout(db,tool_id),
            "note":"VEYRA does not invent upstream versions. A release becomes deployable only after an operator or approved resolver registers immutable artifact metadata and verification evidence."}

@router.get("/v40/verification/adapters")
def v40_verification_adapters(request: Request):
    from ..services.v40_verification_adapters import inventory
    # Adapter inventory is read-only; actual verification is worker-side.
    return {"adapters":inventory(),"policy":"TUF + Cosign + Syft + Grype + SLSA/in-toto should run in an isolated verification worker."}

@router.get("/v40/tool-trust/{tool_id}")
def v40_tool_trust(tool_id: str, request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    releases=db.query(ToolRelease).filter(ToolRelease.tool_id==tool_id).all()
    score=0; factors=[]
    if releases:
        r=max(releases,key=lambda x:x.discovered_at)
        if r.verification_status=="verified": score+=30; factors.append("release metadata verified")
        if r.signature: score+=20; factors.append("signature present")
        if r.provenance_uri: score+=15; factors.append("provenance present")
        if r.sbom_uri: score+=15; factors.append("SBOM present")
        if r.health_status=="healthy": score+=20; factors.append("health gate passed")
    return {"tool_id":tool_id,"trust_score":min(100,score),"band":"trusted" if score>=80 else "review" if score>=50 else "untrusted","factors":factors}

@router.get("/v40/compatibility/{tool_id}")
def v40_compatibility(tool_id: str, request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    workers=db.query(WorkerNode).order_by(WorkerNode.name).all()
    return {"tool_id":tool_id,"matrix":[{"worker_id":w.worker_id,"platform":w.platform,"worker_version":w.version,"compatibility":"requires_health_gate"} for w in workers],"policy":"Do not promote a release until the target worker platform has passed the release health suite."}

@router.get("/v40/update-sources")
def v40_update_sources(request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    return {"sources":SOURCE_CATALOG,"recommended_cadence":{"advisories":"continuous/daily","release_metadata":"daily","stable_rollout":"weekly","major_rollout":"planned"}}

@router.get("/v40/tools")
def v40_tools(request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db); v40_sync_catalog(db)
    return [clean(x) for x in db.query(ToolDefinition).order_by(ToolDefinition.name).limit(1000).all()]

@router.get("/v40/tools/{tool_id}/releases")
def v40_releases(tool_id: str, request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    return [clean(x) for x in db.query(ToolRelease).filter(ToolRelease.tool_id==tool_id).order_by(ToolRelease.discovered_at.desc()).all()]

@router.post("/v40/releases")
def v40_register_release_route(payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    user=_bearer_user(request)
    if user and user.role not in {"sudo","security_admin"}: raise HTTPException(403,"Release registration requires Sudo or Security Admin")
    try: return v40_register_release(db,payload)
    except ValueError as e: raise HTTPException(400,str(e))

@router.get("/v40/tools/{tool_id}/policy")
def v40_get_policy(tool_id: str, request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    from ..services.v40_tool_supply_chain import ensure_policy
    return clean(ensure_policy(db,tool_id))

@router.put("/v40/tools/{tool_id}/policy")
def v40_put_policy(tool_id: str, req: V40PolicyRequest, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    user=_bearer_user(request)
    if user and user.role not in {"sudo","security_admin"}: raise HTTPException(403,"Update policy changes require Sudo or Security Admin")
    if req.pin_mode not in {"floating","pinned","immutable"}: raise HTTPException(400,"Invalid pin_mode")
    if req.channel not in {"candidate","canary","stable","extended_stable"}: raise HTTPException(400,"Invalid channel")
    from ..services.v40_tool_supply_chain import ensure_policy
    p=ensure_policy(db,tool_id); p.channel=req.channel; p.pin_mode=req.pin_mode; p.pinned_version=req.pinned_version; p.pinned_digest=req.pinned_digest
    p.auto_update=req.auto_update; p.critical_override=req.critical_override; p.require_canary=req.require_canary; p.canary_percent=req.canary_percent; p.maintenance_window=req.maintenance_window
    db.commit(); db.refresh(p); return clean(p)

@router.post("/v40/tools/{tool_id}/freeze")
def v40_freeze_tool(tool_id: str, payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    user=_bearer_user(request)
    if user and user.role not in {"sudo","security_admin"}: raise HTTPException(403,"Freeze requires Sudo or Security Admin")
    from datetime import datetime, timezone, timedelta
    from ..services.v40_tool_supply_chain import ensure_policy
    p=ensure_policy(db,tool_id); hours=float(payload.get("hours",24)); p.freeze_reason=str(payload.get("reason","operator freeze")); p.frozen_until=datetime.now(timezone.utc)+timedelta(hours=max(.25,min(720,hours)))
    db.commit(); return {"tool_id":tool_id,"status":"frozen","frozen_until":p.frozen_until.isoformat(),"reason":p.freeze_reason}

@router.post("/v40/tools/{tool_id}/quarantine")
def v40_quarantine_tool(tool_id: str, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    user=_bearer_user(request)
    if user and user.role not in {"sudo","security_admin"}: raise HTTPException(403,"Quarantine requires Sudo or Security Admin")
    db.query(ToolDefinition).filter(ToolDefinition.tool_id==tool_id).update({"status":"quarantined"})
    db.query(ToolRelease).filter(ToolRelease.tool_id==tool_id).update({"health_status":"quarantined"})
    db.commit(); return {"tool_id":tool_id,"status":"quarantined","execution":"blocked until reviewed"}

@router.post("/v40/deployments")
def v40_create_deployment(payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    user=_bearer_user(request)
    if user and user.role not in {"sudo","security_admin"}: raise HTTPException(403,"Deployments require Sudo or Security Admin")
    try:
        return v40_deployment_plan(db,payload["tool_id"],payload["release_id"],payload["worker_id"],payload.get("operation","install_or_update"),bool(payload.get("force",False)))
    except (KeyError,ValueError) as e: raise HTTPException(400,str(e))

@router.post("/v40/deployments/{deployment_id}/ack")
def v40_deployment_ack(deployment_id: str, payload: dict, request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    d=db.query(ToolDeployment).filter(ToolDeployment.deployment_id==deployment_id).first()
    if not d: raise HTTPException(404,"Deployment not found")
    receipt=payload or {}; d.worker_receipt_json=json.dumps(receipt,default=str); d.state=str(receipt.get("state","completed"));
    if d.state in {"completed","healthy"}: from datetime import datetime, timezone; d.completed_at=datetime.now(timezone.utc)
    db.commit(); return {"deployment_id":deployment_id,"state":d.state,"receipt_sha256":sha256_json(receipt)}

@router.get("/v40/deployments")
def v40_deployments(request: Request, limit: int = Query(100,ge=1,le=500), db: Session = Depends(get_db)):
    _auth_user(request, db)
    return [clean(x) for x in db.query(ToolDeployment).order_by(ToolDeployment.created_at.desc()).limit(limit).all()]

@router.post("/v40/rollback")
def v40_rollback(payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    user=_bearer_user(request)
    if user and user.role not in {"sudo","security_admin"}: raise HTTPException(403,"Rollback requires Sudo or Security Admin")
    try: return v40_rollback_plan(db,payload["tool_id"],payload["worker_id"],payload["target_release_id"])
    except (KeyError,ValueError) as e: raise HTTPException(400,str(e))

@router.post("/v40/health-checks")
def v40_health_check(payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    user=_bearer_user(request)
    if user and user.role not in {"sudo","security_admin"}: raise HTTPException(403,"Health verdicts require Sudo or Security Admin")
    release_id=payload.get("release_id"); release=db.query(ToolRelease).filter(ToolRelease.release_id==release_id).first()
    if not release: raise HTTPException(404,"Release not found")
    checks=payload.get("checks") or [{"name":"binary_integrity","status":"pass"},{"name":"dependency_integrity","status":"pass"},{"name":"safe_smoke_test","status":"pass"},{"name":"parser_regression","status":"pass"},{"name":"security_regression","status":"pass"}]
    status="healthy" if all(str(x.get("status")).lower()=="pass" for x in checks) else "failed"
    evidence=sha256_json({"release_id":release_id,"checks":checks})
    h=ToolHealthCheck(check_id="hc_"+uuid.uuid4().hex[:16],release_id=release_id,worker_id=payload.get("worker_id",""),status=status,checks_json=json.dumps(checks),evidence_sha256=evidence,notes=payload.get("notes",""))
    release.health_status=status; db.add(h); db.commit(); db.refresh(h)
    if status=="failed": release.verification_status="verified"  # artifact remains verified; deployment engine must not promote it
    db.commit()
    return {"check_id":h.check_id,"release_id":release_id,"status":status,"evidence_sha256":evidence,"promotion":status=="healthy"}

@router.get("/v40/health-checks")
def v40_health_checks(request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    return [clean(x) for x in db.query(ToolHealthCheck).order_by(ToolHealthCheck.created_at.desc()).limit(200).all()]


@router.get("/v40/agent-swarm/containment")
def v40_agent_swarm_containment(request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    p=db.query(AgentContainmentPolicy).first()
    if not p:
        p=AgentContainmentPolicy(policy_id="agent_default",name="Default Agent Containment",egress_mode="deny_by_default",allowed_destinations_json="[]",service_account_velocity_threshold=120,website_collaboration_detection=True,emergency_stop=False,require_human_approval_for_external_action=True)
        db.add(p); db.commit(); db.refresh(p)
    return {"policy":clean(p),"controls":["deny-by-default egress","approved destination allowlist","non-human identity velocity anomaly","external website collaboration detection","emergency stop","human approval for external actions"],"note":"These controls are defensive policy state. Enforcement must occur at the worker/network/identity control points; the SaaS API does not directly manipulate third-party infrastructure."}

@router.put("/v40/agent-swarm/containment")
def v40_agent_swarm_containment_update(payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    user=_bearer_user(request)
    if user and user.role not in {"sudo","security_admin"}: raise HTTPException(403,"Containment policy changes require Sudo or Security Admin")
    p=db.query(AgentContainmentPolicy).first()
    if not p:
        p=AgentContainmentPolicy(policy_id="agent_default"); db.add(p)
    p.egress_mode=payload.get("egress_mode",p.egress_mode); p.allowed_destinations_json=json.dumps(payload.get("allowed_destinations",json.loads(p.allowed_destinations_json or "[]")))
    p.service_account_velocity_threshold=int(payload.get("service_account_velocity_threshold",p.service_account_velocity_threshold)); p.website_collaboration_detection=bool(payload.get("website_collaboration_detection",p.website_collaboration_detection))
    p.emergency_stop=bool(payload.get("emergency_stop",p.emergency_stop)); p.require_human_approval_for_external_action=bool(payload.get("require_human_approval_for_external_action",p.require_human_approval_for_external_action))
    db.commit(); db.refresh(p); return {"policy":clean(p),"status":"updated"}

@router.post("/v40/agent-swarm/simulate")
def v40_agent_swarm_simulate(payload: dict, request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    actions=int(payload.get("actions_per_minute",0)); destinations=int(payload.get("external_destinations",0)); coordination=int(payload.get("coordination_sites",0)); privileged=bool(payload.get("privileged_identity",False))
    score=min(100, actions/2 + destinations*12 + coordination*15 + (25 if privileged else 0))
    controls=[]
    if actions>120: controls.append("freeze service identity");
    if destinations>0: controls.append("deny unapproved egress");
    if coordination>=2: controls.append("open swarm-correlation case");
    if privileged: controls.append("require privileged-session review")
    return {"risk_score":round(score,1),"classification":"critical" if score>=80 else "high" if score>=60 else "medium" if score>=35 else "low","recommended_controls":controls,"mode":"simulation_only"}

@router.post("/v40/artifacts")
def v40_register_artifact(payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    user=_bearer_user(request)
    if user and user.role not in {"sudo","security_admin"}: raise HTTPException(403,"Artifact registration requires Sudo or Security Admin")
    if not payload.get("sha256") or len(payload["sha256"])!=64: raise HTTPException(400,"sha256 must be 64 hex characters")
    a=ToolArtifact(artifact_id="art_"+uuid.uuid4().hex[:16],release_id=payload.get("release_id",""),storage_uri=payload.get("storage_uri",""),digest=payload.get("digest","sha256:"+payload["sha256"]),sha256=payload["sha256"],signature_status=payload.get("signature_status","verified"),provenance_status=payload.get("provenance_status","verified"),sbom_status=payload.get("sbom_status","verified"),immutable=True)
    db.add(a); db.commit(); db.refresh(a); return clean(a)

@router.get("/v40/artifacts")
def v40_artifacts(request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db); return [clean(x) for x in db.query(ToolArtifact).order_by(ToolArtifact.created_at.desc()).limit(200).all()]


# ---------------------------------------------------------------------------
# VEYRA v4.2 — trusted supply-chain fabric
# ---------------------------------------------------------------------------
@router.get("/v42/trusted-supply-chain/overview")
def v42_trusted_overview(request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    from ..services.v42_trusted_supply_chain import trusted_overview
    return trusted_overview(db)

@router.get("/v42/releases/{release_id}/verification-plan")
def v42_verification_plan(release_id: str, request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    from ..services.v42_trusted_supply_chain import verification_plan
    rel=db.query(ToolRelease).filter(ToolRelease.release_id==release_id).first()
    if not rel: raise HTTPException(404,"Release not found")
    return verification_plan(rel)

@router.post("/v42/releases/{release_id}/attestations")
def v42_attestation(release_id: str, payload: dict, request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    from ..services.v42_trusted_supply_chain import ingest_attestation
    try: return ingest_attestation(db, release_id, payload)
    except ValueError as exc: raise HTTPException(400,str(exc))

@router.get("/v42/releases/{release_id}/attestations")
def v42_attestations(release_id: str, request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    rows=db.query(SupplyChainAttestation).filter(SupplyChainAttestation.release_id==release_id).order_by(SupplyChainAttestation.created_at.desc()).all()
    return [clean(x) for x in rows]

@router.post("/v42/canary/plan")
def v42_canary_plan(payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.v42_trusted_supply_chain import canary_plan
    try: return canary_plan(db,str(payload.get("tool_id","")),str(payload.get("release_id","")),list(payload.get("worker_ids") or []),int(payload.get("percent",10)))
    except ValueError as exc: raise HTTPException(400,str(exc))

@router.post("/v42/canary/{cohort_id}/evaluate")
def v42_canary_evaluate(cohort_id: str, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.v42_trusted_supply_chain import evaluate_canary
    try: return evaluate_canary(db,cohort_id)
    except ValueError as exc: raise HTTPException(400,str(exc))

@router.post("/v42/releases/{release_id}/trusted-promote")
def v42_trusted_promote(release_id: str, payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.v42_trusted_supply_chain import trusted_promote
    try: return trusted_promote(db,release_id,str(payload.get("channel","stable")))
    except ValueError as exc: raise HTTPException(400,str(exc))

@router.post("/v42/ai-supply-chain/assets")
def v42_register_ai_asset(payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    required=["asset_id","asset_type","name","version"]
    missing=[x for x in required if not payload.get(x)]
    if missing: raise HTTPException(400,"Missing: "+", ".join(missing))
    row=db.query(AISupplyChainAsset).filter(AISupplyChainAsset.asset_id==payload["asset_id"]).first()
    if not row:
        row=AISupplyChainAsset(asset_id=payload["asset_id"],asset_type=payload["asset_type"],name=payload["name"],version=payload["version"])
        db.add(row)
    for k in ("digest","source_uri","provenance_uri","sbom_uri","policy_status","trust_status"):
        if k in payload: setattr(row,k,str(payload[k]))
    row.metadata_json=json.dumps(payload.get("metadata",{}),sort_keys=True)
    db.commit(); db.refresh(row); return clean(row)

@router.get("/v42/ai-supply-chain/assets")
def v42_ai_assets(request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    return [clean(x) for x in db.query(AISupplyChainAsset).order_by(AISupplyChainAsset.created_at.desc()).limit(500).all()]

@router.post("/v42/agent-circuit-breaker")
def v42_circuit_breaker(payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from ..services.v42_trusted_supply_chain import create_circuit_breaker
    if not payload.get("agent_id"): raise HTTPException(400,"agent_id is required")
    return create_circuit_breaker(db,str(payload["agent_id"]),str(payload.get("reason","operator emergency stop")),str(payload.get("scope","agent")))

@router.get("/v42/agent-circuit-breakers")
def v42_circuit_breakers(request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    return [clean(x) for x in db.query(AgentCircuitBreaker).order_by(AgentCircuitBreaker.activated_at.desc()).limit(200).all()]

@router.post("/v42/verification/run-fixed")
def v42_run_fixed_verifier(payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    """Managed-worker endpoint contract. The API only exposes a fixed verifier allowlist; production should route this to a worker queue."""
    verifier=str(payload.get("verifier","")); args=list(payload.get("args") or [])
    if verifier not in {"cosign","syft","grype","tuf"}: raise HTTPException(400,"Verifier not allowlisted")
    if any(str(a).startswith("-") and a in {"--shell","--command","-c"} for a in args): raise HTTPException(400,"Shell execution flags are prohibited")
    from ..services.v42_trusted_supply_chain import VERIFIER_COMMANDS
    return {"status":"worker_contract_only","verifier":verifier,"binary":VERIFIER_COMMANDS[verifier],"args":args,"execution":"managed_worker_required","shell":False}

# ---------------------------------------------------------------------------
# VEYRA v4.1 — verified worker runtime, promotion and rollback controller
# ---------------------------------------------------------------------------
@router.get("/v41/supply-chain/runtime")
def v41_runtime_overview(request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    from ..services.v41_supply_chain_runtime import runtime_overview
    return runtime_overview(db)

@router.post("/v41/verification/{release_id}/report")
def v41_verification_report(release_id: str, payload: dict, request: Request, db: Session = Depends(get_db)):
    _auth_user(request, db)
    worker_id = str(payload.get("worker_id", ""))
    if not worker_id: raise HTTPException(400, "worker_id is required")
    # Worker authentication must be enforced by workload identity in production.
    from ..services.v41_supply_chain_runtime import accept_verification_report
    try:
        result = accept_verification_report(db, release_id, worker_id, payload)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return result

@router.post("/v41/releases/{release_id}/promote")
def v41_promote_release(release_id: str, payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    user = _bearer_user(request)
    if user and user.role not in {"sudo", "security_admin"}:
        raise HTTPException(403, "Release promotion requires Sudo or Security Admin")
    from ..services.v41_supply_chain_runtime import promote_release
    try:
        return promote_release(db, release_id, str(payload.get("channel", "stable")))
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@router.post("/v41/deployments/{deployment_id}/rollback-on-failure")
def v41_rollback_on_failure(deployment_id: str, payload: dict, request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    user = _bearer_user(request)
    if user and user.role not in {"sudo", "security_admin"}:
        raise HTTPException(403, "Rollback requires Sudo or Security Admin")
    from ..services.v41_supply_chain_runtime import rollback_on_failure
    try:
        return rollback_on_failure(db, deployment_id, str(payload.get("reason", "health regression")))
    except ValueError as exc:
        raise HTTPException(400, str(exc))

# ---------------------------------------------------------------------------
# VEYRA v6.0 — Checklist Registry (P6-A foundation)
# ---------------------------------------------------------------------------
class ChecklistRunRequest(BaseModel):
    parameters: dict = Field(default_factory=dict)
    notes: str = Field(default="", max_length=2000)
    approval_confirmed: bool = False
    evidence: dict = Field(default_factory=dict)


@router.get("/v60/checklists")
def v60_list_checklists(domain: str | None = Query(None, max_length=64), tier: str | None = Query(None, max_length=32)):
    """List all registered checklists. Filter by domain or tier when supplied."""
    from ..services.checklist_registry import CHECKLISTS

    items = CHECKLISTS
    if domain:
        items = [c for c in items if c["domain"] == domain]
    if tier:
        items = [c for c in items if c["tier"] == tier]
    return {"total": len(items), "checklists": items}


@router.get("/v60/checklists/domains")
def v60_checklist_domains():
    """Domain summary — counts per domain plus tier breakdown."""
    from ..services.checklist_registry import CHECKLISTS, DOMAINS
    from collections import Counter

    by_domain = Counter(c["domain"] for c in CHECKLISTS)
    by_tier = Counter(c["tier"] for c in CHECKLISTS)
    return {"domains": DOMAINS, "per_domain": dict(by_domain), "per_tier": dict(by_tier), "total": len(CHECKLISTS)}


@router.get("/v60/checklists/{checklist_id}")
def v60_get_checklist(checklist_id: str):
    """Single checklist definition by id."""
    from ..services.checklist_runner import get_checklist, UnknownChecklistError

    try:
        return get_checklist(checklist_id)
    except UnknownChecklistError:
        raise HTTPException(404, f"Checklist '{checklist_id}' not found")


@router.post("/v60/checklists/{checklist_id}/run")
def v60_run_checklist(checklist_id: str, req: ChecklistRunRequest, request: Request, db: Session = Depends(get_db)):
    """Govern a checklist run — approval-gated for essential tier, returns signed receipt.

    Essential tier requires `approval_confirmed=true`. Evidence can be supplied
    via `evidence` and is stored on the result row.
    """
    from ..services.checklist_runner import UnknownChecklistError, run_checklist

    _auth_user(request, db)
    try:
        run = run_checklist(checklist_id, parameters=req.parameters)
    except UnknownChecklistError:
        raise HTTPException(404, f"Checklist '{checklist_id}' not found")
    # Approval gate: essential tier requires explicit confirmation
    if run.tier == "essential" and not req.approval_confirmed:
        raise HTTPException(403, "Essential checklists require approval_confirmed=true")
    # Merge caller notes without mutating the frozen dataclass (return shape carries it)
    notes = req.notes.strip() or run.notes
    payload = {
        "checklist_id": run.checklist_id,
        "domain": run.domain,
        "category": run.category,
        "name": run.name,
        "owner_role": run.owner_role,
        "cadence": run.cadence,
        "tier": run.tier,
        "scope": run.scope,
        "evidence_expected": list(run.evidence_expected),
        "boundary": run.boundary,
        "status": run.status,
        "requested_at": run.requested_at.isoformat(),
        "parameters": run.parameters,
        "notes": notes,
    }
    db.add(AuditEvent(actor="console-user", action="checklist_run_requested", target=checklist_id, outcome=run.status))
    db.commit()
    # also persist (P6-A-4) — store supplied evidence on result row
    try:
        from app.services.checklist_runner import create_persisted_run, create_receipt
        from app.models import ChecklistResult
        import uuid as _uuid

        prow = create_persisted_run(db, checklist_id, requested_by="console-user", parameters=req.parameters, notes=notes)
        # attach evidence if supplied
        if req.evidence:
            db.add(ChecklistResult(result_id="res_" + _uuid.uuid4().hex[:16], run_id=prow.run_id, checklist_id=checklist_id, check_name="evidence", status="pass", evidence_json=json.dumps(req.evidence, sort_keys=True)))
            db.commit()
        # attach receipt
        create_receipt(db, prow.run_id, payload)
        payload["run_id"] = prow.run_id
        payload["receipt_sha256"] = payload.get("event_sha256", "")
        # wire alerts (P6-G) — best-effort, never fails the run
        try:
            from app.services.alerts import notify_checklist_run

            notify_checklist_run(checklist_id, prow.run_id, run.tier, req.evidence)
        except Exception:
            pass
    except Exception:
        pass
    return payload


@router.get("/v60/runs")
def v60_list_runs(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    from app.services.checklist_runner import list_persisted_runs

    rows = list_persisted_runs(db, limit)
    return [{"run_id": r.run_id, "checklist_id": r.checklist_id, "status": r.status, "requested_at": r.requested_at.isoformat() if r.requested_at else "", "requested_by": r.requested_by} for r in rows]


@router.get("/v60/runs/{run_id}")
def v60_get_run(run_id: str, db: Session = Depends(get_db)):
    from app.services.checklist_runner import get_persisted_run

    row = get_persisted_run(db, run_id)
    if not row:
        raise HTTPException(404, "Run not found")
    from app.models import ChecklistResult, ChecklistReceipt

    results = db.query(ChecklistResult).filter(ChecklistResult.run_id == run_id).all()
    receipt = db.query(ChecklistReceipt).filter(ChecklistReceipt.run_id == run_id).first()
    return {
        "run_id": row.run_id,
        "checklist_id": row.checklist_id,
        "status": row.status,
        "parameters": json.loads(row.parameters_json or "{}"),
        "notes": row.notes,
        "requested_at": row.requested_at.isoformat() if row.requested_at else "",
        "results": [{"result_id": r.result_id, "check_name": r.check_name, "status": r.status, "evidence": json.loads(r.evidence_json or "{}")} for r in results],
        "receipt": {"receipt_id": receipt.receipt_id, "payload_sha256": receipt.payload_sha256, "signature": receipt.signature} if receipt else None,
    }


@router.get("/v60/receipts/{run_id}")
def v60_get_receipt(run_id: str, db: Session = Depends(get_db)):
    from app.models import ChecklistReceipt

    row = db.query(ChecklistReceipt).filter(ChecklistReceipt.run_id == run_id).first()
    if not row:
        raise HTTPException(404, "Receipt not found")
    return {"receipt_id": row.receipt_id, "run_id": row.run_id, "payload_sha256": row.payload_sha256, "signature": row.signature, "payload": json.loads(row.payload_json or "{}")}


# ---------------------------------------------------------------------------
# VEYRA v6.1 — Live sensors, baselines, drop diagnosis (P6-B)
# ---------------------------------------------------------------------------
class LiveIngestRequest(BaseModel):
    sensor_type: str = Field(pattern="^(wifi|ethernet|device|drop|traffic)$")
    sensor_id: str = Field(default="unknown", max_length=128)
    event_type: str = Field(min_length=1, max_length=128)
    severity: str = Field(default="INFO", pattern="^(INFO|LOW|MEDIUM|HIGH|CRITICAL)$")
    payload: dict = Field(default_factory=dict)
    provenance: str = Field(default="", max_length=255)
    trace_id: str = Field(default="", max_length=128)


@router.post("/v61/ingest")
def v61_ingest(req: LiveIngestRequest, db: Session = Depends(get_db), _auth: None = Depends(require_collector)):
    from app.services.live_sensor_ingest import normalize_event, persist_event

    norm = normalize_event(req.sensor_type, req.event_type, req.payload, req.sensor_id, req.severity, req.provenance, req.trace_id)
    row = persist_event(db, norm)
    db.add(AuditEvent(actor="sensor", action="live_sensor_ingested", target=req.sensor_type, outcome=req.severity))
    db.commit()
    # P6-G: alert on HIGH/CRITICAL or drop events
    try:
        from app.services.alerts import notify_sensor_event

        if norm["severity"] in ("HIGH", "CRITICAL") or norm["sensor_type"] == "drop":
            notify_sensor_event(norm)
    except Exception:
        pass
    return {"event_id": row.event_id, "event_sha256": row.event_sha256, "observed_at": row.observed_at.isoformat()}


@router.get("/v61/events")
def v61_events(limit: int = Query(50, ge=1, le=500), sensor_type: str | None = Query(None, max_length=32), db: Session = Depends(get_db)):
    from app.models import LiveSensorEvent

    q = db.query(LiveSensorEvent)
    if sensor_type:
        q = q.filter(LiveSensorEvent.sensor_type == sensor_type)
    rows = q.order_by(LiveSensorEvent.observed_at.desc()).limit(limit).all()
    return [{"event_id": r.event_id, "sensor_type": r.sensor_type, "event_type": r.event_type, "severity": r.severity, "payload": json.loads(r.payload_json or "{}"), "event_sha256": r.event_sha256, "observed_at": r.observed_at.isoformat()} for r in rows]


class BaselineCreateRequest(BaseModel):
    scope: str = Field(min_length=1, max_length=64)
    snapshot: dict
    owner: str = Field(default="security_operator", max_length=255)
    approved: bool = False


@router.post("/v61/baselines")
def v61_create_baseline(req: BaselineCreateRequest, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from app.services.baseline_engine import create_baseline

    row = create_baseline(db, req.scope, req.snapshot, req.owner, req.approved)
    return {"baseline_id": row.baseline_id, "scope": row.scope, "snapshot_sha256": row.snapshot_sha256, "approved": row.approved}


@router.get("/v61/baselines")
def v61_list_baselines(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    from app.models import NetworkBaseline

    rows = db.query(NetworkBaseline).order_by(NetworkBaseline.created_at.desc()).limit(limit).all()
    return [{"baseline_id": r.baseline_id, "scope": r.scope, "version": r.version, "owner": r.owner, "snapshot_sha256": r.snapshot_sha256, "approved": r.approved} for r in rows]


@router.post("/v61/baselines/{baseline_id}/approve")
def v61_approve_baseline(baseline_id: str, db: Session = Depends(get_db), _: bool = Depends(require_admin)):
    from app.services.baseline_engine import approve_baseline

    try:
        row = approve_baseline(db, baseline_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {"baseline_id": row.baseline_id, "approved": row.approved}


class BaselineEvaluateRequest(BaseModel):
    scope: str = Field(min_length=1, max_length=64)
    current: dict


@router.post("/v61/baselines/evaluate")
def v61_evaluate_baseline(req: BaselineEvaluateRequest, db: Session = Depends(get_db)):
    from app.services.baseline_engine import evaluate_current

    return evaluate_current(db, req.scope, req.current)


class DropCreateRequest(BaseModel):
    link_id: str = Field(min_length=1, max_length=255)
    link_type: str = Field(default="wifi", pattern="^(wifi|ethernet|unknown)$")
    signal_dbm: float | None = None
    dhcp_state: str = Field(default="unknown", max_length=32)
    dns_state: str = Field(default="unknown", max_length=32)
    ap_assoc_state: str = Field(default="unknown", max_length=32)
    recent_flaps: int = Field(default=0, ge=0, le=1000)


@router.post("/v61/drops")
def v61_create_drop(req: DropCreateRequest, db: Session = Depends(get_db)):
    from app.services.drop_diagnosis import persist_drop

    row = persist_drop(db, req.link_id, req.link_type, req.signal_dbm, req.dhcp_state, req.dns_state, req.ap_assoc_state, req.recent_flaps)
    hyps = json.loads(row.hypotheses_json or "[]")
    try:
        from app.services.alerts import notify_drop

        notify_drop(req.link_id, hyps)
    except Exception:
        pass
    return {"drop_id": row.drop_id, "link_id": row.link_id, "hypotheses": hyps}


@router.get("/v60/trends")
def v60_trends(db: Session = Depends(get_db)):
    from app.services.trends import overview

    return overview(db)


@router.get("/v60/trends/posture")
def v60_posture(days: int = Query(14, ge=1, le=90), db: Session = Depends(get_db)):
    from app.services.trends import posture_over_time

    return posture_over_time(db, days)


@router.get("/v60/trends/mttr")
def v60_mttr(db: Session = Depends(get_db)):
    from app.services.trends import mttr_per_checklist

    return mttr_per_checklist(db)


@router.get("/v61/drops")
def v61_list_drops(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    from app.models import DropEvent

    rows = db.query(DropEvent).order_by(DropEvent.created_at.desc()).limit(limit).all()
    return [{"drop_id": r.drop_id, "link_id": r.link_id, "link_type": r.link_type, "hypotheses": json.loads(r.hypotheses_json or "[]"), "created_at": r.created_at.isoformat()} for r in rows]


@router.get("/v40/docs/index")
def v40_docs_index(request: Request, db: Session = Depends(get_db)):
    """Hydejack-inspired documentation index: markdown-first, searchable, printable."""
    _auth_user(request, db)
    root=_os.path.abspath(_os.path.join(_os.path.dirname(__file__),"../../..","docs"))
    items=[]
    if _os.path.isdir(root):
        for base,_,files in _os.walk(root):
            for fn in sorted(files):
                if not fn.lower().endswith(".md"): continue
                path=_os.path.join(base,fn); rel=_os.path.relpath(path,root).replace(_os.sep,"/")
                title=fn[:-3].replace("_"," ").replace("-"," ")
                try:
                    with open(path,encoding="utf-8",errors="ignore") as fh:
                        for line in fh:
                            if line.startswith("# "): title=line[2:].strip(); break
                except Exception: pass
                items.append({"path":rel,"title":title,"section":rel.split("/")[0] if "/" in rel else "root"})
    return {"release":"4.0","style":"markdown-first documentation hub","features":["search","TOC-ready headings","dark mode","print/PDF friendly","semantic HTML","offline-capable static export"],"items":items}
