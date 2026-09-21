"""VEYRA v5.0 unified trust control plane.

All decisions are advisory/control-plane contracts. This module never executes
shell commands, network attacks, credential operations, persistence, C2, or
other external actions. Enforcement belongs to authorized managed workers and
external identity/network policy points.
"""
from __future__ import annotations
import hashlib, json, uuid
from datetime import datetime, timezone

TRUST_INVARIANT = (
    "No tool, model, agent, MCP server, artifact or update becomes trusted merely "
    "because it exists. It must establish identity, provenance, integrity, policy "
    "compliance, validation, controlled deployment and observable runtime behavior."
)
GATES = [
    "identity", "provenance", "integrity", "policy_compliance", "validation",
    "deployment_control", "runtime_attestation", "behavioral_baseline",
    "trajectory_assurance", "evidence_integrity", "circuit_breaker_readiness",
]
ASSET_TYPES = [
    "model", "model_adapter", "dataset", "prompt_package", "agent", "mcp_server",
    "a2a_endpoint", "tool", "rag_corpus", "vector_index", "embedding_model",
    "gateway", "skill", "agent_card", "deployment_wrapper", "metadata"
]


def _now(): return datetime.now(timezone.utc)
def _sha(payload): return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def evaluate_asset(asset: dict) -> dict:
    """Evaluate an AI supply-chain asset without trusting presence/registration."""
    checks = {
        "identity": bool(asset.get("publisher") or asset.get("issuer") or asset.get("runtime_identity")),
        "provenance": bool(asset.get("provenance_uri") or asset.get("provenance")),
        "integrity": bool(asset.get("digest")),
        "policy_compliance": asset.get("policy_status", "pending") in {"approved", "compliant", "verified"},
        "validation": asset.get("validation_status", "pending") in {"passed", "verified"},
        "deployment_control": asset.get("deployment_status", "pending") in {"controlled", "approved"},
        "runtime_attestation": bool(asset.get("runtime_attestation") or asset.get("runtime_identity")),
        "behavioral_baseline": bool(asset.get("behavior_baseline")),
        "trajectory_assurance": bool(asset.get("trajectory_policy")),
        "evidence_integrity": bool(asset.get("evidence_sha256")),
        "circuit_breaker_readiness": bool(asset.get("circuit_breaker_id")),
    }
    passed = sum(checks.values())
    status = "trusted" if passed == len(GATES) else ("conditional" if passed >= 7 else "untrusted")
    return {"status": status, "score": round(passed / len(GATES) * 100, 1), "checks": checks, "missing": [k for k,v in checks.items() if not v]}

def make_aibom(asset: dict, components: list[dict]) -> dict:
    doc = {
        "format": "VEYRA-AIBOM-1.0",
        "generated_at": _now().isoformat(),
        "root": {k: asset.get(k, "") for k in ("asset_id","asset_type","name","version","digest","publisher")},
        "components": components,
    }
    doc["document_sha256"] = _sha(doc)
    return doc

def evaluate_trajectory(events: list[dict], policy: dict | None = None) -> dict:
    """Trajectory-level control: individual allowed calls do not imply an allowed chain."""
    policy = policy or {}
    allowed_tools = set(policy.get("allowed_tools", []))
    allowed_destinations = set(policy.get("allowed_destinations", []))
    violations=[]
    previous=None
    for i, event in enumerate(events):
        tool=event.get("tool") or event.get("action")
        dest=event.get("destination")
        if allowed_tools and tool and tool not in allowed_tools:
            violations.append({"index":i,"type":"tool_not_allowlisted","tool":tool})
        if allowed_destinations and dest and dest not in allowed_destinations:
            violations.append({"index":i,"type":"destination_not_allowlisted","destination":dest})
        if event.get("approval_required") and not event.get("approved"):
            violations.append({"index":i,"type":"missing_approval"})
        if previous and previous.get("identity") and event.get("identity") and previous["identity"] != event["identity"] and not event.get("delegation"):
            violations.append({"index":i,"type":"unexpected_identity_transition"})
        previous=event
    score=max(0,100-len(violations)*18)
    return {"trajectory_id":"traj_"+uuid.uuid4().hex[:16],"status":"pass" if not violations else "fail","score":score,"events":len(events),"violations":violations,"evidence_sha256":_sha({"events":events,"violations":violations})}

