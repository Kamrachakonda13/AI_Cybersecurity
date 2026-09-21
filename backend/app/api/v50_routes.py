from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import json, hashlib, uuid
from ..db import get_db
from ..models import AISupplyChainAsset, AIAssetTrustRecord, AIBOMRecord, TrustGraphNode, TrustGraphEdge, AgentTrajectory, TrustDecisionRecord, RuntimeAttestation, SignedMandate
from ..services.v50_trust_control_plane import *

router = APIRouter(prefix="/api/v50", tags=["v5.0 trust control plane"])

def admin(request: Request):
    # Reuse the platform's administrator gate; v5.0 never bypasses it.
    from .routes import require_admin
    return require_admin(request)

class AssetIn(BaseModel):
    asset_id: str
    asset_type: str = "model"
    name: str
    version: str = ""
    digest: str = ""
    publisher: str = ""
    issuer: str = ""
    runtime_identity: str = ""
    source_uri: str = ""
    provenance_uri: str = ""
    policy_status: str = "pending"
    validation_status: str = "pending"
    deployment_status: str = "pending"
    behavior_baseline: str = ""
    trajectory_policy: str = ""
    evidence_sha256: str = ""
    metadata: dict = Field(default_factory=dict)

class TrajectoryIn(BaseModel):
    agent_id: str
    events: list[dict] = Field(default_factory=list)
    policy: dict = Field(default_factory=dict)

class GraphIn(BaseModel):
    assets: list[dict] = Field(default_factory=list)
    relationships: list[dict] = Field(default_factory=list)

class MandateIn(BaseModel):
    principal: str
    delegate: str
    allowed_tools: list[str] = Field(default_factory=list)
    constraints: dict = Field(default_factory=dict)
    signature: str = ""
    expires_at: str | None = None

@router.get("/overview")
def v50_overview(db: Session = Depends(get_db), _=Depends(admin)):
    return overview(db)

@router.get("/gates")
def v50_gates(_=Depends(admin)):
    return {"gates": GATES, "asset_types": ASSET_TYPES, "trust_invariant": TRUST_INVARIANT}

@router.post("/ai-assets/register")
def register_ai_asset(body: AssetIn, db: Session = Depends(get_db), _=Depends(admin)):
    if body.asset_type not in ASSET_TYPES: raise HTTPException(400, "Unsupported AI asset type")
    existing=db.query(AISupplyChainAsset).filter(AISupplyChainAsset.asset_id==body.asset_id).first()
    data=body.model_dump()
    if existing:
        for k,v in {"asset_type":body.asset_type,"name":body.name,"version":body.version,"digest":body.digest,"source_uri":body.source_uri,"provenance_uri":body.provenance_uri,"policy_status":body.policy_status}.items(): setattr(existing,k,v)
        existing.metadata_json=json.dumps(body.metadata, sort_keys=True)
        obj=existing
    else:
        obj=AISupplyChainAsset(asset_id=body.asset_id,asset_type=body.asset_type,name=body.name,version=body.version,digest=body.digest,source_uri=body.source_uri,provenance_uri=body.provenance_uri,policy_status=body.policy_status,metadata_json=json.dumps(body.metadata,sort_keys=True))
        db.add(obj)
    ev=evaluate_asset(data)
    obj.trust_status=ev["status"]
    db.add(AIAssetTrustRecord(asset_id=body.asset_id,trust_score=ev["score"],trust_status=ev["status"],gates_json=json.dumps(ev["checks"],sort_keys=True),missing_json=json.dumps(ev["missing"]),evidence_sha256=body.evidence_sha256 or hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()))
    db.commit()
    return {"asset":body.asset_id,"evaluation":ev}

@router.get("/ai-assets")
def list_ai_assets(db: Session = Depends(get_db), _=Depends(admin)):
    return [{"asset_id":x.asset_id,"asset_type":x.asset_type,"name":x.name,"version":x.version,"digest":x.digest,"trust_status":x.trust_status,"policy_status":x.policy_status} for x in db.query(AISupplyChainAsset).order_by(AISupplyChainAsset.created_at.desc()).limit(500)]

