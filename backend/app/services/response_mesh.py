"""VEYRA v2.2 Continuous Detection & Response Mesh.

This service is deliberately deterministic at the enforcement boundary. It can
normalize alerts, match fixed detection rules, open investigations and create
approval-gated response requests. The POC never performs host/network changes.
"""
from datetime import datetime, timezone
import hashlib, json, uuid
from ..models import UnifiedSecurityEvent, DetectionRule, ResponseAction, InvestigationCase, InvestigationApproval, AuditEvent

DEFAULT_RULES = [
    {"rule_id":"DET-AI-001","name":"High-risk AI tool invocation","source":"ai","event_types":["agent_tool_call","ai_gateway_denial"],"min_risk_score":60,"action":"investigate"},
    {"rule_id":"DET-ID-001","name":"Privileged anomalous session","source":"identity","event_types":["login_anomaly","privileged_session"],"min_risk_score":60,"action":"investigate"},
    {"rule_id":"DET-NET-001","name":"High-risk network transfer","source":"network","event_types":["network_anomaly","possible_exfiltration"],"min_risk_score":70,"action":"investigate"},
    {"rule_id":"DET-END-001","name":"Endpoint execution anomaly","source":"endpoint","event_types":["process_anomaly","persistence_signal"],"min_risk_score":60,"action":"investigate"},
    {"rule_id":"DET-CLOUD-001","name":"High-risk cloud control-plane activity","source":"cloud","event_types":["cloud_anomaly","privilege_change"],"min_risk_score":60,"action":"investigate"},
]

def _now(): return datetime.now(timezone.utc)
def _id(prefix): return f"{prefix}_{uuid.uuid4().hex[:16]}"
def _sha(v): return hashlib.sha256(json.dumps(v, sort_keys=True, default=str).encode()).hexdigest()

def ensure_rules(db):
    if db.query(DetectionRule).count(): return
    for r in DEFAULT_RULES:
        db.add(DetectionRule(rule_id=r["rule_id"],name=r["name"],source=r["source"],event_types=json.dumps(r["event_types"]),min_risk_score=r["min_risk_score"],action=r["action"]))
    db.commit()

def connector_health():
    return [
      {"name":"Security Fabric Collector","kind":"telemetry","status":"healthy","mode":"normalized events"},
      {"name":"Endpoint Agent","kind":"endpoint","status":"ready","mode":"collector-authenticated"},
      {"name":"Cloud Adapters","kind":"cloud","status":"ready","mode":"read-only POC"},
      {"name":"AI Gateway","kind":"ai","status":"healthy","mode":"policy evaluation"},
      {"name":"Threat Intelligence","kind":"intel","status":"ready","mode":"enrichment"},
      {"name":"SOAR","kind":"response","status":"approval-gated","mode":"no external enforcement in POC"},
    ]

def evaluate_event(db, event_id):
    ensure_rules(db)
    event=db.query(UnifiedSecurityEvent).filter(UnifiedSecurityEvent.event_id==event_id).first()
    if not event: raise ValueError(f"Unknown event '{event_id}'")
    matches=[]
    for r in db.query(DetectionRule).filter(DetectionRule.enabled==True).all():
        types=json.loads(r.event_types or "[]")
        if event.event_type in types and float(event.risk_score or 0) >= r.min_risk_score:
            matches.append({"rule_id":r.rule_id,"name":r.name,"action":r.action,"threshold":r.min_risk_score})
    return {"event_id":event_id,"matched":matches,"decision":"investigate" if matches else "observe"}

def ingest_alert(db, req):
    payload=req.get("payload") or {}
    event_id=req.get("event_id") or _id("evt")
    existing=db.query(UnifiedSecurityEvent).filter(UnifiedSecurityEvent.event_id==event_id).first()
    if existing: return {"event_id":event_id,"status":"duplicate","decision":"observe","matched":[]}
    row=UnifiedSecurityEvent(event_id=event_id,trace_id=req.get("trace_id",_id("trace")),plane=req.get("plane","detection"),event_type=req.get("event_type","alert"),actor=req.get("actor",""),source=req.get("source",""),target=req.get("target",""),risk_score=float(req.get("risk_score",0)),severity=req.get("severity","INFO"),payload=json.dumps(payload,default=str),event_sha256=_sha(payload),observed_at=_now())
    db.add(row); db.add(AuditEvent(actor="detection-mesh",action="alert_ingested",target=event_id,outcome=row.severity)); db.commit()
    decision=evaluate_event(db,event_id)
    if decision["matched"]:
        from .autonomous_soc import investigate_event
        case=investigate_event(db,event_id,actor="detection-mesh")
        decision["case_id"]=case["case_id"]
    return {"event_id":event_id,"status":"ingested",**decision}

def request_response(db, case_id, action, target, approval_id=None):
    allowed={"isolate_host","revoke_sessions","block_ip","collect_evidence"}
    if action not in allowed: raise ValueError("Unsupported response action")
    case=db.query(InvestigationCase).filter(InvestigationCase.case_id==case_id).first()
    if not case: raise ValueError("Unknown case")
    aid=_id("resp")
    row=ResponseAction(action_id=aid,case_id=case_id,action=action,target=target,approval_id=approval_id,status="approved_for_adapter" if approval_id else "pending_approval",verification_status="not_started")
    db.add(row); db.add(AuditEvent(actor="response-mesh",action="response_action_created",target=case_id,outcome=row.status)); db.commit()
    return serialize_action(row)

def verify_response(db, action_id, observed_state, evidence=None):
    row=db.query(ResponseAction).filter(ResponseAction.action_id==action_id).first()
    if not row: raise ValueError("Unknown response action")
    evidence=evidence or {}
    row.verification_status="verified" if observed_state else "failed"
    row.status="completed" if observed_state else "verification_failed"
    row.evidence_sha256=_sha(evidence); row.verified_at=_now()
    db.add(AuditEvent(actor="verification-engine",action="response_verification",target=action_id,outcome=row.verification_status)); db.commit()
    return serialize_action(row)

def serialize_action(row):
    return {"action_id":row.action_id,"case_id":row.case_id,"action":row.action,"target":row.target,"status":row.status,"verification_status":row.verification_status,"approval_id":row.approval_id,"evidence_sha256":row.evidence_sha256}

def list_actions(db, limit=50):
    return [serialize_action(x) for x in db.query(ResponseAction).order_by(ResponseAction.created_at.desc()).limit(limit).all()]
