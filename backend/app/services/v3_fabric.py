"""VEYRA v3.0 Full Security Operations Fabric.

This module is an orchestration/read-model layer over existing telemetry. It does not
execute offensive commands or containment actions. High-impact response is represented
as a governed plan for approval and isolated-worker execution.
"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models import Asset, Service, Identity, SessionEvent, NetworkFlow, ThreatIntel, CloudResource, AIAsset, Finding, Incident, AuditEvent, Device, DnsQuery, LoginAttempt, WifiNetwork, UnifiedSecurityEvent

PIPELINE = ["Detect", "Preserve", "Investigate", "Correlate", "Reconstruct", "Enrich", "Attribute", "Contain", "Recover", "Verify", "Learn"]


def _risk_band(score):
    score = float(score or 0)
    return "CRITICAL" if score >= 80 else "HIGH" if score >= 60 else "MEDIUM" if score >= 35 else "LOW"


def _count(db, model):
    return db.query(model).count()


def overview(db: Session):
    findings = db.query(Finding).filter(Finding.status == "open").order_by(Finding.risk_score.desc()).limit(12).all()
    incidents = db.query(Incident).filter(Incident.status == "open").order_by(Incident.created_at.desc()).limit(12).all()
    flows = db.query(NetworkFlow).filter(NetworkFlow.risk_score >= 60).order_by(NetworkFlow.risk_score.desc()).limit(20).all()
    unknown = [x for x in db.query(Device).limit(200).all() if not getattr(x, "trusted", False)]
    return {
        "version": "3.0.0",
        "posture": {"open_findings": _count(db, Finding), "open_incidents": _count(db, Incident), "high_risk_flows": len(flows), "unknown_devices": len(unknown), "cloud_resources": _count(db, CloudResource), "ai_assets": _count(db, AIAsset)},
        "pipeline": PIPELINE,
        "priority_queue": [{"type":"finding","id":x.id,"title":x.title,"severity":x.severity,"risk":x.risk_score,"asset_id":x.asset_id} for x in findings] + [{"type":"incident","id":x.id,"title":x.title,"severity":x.severity,"risk":80 if x.severity=="CRITICAL" else 65 if x.severity=="HIGH" else 45,"asset":x.asset} for x in incidents],
        "control_plane": {"execution":"managed_worker_only","containment":"approval_required","attribution":"hypothesis_only","evidence":"hash_and_chain_of_custody"},
    }


def graph_read_model(db: Session):
    nodes, edges = [], []
    for a in db.query(Asset).limit(200):
        nodes.append({"id":f"asset:{a.id}","type":"asset","label":a.hostname,"risk":a.criticality*20})
    for i in db.query(Identity).limit(200):
        nodes.append({"id":f"identity:{i.id}","type":"identity","label":i.username,"risk":80 if i.privilege>=4 and not i.mfa_enabled else i.privilege*15})
    for ai in db.query(AIAsset).limit(200):
        nodes.append({"id":f"ai:{ai.id}","type":"ai","label":ai.name,"risk":ai.risk_score})
    for c in db.query(CloudResource).limit(200):
        nodes.append({"id":f"cloud:{c.id}","type":"cloud","label":c.resource_id,"risk":c.risk_score})
    for f in db.query(NetworkFlow).limit(300):
        if f.src_asset_id: edges.append({"source":f"asset:{f.src_asset_id}","target":f"ip:{f.dst_ip}","type":"flow","risk":f.risk_score})
    for s in db.query(Service).limit(300):
        edges.append({"source":f"asset:{s.asset_id}","target":f"service:{s.id}","type":"exposes","risk":0 if s.expected else 70})
    return {"nodes":nodes,"edges":edges,"legend":["asset","identity","ai","cloud","service","ip"],"note":"Read-model graph. Causal conclusions require evidence correlation."}


def attack_reconstruction(db: Session, limit=50):
    events=[]
    for f in db.query(Finding).filter(Finding.status=="open").order_by(Finding.created_at.asc()).limit(limit):
        events.append({"time":f.created_at.isoformat(),"stage":"detect","source":"finding","actor":"unknown","target":f"asset:{f.asset_id}","risk":f.risk_score,"detail":f.title})
    for s in db.query(SessionEvent).order_by(SessionEvent.started_at.asc()).limit(limit):
        events.append({"time":s.started_at.isoformat(),"stage":"access","source":"session","actor":s.username,"target":f"asset:{s.asset_id}","risk":s.anomaly_score*100,"detail":f"{s.application} via {s.auth_method}"})
    for f in db.query(NetworkFlow).filter(NetworkFlow.risk_score>=50).order_by(NetworkFlow.observed_at.asc()).limit(limit):
        events.append({"time":f.observed_at.isoformat(),"stage":"movement_or_egress","source":"network_flow","actor":f.src_ip,"target":f"{f.dst_ip}:{f.dst_port}","risk":f.risk_score,"detail":f"{f.bytes_out} bytes; action={f.action}"})
    for a in db.query(AuditEvent).order_by(AuditEvent.created_at.asc()).limit(limit):
        events.append({"time":a.created_at.isoformat(),"stage":"control","source":"audit","actor":a.actor,"target":a.target,"risk":0,"detail":f"{a.action}: {a.outcome}"})
    events.sort(key=lambda x:x["time"])
    return {"events":events[-limit:],"confidence":"correlation_only","warning":"Timestamp ordering is not proof of causality; preserve raw source evidence."}


def ai_investigation(db: Session):
    high_findings = db.query(Finding).filter(Finding.risk_score>=60, Finding.status=="open").count()
    high_flows = db.query(NetworkFlow).filter(NetworkFlow.risk_score>=70).count()
    anomalous_sessions = db.query(SessionEvent).filter(SessionEvent.anomaly_score>=0.7).count()
    public_cloud = db.query(CloudResource).filter(CloudResource.public_exposure==True).count()
    risky_ai = db.query(AIAsset).filter(AIAsset.risk_score>=60).count()
    signals=[]
    if high_findings: signals.append({"signal":"high_risk_findings","count":high_findings,"priority":90})
    if high_flows: signals.append({"signal":"high_risk_network_flows","count":high_flows,"priority":85})
    if anomalous_sessions: signals.append({"signal":"anomalous_sessions","count":anomalous_sessions,"priority":80})
    if public_cloud: signals.append({"signal":"public_cloud_resources","count":public_cloud,"priority":75})
    if risky_ai: signals.append({"signal":"risky_ai_assets","count":risky_ai,"priority":78})
    signals.sort(key=lambda x:x["priority"], reverse=True)
    return {"signals":signals,"reasoning_steps":["preserve evidence","correlate deterministic signals","construct attack path","enrich with internal/external intelligence","produce competing hypotheses","request human verification"],"guardrails":["no autonomous attribution","no hack-back","no destructive response","no arbitrary shell"]}


def response_plan(db: Session, incident_id: int | None = None):
    incident = db.query(Incident).filter(Incident.id==incident_id).first() if incident_id else db.query(Incident).filter(Incident.status=="open").order_by(Incident.created_at.desc()).first()
    if not incident:
        return {"status":"no_open_incident","actions":[]}
    actions=[
        {"id":"preserve","name":"Preserve evidence","mode":"read_only","approval":"not_required","verification":"hash artifacts"},
        {"id":"isolate","name":"Isolate affected host","mode":"governed_response","approval":"required","verification":"confirm isolation state"},
        {"id":"identity","name":"Revoke suspicious sessions/tokens","mode":"governed_response","approval":"required","verification":"confirm sessions revoked"},
        {"id":"network","name":"Block confirmed malicious indicator","mode":"governed_response","approval":"required","verification":"confirm policy propagation"},
        {"id":"recover","name":"Recovery verification","mode":"read_only","approval":"not_required","verification":"re-scan and compare baseline"},
    ]
    return {"incident":{"id":incident.id,"title":incident.title,"severity":incident.severity,"status":incident.status,"asset":incident.asset},"actions":actions,"execution":"staged_only; dispatch requires policy/approval and managed worker","plan_sha256_hint":"hash the canonical JSON plan before approval"}


def recovery_check(db: Session, incident_id: int | None = None):
    open_findings=db.query(Finding).filter(Finding.status=="open").count()
    drift=db.query(Service).filter(Service.expected==False).count()
    highflows=db.query(NetworkFlow).filter(NetworkFlow.risk_score>=70).count()
    return {"incident_id":incident_id,"checks":[
        {"name":"open_high_risk_findings","pass":open_findings==0,"value":open_findings},
        {"name":"unexpected_services","pass":drift==0,"value":drift},
        {"name":"high_risk_flows","pass":highflows==0,"value":highflows},
    ],"overall":"ready_for_review" if open_findings==0 and drift==0 and highflows==0 else "not_verified","note":"Recovery verification is a recommendation/read-model; it does not alter hosts."}