@router.post("/aibom/generate")
def generate_aibom(body: GraphIn, db: Session = Depends(get_db), _=Depends(admin)):
    if not body.assets: raise HTTPException(400,"At least one root asset is required")
    root=body.assets[0]
    doc=make_aibom(root, body.relationships)
    bom_id="bom_"+uuid.uuid4().hex[:16]
    db.add(AIBOMRecord(bom_id=bom_id,root_asset_id=root.get("asset_id",""),document_json=json.dumps(doc,sort_keys=True),document_sha256=doc["document_sha256"]))
    db.commit()
    return {"bom_id":bom_id,**doc}

@router.post("/trajectory/evaluate")
def trajectory(body: TrajectoryIn, db: Session = Depends(get_db), _=Depends(admin)):
    result=evaluate_trajectory(body.events,body.policy)
    db.add(AgentTrajectory(trajectory_id=result["trajectory_id"],agent_id=body.agent_id,status=result["status"],score=result["score"],events_json=json.dumps(body.events,sort_keys=True),violations_json=json.dumps(result["violations"],sort_keys=True),evidence_sha256=result["evidence_sha256"]))
    db.commit()
    return result

@router.post("/trust/decide")
def decide(asset: dict, db: Session = Depends(get_db), _=Depends(admin)):
    result=trust_decision(asset,asset.get("trajectory"))
    db.add(TrustDecisionRecord(decision_id=result["decision_id"],subject_id=asset.get("asset_id") or asset.get("agent_id") or "unknown",decision=result["decision"],reason=result["reason"],evidence_sha256=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()))
    db.commit()
    return result

@router.post("/trust-graph/rebuild")
def rebuild_graph(body: GraphIn, db: Session = Depends(get_db), _=Depends(admin)):
    graph=build_trust_graph(body.assets,body.relationships)
    for n in graph["nodes"]:
        old=db.query(TrustGraphNode).filter(TrustGraphNode.node_id==n["id"]).first()
        if not old: db.add(TrustGraphNode(node_id=n["id"],node_type=n["type"],label=n.get("label") or "",trust_status=n["trust"],trust_score=n["score"]))
        else: old.trust_status=n["trust"]; old.trust_score=n["score"]
    for e in body.relationships:
        eid=e.get("edge_id") or "edge_"+hashlib.sha256(json.dumps(e,sort_keys=True).encode()).hexdigest()[:16]
        if not db.query(TrustGraphEdge).filter(TrustGraphEdge.edge_id==eid).first(): db.add(TrustGraphEdge(edge_id=eid,source_id=e.get("source_id",""),target_id=e.get("target_id",""),relationship=e.get("relationship","depends_on"),policy_status=e.get("policy_status","pending"),metadata_json=json.dumps(e)))
    db.commit()
    return graph

@router.get("/trust-graph")
def get_graph(db: Session = Depends(get_db), _=Depends(admin)):
    nodes=db.query(TrustGraphNode).limit(1000).all(); edges=db.query(TrustGraphEdge).limit(2000).all()
    return {"graph_version":"5.0","nodes":[{"id":n.node_id,"type":n.node_type,"label":n.label,"trust":n.trust_status,"score":n.trust_score} for n in nodes],"edges":[{"id":e.edge_id,"source_id":e.source_id,"target_id":e.target_id,"relationship":e.relationship,"policy_status":e.policy_status} for e in edges]}

