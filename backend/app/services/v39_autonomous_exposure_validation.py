"""AegisX v3.9 — Autonomous Exposure Validation Fabric.

This service is intentionally an analysis/validation planner. It correlates
managed endpoint, identity, network, finding, AI-agent and evidence telemetry;
AI may rank hypotheses, but deterministic telemetry is authoritative. No
arbitrary commands, persistence, credential attacks, exploit delivery or
hack-back are exposed here.
"""
from __future__ import annotations
import json, hashlib
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.orm import Session
from ..models import (Asset, Device, Finding, Identity, SessionEvent, NetworkFlow,
                      AIAsset, AgentRuntimeEvent, AgentPolicy, SecurityEvidence,
                      UnifiedSecurityEvent, RogueAgentCase)

PLATFORMS = ["Windows", "macOS", "Linux", "Kubernetes", "Cloud", "AI Agent"]

SIGNALS = {
    "agent_identity_mismatch": 28,
    "tool_not_allowlisted": 30,
    "policy_bypass": 35,
    "high_risk_agent_action": 24,
    "credential_anomaly": 24,
    "endpoint_vulnerability": 22,
    "unexpected_egress": 20,
    "multi_agent_coordination": 25,
    "after_hours": 8,
}

def _j(s, default):
    try: return json.loads(s or "{}")
    except Exception: return default

def _score_reasons(score):
    return max(0, min(100, score))

def _agent_anomalies(db):
    policies={p.agent_id:p for p in db.query(AgentPolicy).all()}
    events=db.query(AgentRuntimeEvent).order_by(AgentRuntimeEvent.created_at.asc()).all()
    by={}
    for e in events:
        by.setdefault(e.agent_id, []).append(e)
    rows=[]
    for agent, evs in by.items():
        p=policies.get(agent); score=0; reasons=[]; first=evs[0].created_at; last=evs[-1].created_at
        providers={e.provider for e in evs if e.provider}; tools={e.tool_name for e in evs if e.tool_name}
        if not p:
            score += SIGNALS["agent_identity_mismatch"]; reasons.append("agent is not present in the registered policy set")
        for e in evs:
            if p and e.tool_name and e.tool_name not in _j(p.allowed_tools, []):
                score += SIGNALS["tool_not_allowlisted"]; reasons.append(f"tool outside allowlist: {e.tool_name}")
            if e.policy_decision.lower() in {"deny","blocked","approval_required"}:
                score += SIGNALS["policy_bypass"]; reasons.append(f"policy decision {e.policy_decision}")
            if float(e.risk_score or 0) >= 80:
                score += SIGNALS["high_risk_agent_action"]; reasons.append(f"high-risk runtime event {e.operation}")
        # Coordination signal: many traces/tools/providers for one identity.
        if len({e.trace_id for e in evs}) >= 3 and len(tools) >= 3:
            score += SIGNALS["multi_agent_coordination"]; reasons.append("diverse tool/trace activity suggests coordinated work")
        rows.append({"agent_id":agent,"score":_score_reasons(score),"events":len(evs),"first_seen":first.isoformat(),"last_seen":last.isoformat(),"providers":sorted(providers),"tools":sorted(tools),"reasons":sorted(set(reasons))})
    return sorted(rows,key=lambda x:x["score"],reverse=True)

def _endpoint_exposure(db):
    findings=db.query(Finding).all(); devices=db.query(Device).all()
    out=[]
    for d in devices:
        hits=[]
        for f in findings:
            if f.asset_id and d.hostname and str(f.asset_id)==str(d.id):
                hits.append(f)
        out.append({"hostname":d.hostname,"os":d.os,"ip":d.ip_address,"last_seen":d.last_seen.isoformat() if d.last_seen else "","findings":len(hits),"critical":sum(1 for f in hits if str(f.severity).upper()=="CRITICAL"),"kev":sum(1 for f in hits if f.kev)})
    return out

def _identity_anomalies(db):
    rows=db.query(SessionEvent).order_by(SessionEvent.started_at.desc()).limit(250).all(); out=[]
    for s in rows:
        if float(s.anomaly_score or 0)>=0.7 or s.privileged:
            out.append({"username":s.username,"source_ip":s.source_ip,"asset_id":s.asset_id,"application":s.application,"privileged":s.privileged,"anomaly_score":s.anomaly_score,"started_at":s.started_at.isoformat()})
    return out

def exposure_overview(db):
    agents=_agent_anomalies(db); endpoints=_endpoint_exposure(db); identities=_identity_anomalies(db)
    critical=sum(1 for x in agents if x["score"]>=70)
    vulnerable=sum(1 for x in endpoints if x["critical"] or x["kev"])
    return {"release":"3.9","fabric":"Autonomous Exposure Validation Fabric","platforms":PLATFORMS,"counts":{"assets":db.query(Asset).count(),"devices":db.query(Device).count(),"findings":db.query(Finding).count(),"ai_assets":db.query(AIAsset).count(),"agent_events":db.query(AgentRuntimeEvent).count(),"evidence":db.query(SecurityEvidence).count(),"security_events":db.query(UnifiedSecurityEvent).count()},"rogue_agent_candidates":agents[:25],"endpoint_exposure":endpoints[:50],"identity_anomalies":identities[:50],"risk_summary":{"critical_agent_candidates":critical,"vulnerable_endpoints":vulnerable},"guardrails":["Managed/authorized assets only","No arbitrary command execution from SaaS","No credential theft or persistence","No exploit delivery or hack-back","Containment is staged for human approval","Evidence receipts are authoritative"]}

