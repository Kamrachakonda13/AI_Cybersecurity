"""AegisX v3.7 Security Graph Intelligence.

Read-only correlation layer over the existing Security Graph. It adds a
control/evidence view, graph risk hotspots, AI-agent relationships and drift
signals without creating a new execution path.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..services.graph import build_graph, attack_paths
from ..models import Asset, Finding, Incident, Identity, CloudResource, AIAsset, SecurityEvidence, SecurityToolJob, AgentRuntimeEvent, AgentPolicy

CONTROL_MAP = [
    ("asset-inventory", "Asset inventory", ["discover"], ["NIST CSF 2.0 ID.AM"]),
    ("identity-least-privilege", "Identity least privilege", ["identity", "privilege"], ["NIST CSF 2.0 PR.AA", "OWASP Agentic ASI03"]),
    ("external-exposure", "External exposure management", ["internet", "exposure"], ["NIST CSF 2.0 ID.RA", "ATT&CK Initial Access"]),
    ("ai-agent-control", "AI agent runtime control", ["ai", "agent", "tool"], ["OWASP ACS", "OWASP Agentic 2026"]),
    ("supply-chain-provenance", "Software and AI supply-chain provenance", ["sbom", "provenance", "worker"], ["SLSA", "Sigstore", "TUF"]),
    ("detection-coverage", "Detection and telemetry coverage", ["detect", "telemetry", "evidence"], ["NIST CSF 2.0 DE.CM", "MITRE ATT&CK"]),
    ("response-verification", "Response and recovery verification", ["contain", "recover", "verify"], ["NIST CSF 2.0 RS/RC"]),
]

def _counts(db: Session):
    return {
        "assets": db.query(func.count(Asset.id)).scalar() or 0,
        "findings": db.query(func.count(Finding.id)).scalar() or 0,
        "open_findings": db.query(func.count(Finding.id)).filter(Finding.status == "open").scalar() or 0,
        "incidents": db.query(func.count(Incident.id)).scalar() or 0,
        "open_incidents": db.query(func.count(Incident.id)).filter(Incident.status == "open").scalar() or 0,
        "identities": db.query(func.count(Identity.id)).scalar() or 0,
        "cloud_resources": db.query(func.count(CloudResource.id)).scalar() or 0,
        "ai_assets": db.query(func.count(AIAsset.id)).scalar() or 0,
        "jobs": db.query(func.count(SecurityToolJob.id)).scalar() or 0,
        "evidence": db.query(func.count(SecurityEvidence.id)).scalar() or 0,
    }

def _enrich_graph(db, g):
    """Add evidence/control/AI-runtime relationships as a deterministic overlay."""
    nodes, edges = g["nodes"], g["edges"]
    def node(key, **attrs): nodes.setdefault(key, {"id": key, **attrs})
    def edge(src, dst, relation, detail=""):
        if src in nodes and dst in nodes:
            edges.append({"src":src,"dst":dst,"relation":relation,"detail":detail})
    for fin in db.query(Finding).all():
        fk=f"finding:{fin.id}"; node(fk, kind="finding", label=fin.title, severity=fin.severity, risk=fin.risk_score, status=fin.status)
        ak=f"asset:{fin.asset_id}"
        if ak in nodes:
            edge(ak,fk,"has-finding",f"{fin.severity} risk={fin.risk_score}")
    for evi in db.query(SecurityEvidence).all():
        ek=f"evidence:{evi.artifact_id}"; node(ek, kind="evidence", label=evi.artifact_id, sha256=evi.sha256, classification=evi.classification)
        jk=f"job:{evi.job_id}"; node(jk, kind="job", label=evi.job_id)
        edge(jk,ek,"produces-evidence",evi.summary or evi.result_type)
    for job in db.query(SecurityToolJob).all():
        jk=f"job:{job.job_id}"; node(jk, kind="job", label=job.tool, status=job.status, environment=job.environment)
        for token in (str(job.target), str(job.scope)):
            for nkey,n in nodes.items():
                if n.get("kind") in ("asset","cloud","ai") and n.get("label") and n.get("label") in token:
                    edge(jk,nkey,"targets",f"governed job {job.job_id}")
    for p in db.query(AgentPolicy).all():
        pk=f"agent-policy:{p.agent_id}"; node(pk, kind="agent-policy", label=p.agent_id, enabled=p.enabled, max_risk=p.max_risk_score)
        ak=f"ai:{p.agent_id}"
        if ak in nodes: edge(ak,pk,"governed-by","deterministic agent policy")
    for ev in db.query(AgentRuntimeEvent).all():
        rk=f"agent-event:{ev.id}"; node(rk, kind="agent-runtime-event", label=ev.operation, risk=ev.risk_score, decision=ev.policy_decision)
        pk=f"agent-policy:{ev.agent_id}"
        if pk in nodes: edge(pk,rk,"evaluates",f"{ev.operation} tool={ev.tool_name} decision={ev.policy_decision}")
        ak=f"ai:{ev.agent_id}"
        if ak in nodes: edge(ak,rk,"emits-runtime-event",ev.trace_id)
    for control in CONTROL_MAP:
        cid,name,_,refs=control; ck=f"control:{cid}"; node(ck, kind="control", label=name, references=refs)
        for fin in db.query(Finding).all():
            title=(fin.title or "").lower(); blob=f"{title} {fin.description or ''}".lower()
            if any(signal in blob for signal in control[2]): edge(f"finding:{fin.id}",ck,"maps-to-control",name)
    return g

def _graph_summary(g):
    kinds = Counter(n.get("kind", "unknown") for n in g["nodes"].values())
    relations = Counter(e.get("relation", "unknown") for e in g["edges"])
    return {"nodes": len(g["nodes"]), "edges": len(g["edges"]), "node_types": dict(kinds), "relations": dict(relations)}

def _hotspots(g):
    degree = Counter()
    labels = {}
    for n in g["nodes"].values(): labels[n["id"]] = n.get("label", n["id"])
    for e in g["edges"]:
        degree[e["src"]] += 1; degree[e["dst"]] += 1
    rows=[]
    for key,count in degree.most_common(12):
        n=g["nodes"].get(key,{})
        score=0
        if n.get("sensitive"): score += 35
        if n.get("external_exposure") or n.get("public"): score += 30
        if n.get("risk") is not None: score += min(30, float(n.get("risk") or 0)*0.3)
        score += min(20, count*2)
        rows.append({"node":key,"label":labels.get(key,key),"kind":n.get("kind"),"connections":count,"risk_score":round(score,1)})
    return rows

def _control_status(db: Session, counts, g):
    statuses=[]
    exposed=sum(1 for n in g["nodes"].values() if n.get("external_exposure") or n.get("public"))
    ai_nodes=sum(1 for n in g["nodes"].values() if n.get("kind")=="ai")
    for cid,name,signals,refs in CONTROL_MAP:
        if cid=="asset-inventory": ok=counts["assets"]>0
        elif cid=="identity-least-privilege": ok=counts["identities"]>0
        elif cid=="external-exposure": ok=exposed==0 or counts["assets"]>0
        elif cid=="ai-agent-control": ok=ai_nodes==0 or counts["evidence"]>0
        elif cid=="supply-chain-provenance": ok=counts["evidence"]>0 and counts["jobs"]>0
        elif cid=="detection-coverage": ok=counts["evidence"]>0
        else: ok=counts["incidents"]==0 or counts["evidence"]>0
        statuses.append({"id":cid,"name":name,"status":"covered" if ok else "attention","references":refs,"signals":signals})
    return statuses

def _drift(db: Session):
    now=datetime.now(timezone.utc)
    cutoff=now-timedelta(days=30)
    jobs=db.query(SecurityToolJob).filter(SecurityToolJob.created_at >= cutoff).all()
    evidence=db.query(SecurityEvidence).filter(SecurityEvidence.created_at >= cutoff).all()
    stale=[]
    if jobs and not evidence:
        stale.append({"type":"evidence","severity":"high","reason":"Recent governed jobs have no recent evidence receipts."})
    if db.query(Finding).filter(Finding.status=="open", Finding.created_at < cutoff).count():
        stale.append({"type":"finding","severity":"medium","reason":"Open findings older than 30 days require remediation or an approved exception."})
    if db.query(Incident).filter(Incident.status=="open", Incident.created_at < cutoff).count():
        stale.append({"type":"incident","severity":"high","reason":"Open incidents older than 30 days require explicit case review."})
    return stale

def intelligence_overview(db: Session):
    counts=_counts(db); g=_enrich_graph(db, build_graph(db)); paths=attack_paths(db, max_paths=8, max_depth=8)
    controls=_control_status(db, counts, g)
    return {
        "release":"3.7", "generated_at":datetime.now(timezone.utc).isoformat(),
        "inventory":counts, "graph":_graph_summary(g), "hotspots":_hotspots(g),
        "attack_paths":paths["paths"], "chokepoints":paths["chokepoints"],
        "controls":controls, "drift_signals":_drift(db),
        "principle":"Correlate assets, identities, cloud, AI, findings, incidents and evidence into one explainable security graph.",
        "guardrails":["read-only correlation","evidence-backed relationships","no autonomous containment","scope and approval remain authoritative","AI explanations must cite graph/evidence inputs"],
    }

def control_evidence(db: Session):
    o=intelligence_overview(db)
    evidence=db.query(SecurityEvidence).order_by(SecurityEvidence.created_at.desc()).limit(50).all()
    by_job=Counter(e.job_id for e in evidence)
    return {"controls":o["controls"],"evidence_receipts":[{"artifact_id":e.artifact_id,"job_id":e.job_id,"sha256":e.sha256,"source":e.source,"classification":e.classification,"result_type":e.result_type,"created_at":e.created_at.isoformat() if e.created_at else None} for e in evidence],"jobs_with_evidence":len(by_job)}