@router.post("/runtime-attestation")
def runtime_attestation(payload: dict, db: Session = Depends(get_db), _=Depends(admin)):
    aid="ra_"+uuid.uuid4().hex[:16]
    evidence=payload.get("evidence",{})
    evsha=hashlib.sha256(json.dumps(evidence,sort_keys=True).encode()).hexdigest()
    status="verified" if payload.get("artifact_digest") and payload.get("workload_identity") and payload.get("policy_hash") else "pending"
    db.add(RuntimeAttestation(attestation_id=aid,subject_id=payload.get("subject_id",""),workload_identity=payload.get("workload_identity",""),artifact_digest=payload.get("artifact_digest",""),policy_hash=payload.get("policy_hash",""),behavior_hash=payload.get("behavior_hash",evsha),status=status,evidence_json=json.dumps(evidence,sort_keys=True)))
    db.commit()
    return {"attestation_id":aid,"status":status,"evidence_sha256":evsha}

@router.post("/mandates")
def mandate(body: MandateIn, db: Session = Depends(get_db), _=Depends(admin)):
    mid="mand_"+uuid.uuid4().hex[:16]
    status="verified" if body.signature else "pending"
    db.add(SignedMandate(mandate_id=mid,principal=body.principal,delegate=body.delegate,allowed_tools_json=json.dumps(body.allowed_tools),constraints_json=json.dumps(body.constraints,sort_keys=True),signature=body.signature,status=status))
    db.commit()
    return {"mandate_id":mid,"status":status,"enforcement":"managed-policy-point-required","note":"VEYRA records the mandate; an authorized enforcement proxy/worker must enforce it."}

@router.get("/decisions")
def decisions(db: Session = Depends(get_db), _=Depends(admin)):
    return [{"decision_id":x.decision_id,"subject_id":x.subject_id,"decision":x.decision,"reason":x.reason,"evidence_sha256":x.evidence_sha256,"created_at":x.created_at} for x in db.query(TrustDecisionRecord).order_by(TrustDecisionRecord.created_at.desc()).limit(500)]

class AuthorityIn(BaseModel):
    agent_id: str
    issuer: str = ""
    owner: str = ""
    credential_ref: str = ""
    authority: dict = Field(default_factory=dict)
    delegation_chain: list[dict] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    allowed_resources: list[str] = Field(default_factory=list)
    expires_at: str | None = None
    status: str = "active"

class GatewayIn(BaseModel):
    gateway_id: str
    agent_id: str
    request: dict = Field(default_factory=dict)
    policy: dict = Field(default_factory=dict)

class MCPFingerprintIn(BaseModel):
    server_id: str
    version: str = ""
    publisher: str = ""
    tools_hash: str = ""
    permissions_hash: str = ""
    endpoint_hash: str = ""

class MemoryIn(BaseModel):
    memory_id: str
    agent_id: str
    owner: str = ""
    classification: str = "internal"
    content_hash: str = ""
    provenance: str = ""
    poisoning_score: float = 0

class TransactionIn(BaseModel):
    transaction_id: str
    agent_id: str
    target: str = ""
    amount: float = 0
    transaction_ceiling: float = 0
    new_destination: bool = False
    unusual_time: bool = False
    approval_required: bool = True
    approved: bool = False

class BehaviorIn(BaseModel):
    agent_id: str
    baseline: dict = Field(default_factory=dict)
    observed: dict = Field(default_factory=dict)

class TwinIn(BaseModel):
    root_subject: str
    nodes: list[dict] = Field(default_factory=list)
    edges: list[dict] = Field(default_factory=list)

@router.post("/identity/authority")
def authority(body: AuthorityIn, db: Session = Depends(get_db), _=Depends(admin)):
    from ..models import AgentIdentityAuthority
    ev=evaluate_agent_authority(body.model_dump())
    obj=db.query(AgentIdentityAuthority).filter_by(agent_id=body.agent_id).first()
    if not obj:
        obj=AgentIdentityAuthority(agent_id=body.agent_id); db.add(obj)
    obj.issuer=body.issuer; obj.owner=body.owner; obj.credential_ref=body.credential_ref
    obj.authority_json=json.dumps({**body.authority,"allowed_tools":body.allowed_tools,"allowed_resources":body.allowed_resources},sort_keys=True)
    obj.delegation_chain_json=json.dumps(body.delegation_chain,sort_keys=True); obj.status=body.status
    obj.evidence_sha256=_sha(body.model_dump()); db.commit()
    return {"agent_id":body.agent_id,"evaluation":ev,"evidence_sha256":obj.evidence_sha256}