def _containment_plan(candidate):
    return [
      {"step":1,"action":"Preserve evidence","detail":"Freeze relevant runtime, identity, endpoint, network and audit telemetry; hash exported evidence."},
      {"step":2,"action":"Quarantine the agent identity","detail":"Stage revocation of the agent/session/API credential through the approved identity control plane."},
      {"step":3,"action":"Constrain the endpoint","detail":"Stage network isolation or application quarantine for the affected managed endpoint; require human approval."},
      {"step":4,"action":"Close the initial access path","detail":"Patch or mitigate confirmed OS/application exposure and remove unauthorized tool/MCP/A2A trust."},
      {"step":5,"action":"Hunt laterally","detail":"Search the same agent identity, credential, IP, trace, tool and artifact fingerprints across the tenant."},
      {"step":6,"action":"Verify recovery","detail":"Re-run deterministic endpoint, identity and agent-control checks and require fresh evidence receipts."},
    ]

def investigate_agent(db, agent_id):
    events=db.query(AgentRuntimeEvent).filter(AgentRuntimeEvent.agent_id==agent_id).order_by(AgentRuntimeEvent.created_at.asc()).all()
    policy=db.query(AgentPolicy).filter(AgentPolicy.agent_id==agent_id).first()
    if not events: return {"status":"not_found","agent_id":agent_id}
    first,last=events[0],events[-1]; anomalies=_agent_anomalies(db); cand=next((x for x in anomalies if x["agent_id"]==agent_id),None) or {"score":0,"reasons":[]}
    evidence=[]
    for e in events:
        evidence.append({"type":"agent_runtime_event","id":e.id,"trace_id":e.trace_id,"operation":e.operation,"provider":e.provider,"model":e.model,"tool":e.tool_name,"policy":e.policy_decision,"risk":e.risk_score,"created_at":e.created_at.isoformat()})
    root=[]
    if not policy: root.append("unregistered agent identity")
    if any(e.policy_decision.lower() in {"deny","blocked"} for e in events): root.append("policy boundary encountered")
    if any(float(e.risk_score or 0)>=80 for e in events): root.append("high-risk runtime behavior")
    case_id="rag_"+uuid4().hex[:20]
    plan=_containment_plan(cand)
    case=RogueAgentCase(case_id=case_id,confidence=min(1,cand["score"]/100),agent_identity=agent_id,suspected_provider=first.provider or "unknown",first_seen=first.created_at.isoformat(),last_seen=last.created_at.isoformat(),root_cause="; ".join(root) or "insufficient deterministic evidence",evidence_json=json.dumps(evidence),timeline_json=json.dumps(evidence),recommended_actions_json=json.dumps(plan))
    db.add(case); db.commit()
    digest=hashlib.sha256(json.dumps(evidence,sort_keys=True,default=str).encode()).hexdigest()
    return {"status":"investigating","case_id":case_id,"agent_id":agent_id,"confidence":case.confidence,"first_seen":case.first_seen,"last_seen":case.last_seen,"suspected_provider":case.suspected_provider,"root_cause":case.root_cause,"timeline":evidence,"evidence_sha256":digest,"containment_plan":plan,"security_boundary":"Plan only; execution requires existing approval-gated response controls."}

def cases(db):
    rows=db.query(RogueAgentCase).order_by(RogueAgentCase.created_at.desc()).limit(100).all()
    return {"cases":[{"case_id":r.case_id,"status":r.status,"confidence":r.confidence,"agent_identity":r.agent_identity,"provider":r.suspected_provider,"first_seen":r.first_seen,"last_seen":r.last_seen,"root_cause":r.root_cause,"created_at":r.created_at.isoformat()} for r in rows]}

def validation_matrix(db):
    return {"checks":[
      {"id":"asset-fingerprint","name":"Continuous asset fingerprinting","platforms":PLATFORMS,"evidence":["OS/build/package inventory","agent inventory","cloud/K8s resource inventory"]},
      {"id":"vulnerability-correlation","name":"Vulnerability/advisory correlation","platforms":["Windows","macOS","Linux","Kubernetes","Cloud"],"evidence":["vendor advisory","installed version/build","CVE/KEV mapping"]},
      {"id":"agent-runtime","name":"Agent runtime integrity","platforms":["AI Agent"],"evidence":["agent identity","tool calls","policy decision","trace ID","provider/model"]},
      {"id":"identity-chain","name":"Identity and credential chain","platforms":PLATFORMS,"evidence":["session","source IP","MFA","privilege","credential lifecycle"]},
      {"id":"attack-path","name":"Attack-path exposure","platforms":PLATFORMS,"evidence":["graph relationships","flows","findings","identity edges"]},
      {"id":"remediation-proof","name":"Independent remediation proof","platforms":PLATFORMS,"evidence":["before snapshot","after snapshot","fresh worker receipt","verification result"]},
    ]}
