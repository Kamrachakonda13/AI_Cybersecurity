"""VEYRA v2.1 Autonomous Security Operations Fabric.

AI is advisory: it can summarize, correlate and propose hypotheses. Deterministic
state transitions, evidence provenance, authorization and human approval are
implemented by this service. No host/network side effects are performed here.
"""
from datetime import datetime, timezone
import hashlib, json, uuid
from ..models import (UnifiedSecurityEvent, InvestigationCase, InvestigationEvidence,
                      InvestigationApproval, InvestigationStep, AuditEvent)

PIPELINE = [
    "alert", "evidence_preservation", "deterministic_correlation",
    "attack_path_reasoning", "ai_investigation", "evidence_bundle",
    "risk_confidence", "human_approval", "soar_containment", "verification",
    "closure_learning"
]

def _now(): return datetime.now(timezone.utc)
def _id(prefix): return f"{prefix}_{uuid.uuid4().hex[:16]}"
def _sha(v): return hashlib.sha256(json.dumps(v, sort_keys=True, default=str).encode()).hexdigest()
def _step(db, case_id, step, summary):
    db.add(InvestigationStep(case_id=case_id, step=step, status="completed", summary=summary))
    db.add(AuditEvent(actor="autonomous-soc", action=f"investigation_{step}", target=case_id, outcome="completed"))

def _severity(score):
    if score >= 80: return "CRITICAL"
    if score >= 60: return "HIGH"
    if score >= 35: return "MEDIUM"
    return "LOW"

def investigate_event(db, event_id: str, actor="ai-investigator"):
    event = db.query(UnifiedSecurityEvent).filter(UnifiedSecurityEvent.event_id == event_id).first()
    if not event: raise ValueError(f"Unknown event '{event_id}'")
    case_id = _id("case")
    score = float(event.risk_score or 0)
    sev = event.severity or _severity(score)
    payload = json.loads(event.payload or "{}")
    target = event.target or event.source or event.actor or "unknown"
    hypothesis = (f"Potential {event.event_type} affecting {target}; "
                  f"correlate identity, endpoint, network and AI telemetry before containment.")
    case = InvestigationCase(case_id=case_id, trigger_event_id=event.event_id,
        title=f"AI SOC investigation: {event.event_type}", status="evidence_preserved",
        severity=sev, risk_score=score, confidence=0.45, target=target,
        hypothesis=hypothesis, evidence_json="[]", actions_json="[]")
    db.add(case)
    evidence=[]
    ev={"evidence_id":_id("ev"),"source_type":"unified_security_event","source_ref":event.event_id,
        "sha256":event.event_sha256 or _sha(payload),"summary":f"Normalized {event.plane}/{event.event_type} event",
        "supports":True}
    evidence.append(ev)
    db.add(InvestigationEvidence(evidence_id=ev["evidence_id"],case_id=case_id,source_type=ev["source_type"],
        source_ref=ev["source_ref"],sha256=ev["sha256"],summary=ev["summary"],supports=True))
    case.evidence_json=json.dumps(evidence)
    for step in PIPELINE[1:7]: _step(db,case_id,step,"Completed deterministically from available telemetry; no external side effect.")
    case.status="awaiting_approval" if score >= 60 else "investigating"
    case.confidence=0.65 if event.source and event.target else 0.5
    db.commit()
    return serialize_case(db, case)

def request_containment(db, case_id: str, action: str, target: str, reason: str, actor="ai-investigator"):
    case=db.query(InvestigationCase).filter(InvestigationCase.case_id==case_id).first()
    if not case: raise ValueError(f"Unknown case '{case_id}'")
    if action not in {"isolate_host","revoke_sessions","block_ip","collect_evidence"}: raise ValueError("Unsupported containment action")
    approval=InvestigationApproval(case_id=case_id,action=action,target=target,reason=reason,actor=actor,status="pending")
    db.add(approval); case.status="awaiting_approval"; _step(db,case_id,"human_approval","Containment proposed; awaiting explicit human approval.")
    db.commit(); return {"case_id":case_id,"approval_id":approval.id,"status":"pending","action":action,"target":target}

def decide_approval(db, approval_id:int, approved:bool, actor="analyst"):
    approval=db.get(InvestigationApproval,approval_id)
    if not approval: raise ValueError(f"Unknown approval '{approval_id}'")
    if approval.status != "pending": raise ValueError(f"Approval already {approval.status}")
    approval.status="approved" if approved else "rejected"; approval.actor=actor; approval.decided_at=_now()
    case=db.query(InvestigationCase).filter(InvestigationCase.case_id==approval.case_id).first()
    if case:
        if approved:
            case.status="containment_approved"; _step(db,case.case_id,"soar_containment","Approved action queued for governed SOAR adapter; this POC performs no external enforcement.")
        else:
            case.status="closed"; _step(db,case.case_id,"closure_learning","Containment rejected; case closed with analyst decision preserved.")
    db.add(AuditEvent(actor=actor,action="investigation_approval_decision",target=approval.case_id,outcome=approval.status))
    db.commit()
    return {"approval_id":approval.id,"status":approval.status,"case_id":approval.case_id}

def serialize_case(db, case):
    approvals=db.query(InvestigationApproval).filter(InvestigationApproval.case_id==case.case_id).order_by(InvestigationApproval.id.desc()).all()
    steps=db.query(InvestigationStep).filter(InvestigationStep.case_id==case.case_id).order_by(InvestigationStep.id.asc()).all()
    return {"case_id":case.case_id,"title":case.title,"status":case.status,"severity":case.severity,
            "risk_score":case.risk_score,"confidence":case.confidence,"target":case.target,"hypothesis":case.hypothesis,
            "evidence":json.loads(case.evidence_json or "[]"),
            "approvals":[{"id":a.id,"action":a.action,"target":a.target,"status":a.status,"reason":a.reason} for a in approvals],
            "steps":[{"step":s.step,"status":s.status,"summary":s.summary} for s in steps]}

def list_cases(db, limit=50):
    return [serialize_case(db,c) for c in db.query(InvestigationCase).order_by(InvestigationCase.updated_at.desc()).limit(limit).all()]
