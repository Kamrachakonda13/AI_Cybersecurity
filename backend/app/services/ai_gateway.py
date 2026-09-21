"""VEYRA AI Security Gateway: deterministic policy + telemetry boundary.

This is a control-plane reference gateway, not a model provider. It evaluates
requests from approved internal agents before model/tool/memory side effects.
It never executes arbitrary tools and never generates offensive payloads.
"""
from __future__ import annotations
import hashlib, json, re, uuid
from datetime import datetime, timezone

SENSITIVE_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?previous\s+instructions",
    r"(?i)reveal\s+(the\s+)?system\s+prompt",
    r"(?i)show\s+(me\s+)?(secrets|credentials|api\s+keys)",
    r"(?i)disable\s+(security|guardrails|policy)",
]
HIGH_IMPACT_TOOLS = {"shell", "exec", "delete", "send_email", "rotate_credentials", "isolate_host", "block_ip"}


def utc(): return datetime.now(timezone.utc).isoformat()

def content_risk(text: str) -> tuple[int, list[str]]:
    hits=[]
    for p in SENSITIVE_PATTERNS:
        if re.search(p, text or ""): hits.append(p)
    return min(100, len(hits)*25), hits

def decide(req: dict, policy: dict) -> dict:
    operation=req.get("operation", "chat")
    tool=req.get("tool_name", "")
    text=json.dumps(req.get("input", ""), default=str)
    score,hits=content_risk(text)
    reasons=[]
    if operation not in policy["allowed_operations"]:
        return {"decision":"deny","risk_score":100,"reasons":["operation_not_allowed"]}
    if tool and tool not in policy["allowed_tools"]:
        return {"decision":"deny","risk_score":100,"reasons":["tool_not_allowlisted"]}
    if tool in HIGH_IMPACT_TOOLS:
        score=max(score,80)
        reasons.append("high_impact_tool")
        if policy["require_human_approval"]:
            return {"decision":"approval_required","risk_score":score,"reasons":reasons+hits}
    if hits:
        reasons.extend(["prompt_injection_or_secret_request"])
    if score > policy["max_risk_score"]:
        return {"decision":"deny","risk_score":score,"reasons":reasons+['risk_threshold_exceeded']}
    return {"decision":"allow","risk_score":score,"reasons":reasons}

def trace_id(): return str(uuid.uuid4())

def event_hash(event: dict) -> str:
    return hashlib.sha256(json.dumps(event, sort_keys=True, default=str).encode()).hexdigest()