def trust_decision(asset: dict, trajectory: dict | None = None) -> dict:
    evaluation=evaluate_asset(asset)
    trajectory_ok=not trajectory or trajectory.get("status")=="pass"
    decision="allow" if evaluation["status"]=="trusted" and trajectory_ok else ("approval_required" if evaluation["status"]=="conditional" and trajectory_ok else "deny")
    return {"decision_id":"dec_"+uuid.uuid4().hex[:16],"decision":decision,"asset_score":evaluation["score"],"trajectory_ok":trajectory_ok,"reason":"; ".join(evaluation["missing"]) or "all trust gates satisfied"}

def build_trust_graph(assets: list[dict], relationships: list[dict]) -> dict:
    nodes=[]
    for a in assets:
        ev=evaluate_asset(a)
        nodes.append({"id":a.get("asset_id"),"type":a.get("asset_type"),"label":a.get("name"),"trust":ev["status"],"score":ev["score"]})
    return {"graph_version":"5.0","nodes":nodes,"edges":relationships,"node_count":len(nodes),"edge_count":len(relationships)}

def overview(db):
    from ..models import AISupplyChainAsset, AgentCircuitBreaker, TrustDecisionRecord, TrustGraphNode
    return {
        "platform":"VEYRA Autonomous Security Control Plane",
        "version":"5.0.0",
        "trust_invariant":TRUST_INVARIANT,
        "gates":GATES,
        "asset_types":ASSET_TYPES,
        "ai_assets":db.query(AISupplyChainAsset).count(),
        "trust_decisions":db.query(TrustDecisionRecord).count(),
        "graph_nodes":db.query(TrustGraphNode).count(),
        "armed_circuit_breakers":db.query(AgentCircuitBreaker).filter(AgentCircuitBreaker.state=="armed").count(),
        "control_modes":["observe","approval_required","enforce","emergency_stop"],
        "integrations":["SLSA","Sigstore/Cosign","TUF","Syft","Grype","SPIFFE/SPIRE","MCP","A2A","SCITT-style transparency","SBOM/AIBOM"],
    }

# v5.0 Enterprise Completion Layer: identity, gateway, MCP drift, memory,
# transaction assurance, behavior baselines and digital-twin analysis.
def _decision_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:16]}"

def evaluate_agent_authority(authority: dict) -> dict:
    checks = {
        "agent_identity": bool(authority.get("agent_id") and authority.get("issuer")),
        "owner": bool(authority.get("owner")),
        "credential_reference": bool(authority.get("credential_ref")),
        "delegation_chain": isinstance(authority.get("delegation_chain", []), list),
        "expiration": bool(authority.get("expires_at")),
        "authority_scope": bool(authority.get("allowed_tools") or authority.get("allowed_resources")),
        "revocation_state": authority.get("status", "active") == "active",
    }
    score=round(sum(checks.values())/len(checks)*100,1)
    return {"status":"trusted" if score==100 else ("conditional" if score>=70 else "untrusted"),"score":score,"checks":checks,"missing":[k for k,v in checks.items() if not v]}

def evaluate_gateway_request(request: dict, policy: dict) -> dict:
    reasons=[]
    tool=request.get("tool")
    destination=request.get("destination")
    amount=float(request.get("amount") or 0)
    if policy.get("allowed_tools") and tool not in set(policy.get("allowed_tools", [])): reasons.append("tool_not_allowed")
    if policy.get("allowed_destinations") and destination and destination not in set(policy.get("allowed_destinations", [])): reasons.append("destination_not_allowed")
    if policy.get("transaction_limit", 0) and amount > float(policy["transaction_limit"]): reasons.append("transaction_limit_exceeded")
    if request.get("external") and policy.get("require_approval", True) and not request.get("approved"): reasons.append("human_approval_required")
    decision="deny" if any(x in reasons for x in ("tool_not_allowed","destination_not_allowed")) else ("approval_required" if reasons else "allow")
    return {"decision":decision,"reasons":reasons,"policy_enforced":True,"evidence_sha256":_sha({"request":request,"policy":policy,"reasons":reasons})}