@router.post("/gateway/evaluate")
def gateway(body: GatewayIn, db: Session = Depends(get_db), _=Depends(admin)):
    from ..models import AgentGatewayPolicy
    result=evaluate_gateway_request(body.request,body.policy)
    db.add(AgentGatewayPolicy(gateway_id=body.gateway_id,agent_id=body.agent_id,allowed_tools_json=json.dumps(body.policy.get("allowed_tools",[])),allowed_destinations_json=json.dumps(body.policy.get("allowed_destinations",[])),data_policy_json=json.dumps(body.policy.get("data_policy",{})),rate_limit=int(body.policy.get("rate_limit",60)),transaction_limit=float(body.policy.get("transaction_limit",0)),require_approval=bool(body.policy.get("require_approval",True)),status=result["decision"]))
    db.commit(); return result

@router.post("/mcp/fingerprint")
def mcp_fingerprint(body: MCPFingerprintIn, db: Session = Depends(get_db), _=Depends(admin)):
    from ..models import MCPTrustFingerprint
    current=body.model_dump(); current["fingerprint_sha256"]=_sha(current)
    previous=db.query(MCPTrustFingerprint).filter_by(server_id=body.server_id).first()
    prev=previous.__dict__ if previous else {}
    result=compare_mcp_fingerprint(prev,current)
    if not previous: previous=MCPTrustFingerprint(server_id=body.server_id); db.add(previous)
    previous.version=body.version; previous.publisher=body.publisher; previous.tools_hash=body.tools_hash; previous.permissions_hash=body.permissions_hash; previous.endpoint_hash=body.endpoint_hash; previous.fingerprint_sha256=current["fingerprint_sha256"]; previous.status=result["status"]; previous.drift_type=result["drift_type"]
    db.commit(); return {"server_id":body.server_id,**result}

@router.post("/memory/evaluate")
def memory(body: MemoryIn, db: Session = Depends(get_db), _=Depends(admin)):
    from ..models import AgentMemoryTrustRecord
    result=evaluate_memory(body.model_dump()); db.add(AgentMemoryTrustRecord(**body.model_dump(),status=result["status"])); db.commit(); return result

@router.post("/transaction/assess")
def transaction(body: TransactionIn, db: Session = Depends(get_db), _=Depends(admin)):
    from ..models import AgentTransactionAssessment
    result=assess_transaction(body.model_dump()); db.add(AgentTransactionAssessment(transaction_id=body.transaction_id,agent_id=body.agent_id,target=body.target,amount=body.amount,risk_score=result["risk_score"],decision=result["decision"],reasons_json=json.dumps(result["reasons"]),evidence_sha256=result["evidence_sha256"])); db.commit(); return result

@router.post("/behavior/compare")
def behavior(body: BehaviorIn, db: Session = Depends(get_db), _=Depends(admin)):
    from ..models import AgentBehaviorBaseline
    result=compare_behavior(body.baseline,body.observed)
    if not db.query(AgentBehaviorBaseline).filter_by(agent_id=body.agent_id).first():
        db.add(AgentBehaviorBaseline(agent_id=body.agent_id,tools_json=json.dumps(body.baseline.get("tools",[])),destinations_json=json.dumps(body.baseline.get("destinations",[])),delegation_depth=int(body.baseline.get("delegation_depth",0)),transaction_ceiling=float(body.baseline.get("transaction_ceiling",0)),action_sequence_hash=_sha(body.baseline),baseline_hash=result["evidence_sha256"]))
        db.commit()
    return result

