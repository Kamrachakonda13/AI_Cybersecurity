"""AegisX Security Fabric: normalize and correlate security planes.

The fabric is deliberately deterministic: it correlates persisted telemetry and
produces explainable paths/risk. LLMs may summarize the output but do not alter
policy, authorization, severity, or evidence provenance.
"""
from __future__ import annotations
import hashlib, json, uuid
from datetime import datetime, timezone


def utc(): return datetime.now(timezone.utc)

def stable_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()

def normalize_event(plane, event_type, actor="", source="", target="", risk_score=0, payload=None, trace_id=""):
    payload = payload or {}
    severity = "CRITICAL" if risk_score >= 90 else "HIGH" if risk_score >= 70 else "MEDIUM" if risk_score >= 40 else "LOW" if risk_score > 0 else "INFO"
    body={"plane":plane,"event_type":event_type,"actor":actor,"source":source,"target":target,"risk_score":risk_score,"payload":payload,"trace_id":trace_id}
    return {"event_id":str(uuid.uuid4()),"trace_id":trace_id,"plane":plane,"event_type":event_type,"actor":actor,"source":source,"target":target,"risk_score":risk_score,"severity":severity,"payload":payload,"event_sha256":stable_hash(body),"observed_at":utc().isoformat()}


def security_fabric_overview(db):
    from ..models import (Asset, Finding, Incident, Identity, CloudResource, AIAsset,
                          NetworkFlow, SecurityToolJob, SecurityEvidence, AgentRuntimeEvent,
                          UnifiedSecurityEvent)
    return {
      "planes": {
        "observation": sum([db.query(Asset).count(), db.query(NetworkFlow).count(), db.query(AgentRuntimeEvent).count()]),
        "detection": db.query(Finding).count(),
        "intelligence": db.query(UnifiedSecurityEvent).count(),
        "response": db.query(Incident).count() + db.query(SecurityToolJob).count(),
        "governance": db.query(Identity).count() + db.query(CloudResource).count() + db.query(AIAsset).count(),
        "evidence": db.query(SecurityEvidence).count(),
      },
      "open_findings": db.query(Finding).filter(Finding.status=="open").count(),
      "open_incidents": db.query(Incident).filter(Incident.status=="open").count(),
      "queued_security_jobs": db.query(SecurityToolJob).filter(SecurityToolJob.status.in_(["approved_for_worker","queued_for_isolated_worker"])).count(),
      "ai_runtime_events": db.query(AgentRuntimeEvent).count(),
    }


def ai_attack_paths(db, max_paths=10):
    """Correlate identity -> agent -> vector/data -> cloud/endpoint as a deterministic graph."""
    from ..models import Identity, AIAsset, Asset, CloudResource, AgentRuntimeEvent, AgentPolicy
    nodes={"internet":{"kind":"internet"}}; edges=[]
    def add(k,kind,label,**kw): nodes.setdefault(k,{"id":k,"kind":kind,"label":label,**kw})
    def edge(a,b,rel,detail): edges.append({"src":a,"dst":b,"relation":rel,"detail":detail})
    for i in db.query(Identity).all(): add(f"identity:{i.username}","identity",i.username,privilege=i.privilege)
    for a in db.query(AIAsset).all(): add(f"ai:{a.name}","ai",a.name,asset_type=a.asset_type,risk=a.risk_score)
    for c in db.query(CloudResource).all(): add(f"cloud:{c.resource_id}","cloud",c.resource_id,risk=c.risk_score)
    for a in db.query(Asset).all(): add(f"asset:{a.id}","asset",a.hostname,criticality=a.criticality)
    for p in db.query(AgentPolicy).all():
        add(f"agent:{p.agent_id}","agent",p.agent_id,enabled=p.enabled)
        if p.enabled:
            for i in db.query(Identity).filter(Identity.privilege>=4).limit(20).all(): edge(f"identity:{i.username}",f"agent:{p.agent_id}","controls","privileged identity can operate enrolled agent")
    for e in db.query(AgentRuntimeEvent).all():
        ak=f"agent:{e.agent_id}"; add(ak,"agent",e.agent_id)
        if e.tool_name: edge(ak,f"tool:{e.tool_name}","invokes",f"runtime operation={e.operation}") ; add(f"tool:{e.tool_name}","tool",e.tool_name)
        for ai in db.query(AIAsset).all():
            if ai.asset_type in ("vector database","AI application","agent") and ai.name.lower() in (e.tool_name or "").lower(): edge(ak,f"ai:{ai.name}","accesses","runtime telemetry name correlation")
    for ai in db.query(AIAsset).all():
        if ai.asset_type == "vector database":
            for other in db.query(AIAsset).all():
                if other.asset_type in ("AI application","agent") and other.name != ai.name: edge(f"ai:{other.name}",f"ai:{ai.name}","retrieves","AI application/agent retrieval relationship")
    return {"nodes":nodes,"edges":edges,"paths":_bfs_paths(nodes,edges,max_paths)}


def _bfs_paths(nodes, edges, max_paths):
    from collections import deque
    adj={}
    for e in edges: adj.setdefault(e["src"],[]).append(e)
    targets={k for k,v in nodes.items() if v.get("kind") in ("cloud","ai") or v.get("criticality",0)>=5}
    q=deque([("identity",["identity"])]); out=[]
    # start from every identity to avoid synthetic internet-only assumptions
    q=deque()
    for k,v in nodes.items():
        if v.get("kind")=="identity": q.append((k,[k]))
    seen=set()
    while q and len(out)<max_paths:
        cur,path=q.popleft()
        if cur in targets and len(path)>1:
            sig=tuple(path)
            if sig not in seen:
                seen.add(sig); out.append(path); continue
        if len(path)>7: continue
        for e in adj.get(cur,[]):
            if e["dst"] not in path: q.append((e["dst"],path+[e["dst"]]))
    return out
