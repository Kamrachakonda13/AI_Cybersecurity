"""Agent classification — Gen AI vs Agentic AI vs internal tool agents + why active.

Classifies agents observed in AgentRuntimeEvent / AgentPolicy / PentestAgentPlan
and explains why each is active (policy, recent trace, risk, hypothesis).
"""
from __future__ import annotations

import json
from collections import defaultdict

AGENT_CLASSES = ["Gen AI", "Agentic AI", "Internal Tool Agent", "Unknown"]


def classify_agent(agent_id: str, policy: dict | None = None, recent_ops: list[str] | None = None) -> dict:
    """Heuristic classification from agent_id + policy + observed operations."""
    lower = agent_id.lower()
    ops = set(recent_ops or [])
    # tool agents: dispatchers/merlin/nmap wrappers
    if any(k in lower for k in ("dispatcher", "merlin", "nmap", "worker", "tool")):
        klass = "Internal Tool Agent"
        reason = "Tool dispatch / worker — executes security tools via governed execution_plane"
    elif any(k in lower for k in ("mcp", "a2a", "rag", "memory", "delegation", "autonomous")) or "execute_tool" in ops:
        klass = "Agentic AI"
        reason = "Autonomous tool use / multi-step delegation (MCP/A2A/RAG) observed"
    elif any(k in lower for k in ("llm", "gpt", "claude", "gemini", "model", "eval", "prompt")) or ops & {"chat", "retrieval", "plan"}:
        klass = "Gen AI"
        reason = "LLM-centric operations (chat/retrieval/plan/evaluation) — no autonomous tool delegation"
    else:
        klass = "Unknown"
        reason = "Insufficient telemetry to classify"
    return {"agent_id": agent_id, "class": klass, "reason": reason, "policy": policy, "recent_ops": sorted(ops)}


def why_active(agent_id: str, db) -> dict:
    """Collect evidence for why an agent is active."""
    from app.models import AgentRuntimeEvent, AgentPolicy, InvestigationCase, PentestAgentPlan

    events = db.query(AgentRuntimeEvent).filter(AgentRuntimeEvent.agent_id == agent_id).order_by(AgentRuntimeEvent.created_at.desc()).limit(10).all()
    policy = db.query(AgentPolicy).filter(AgentPolicy.agent_id == agent_id).first()
    cases = db.query(InvestigationCase).filter(InvestigationCase.hypothesis.like(f"%{agent_id}%")).limit(3).all()
    plans = db.query(PentestAgentPlan).filter(PentestAgentPlan.agent_id == agent_id).limit(3).all()

    recent_ops = [e.operation for e in events]
    risk = max((e.risk_score for e in events), default=0)
    last_decision = events[0].policy_decision if events else "no events"
    trace_ids = [e.trace_id for e in events[:3]]

    bullets = []
    if policy:
        bullets.append(f"Policy enabled={policy.enabled}, allowed_tools={policy.allowed_tools[:80]}")
    if events:
        bullets.append(f"Last {len(events)} events: {', '.join(recent_ops[:5])} — latest decision {last_decision} risk {risk}")
    if trace_ids:
        bullets.append(f"Traces: {', '.join(trace_ids)}")
    if cases:
        bullets.append(f"Linked to {len(cases)} investigation case(s): {[c.case_id for c in cases]}")
    if plans:
        bullets.append(f"Has {len(plans)} pentest plan(s): {[p.plan_id for p in plans]}")
    if not bullets:
        bullets.append("No recent telemetry — agent registered but idle / awaiting worker claim")

    is_active = bool(events and (events[0].created_at and True)) or bool(policy and policy.enabled)
    # active if event in last 24h or policy enabled
    try:
        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)
        active_window = any((now - e.created_at).total_seconds() < 86400 for e in events) if events else False
        is_active = active_window or (policy.enabled if policy else False)
    except Exception:
        pass

    classification = classify_agent(agent_id, policy={"enabled": policy.enabled} if policy else None, recent_ops=recent_ops)
    return {"agent_id": agent_id, "is_active": is_active, "classification": classification["class"], "classification_reason": classification["reason"], "evidence": bullets, "recent_ops": recent_ops, "risk_score": risk, "policy": {"enabled": policy.enabled if policy else False}}


def overview(db) -> dict:
    from app.models import AgentRuntimeEvent, AgentPolicy, PentestAgentPlan

    agents = set()
    for (aid,) in db.query(AgentRuntimeEvent.agent_id).distinct().all():
        agents.add(aid)
    for (aid,) in db.query(AgentPolicy.agent_id).distinct().all():
        agents.add(aid)
    for (aid,) in db.query(PentestAgentPlan.agent_id).distinct().all():
        agents.add(aid)

    by_class = defaultdict(list)
    details = []
    for aid in sorted(agents):
        w = why_active(aid, db)
        by_class[w["classification"]].append(aid)
        details.append(w)

    return {
        "total_agents": len(agents),
        "by_class": {k: len(v) for k, v in by_class.items()},
        "agents": details[:50],  # cap
        "classes": AGENT_CLASSES,
        "note": "Gen AI = LLM chat/retrieval; Agentic AI = autonomous tool/MCP/A2A; Internal Tool Agent = security tool workers (nmap etc). Why active = policy + traces + cases.",
    }