@router.post("/digital-twin/simulate")
def digital_twin(body: TwinIn, db: Session = Depends(get_db), _=Depends(admin)):
    from ..models import DigitalTwinScenario
    result=build_digital_twin(body.root_subject,body.nodes,body.edges); sid=_decision_id("twin")
    db.add(DigitalTwinScenario(scenario_id=sid,root_subject=body.root_subject,nodes_json=json.dumps(result["reachable_nodes"],sort_keys=True),edges_json=json.dumps(body.edges,sort_keys=True),blast_radius=result["blast_radius"],risk_score=result["risk_score"],containment_options_json=json.dumps(result["containment_options"]),evidence_sha256=result["evidence_sha256"])); db.commit()
    return {"scenario_id":sid,**result}

# ---------------------------------------------------------------------------
# VEYRA v5.0 AI Applications Layer — six portfolio-grade shared-platform POCs
# ---------------------------------------------------------------------------
from ..models import AIApplicationRun
from ..services import v50_ai_applications as aiapps

class ResearchIn(BaseModel):
    query: str = Field(min_length=3)
class SocRagIn(BaseModel):
    query: str = Field(min_length=3)
class EnterpriseIn(BaseModel):
    question: str = Field(min_length=3)
class IncidentIn(BaseModel):
    events: list[dict] = Field(default_factory=list)


def _record_ai_run(db, application: str, request: dict, result: dict):
    rid="airun_"+uuid.uuid4().hex[:16]
    db.add(AIApplicationRun(run_id=rid,application=application,status="completed",request_json=json.dumps(request,sort_keys=True),result_json=json.dumps(result,sort_keys=True),evidence_sha256=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()))
    db.commit()
    return rid

@router.get("/ai-applications/catalog")
def ai_application_catalog(_=Depends(admin)):
    return {"applications":aiapps.catalog()}

@router.post("/ai-applications/cybsoc-rag")
def ai_cybsoc(body: SocRagIn, db: Session = Depends(get_db), _=Depends(admin)):
    result=aiapps.cybsoc_rag(body.query); result["run_id"]=_record_ai_run(db,result["application"],body.model_dump(),result); return result

@router.post("/ai-applications/vulnerability-rag")
def ai_vulnerability(body: SocRagIn, db: Session = Depends(get_db), _=Depends(admin)):
    result=aiapps.vulnerability_rag(body.query); result["run_id"]=_record_ai_run(db,result["application"],body.model_dump(),result); return result

@router.post("/ai-applications/research-agent")
def ai_research(body: ResearchIn, db: Session = Depends(get_db), _=Depends(admin)):
    result=aiapps.autonomous_research(body.query); result["run_id"]=_record_ai_run(db,result["application"],body.model_dump(),result); return result

@router.post("/ai-applications/incident-response")
def ai_ir(body: IncidentIn, db: Session = Depends(get_db), _=Depends(admin)):
    result=aiapps.incident_response(body.events or None); result["run_id"]=_record_ai_run(db,result["application"],body.model_dump(),result); return result

@router.post("/ai-applications/enterprise-decision")
def ai_enterprise(body: EnterpriseIn, db: Session = Depends(get_db), _=Depends(admin)):
    result=aiapps.enterprise_decision(body.question); result["run_id"]=_record_ai_run(db,result["application"],body.model_dump(),result); return result

@router.post("/ai-applications/evaluation")
def ai_evaluation(db: Session = Depends(get_db), _=Depends(admin)):
    result=aiapps.evaluate_ai(); result["run_id"]=_record_ai_run(db,result["application"],{},result); return result

@router.get("/ai-applications/runs")
def ai_runs(db: Session = Depends(get_db), _=Depends(admin)):
    rows=db.query(AIApplicationRun).order_by(AIApplicationRun.created_at.desc()).limit(100).all()
    return [{"run_id":r.run_id,"application":r.application,"status":r.status,"evidence_sha256":r.evidence_sha256,"created_at":r.created_at} for r in rows]