def compare_mcp_fingerprint(previous: dict, current: dict) -> dict:
    fields=("tools_hash","permissions_hash","endpoint_hash","version")
    changed=[f for f in fields if previous.get(f) and current.get(f) and previous.get(f)!=current.get(f)]
    status="trusted" if not changed else "quarantine" if any(f in changed for f in ("permissions_hash","endpoint_hash")) else "approval_required"
    return {"status":status,"changed":changed,"drift_type":"rug_pull_candidate" if changed else "none","evidence_sha256":_sha({"previous":previous,"current":current})}

def evaluate_memory(memory: dict) -> dict:
    score=0; reasons=[]
    if memory.get("content_hash"): score+=25
    else: reasons.append("missing_content_hash")
    if memory.get("provenance"): score+=25
    else: reasons.append("missing_provenance")
    if memory.get("owner"): score+=20
    else: reasons.append("missing_owner")
    poisoning=float(memory.get("poisoning_score") or 0)
    if poisoning < .3: score+=30
    else: reasons.append("poisoning_risk")
    return {"status":"trusted" if score>=90 else ("conditional" if score>=60 else "quarantine"),"score":score,"reasons":reasons,"evidence_sha256":_sha(memory)}

def assess_transaction(tx: dict) -> dict:
    reasons=[]; risk=0
    amount=float(tx.get("amount") or 0)
    ceiling=float(tx.get("transaction_ceiling") or 0)
    if ceiling and amount>ceiling: risk+=45; reasons.append("exceeds_behavioral_ceiling")
    if tx.get("new_destination"): risk+=25; reasons.append("new_destination")
    if tx.get("unusual_time"): risk+=15; reasons.append("unusual_time")
    if tx.get("approval_required") and not tx.get("approved"): risk+=30; reasons.append("missing_approval")
    risk=min(100,risk)
    decision="block" if risk>=70 else ("step_up" if risk>=35 else "allow")
    return {"decision":decision,"risk_score":risk,"reasons":reasons,"evidence_sha256":_sha(tx)}

def compare_behavior(baseline: dict, observed: dict) -> dict:
    deviations=[]
    if baseline.get("tools") and set(observed.get("tools",[]))-set(baseline.get("tools",[])): deviations.append("new_tool")
    if baseline.get("destinations") and set(observed.get("destinations",[]))-set(baseline.get("destinations",[])): deviations.append("new_destination")
    if int(observed.get("delegation_depth",0)) > int(baseline.get("delegation_depth",0)): deviations.append("delegation_depth_increase")
    if baseline.get("transaction_ceiling") and float(observed.get("transaction_amount",0)) > float(baseline["transaction_ceiling"]): deviations.append("transaction_spike")
    score=max(0,100-len(deviations)*25)
    return {"status":"normal" if not deviations else ("suspicious" if score>=50 else "high_risk"),"score":score,"deviations":deviations,"evidence_sha256":_sha({"baseline":baseline,"observed":observed})}

def build_digital_twin(root: str, nodes: list[dict], edges: list[dict]) -> dict:
    adjacency={n.get("id"):[] for n in nodes}
    for e in edges:
        adjacency.setdefault(e.get("source"),[]).append(e.get("target"))
    seen={root}; queue=[root]
    while queue:
        cur=queue.pop(0)
        for nxt in adjacency.get(cur,[]):
            if nxt and nxt not in seen: seen.add(nxt); queue.append(nxt)
    reachable=[n for n in nodes if n.get("id") in seen]
    risk=min(100, round(len(reachable)*8 + sum(1 for n in reachable if n.get("critical"))*12,1))
    options=["quarantine_root_agent","revoke_delegations","disable_high_risk_tools","restrict_egress","preserve_evidence"]
    return {"root_subject":root,"reachable_nodes":reachable,"blast_radius":len(reachable),"risk_score":risk,"containment_options":options,"evidence_sha256":_sha({"root":root,"reachable":reachable,"edges":edges})}
