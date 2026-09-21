"""AegisX AI/agent security control catalog and safe assessment primitives."""
from __future__ import annotations
from datetime import datetime, timezone

AI_SECURITY_TOOLS = [
    {"name":"Garak","kind":"red_eval","coverage":["prompt injection","jailbreak","data leakage","hallucination"],"profile":"isolated_ai_worker"},
    {"name":"Promptfoo","kind":"red_eval","coverage":["LLM eval","agent eval","regression"],"profile":"isolated_ai_worker"},
    {"name":"NeuralTrust","kind":"runtime_platform","coverage":["agent runtime","AI gateway","posture","red teaming"],"profile":"approved_connector"},
    {"name":"Lakera Guard / Check Point AI Guardrails","kind":"runtime_guardrail","coverage":["prompt injection","jailbreak","data leakage","tool-call policy"],"profile":"approved_connector"},
    {"name":"TrojAI","kind":"model_security","coverage":["model vulnerability","adversarial testing","model integrity"],"profile":"approved_connector"},
    {"name":"CalypsoAI / F5 AI Security","kind":"runtime_security","coverage":["inference protection","guardrails","AI security API"],"profile":"approved_connector"},
    {"name":"Adversarial Robustness Toolbox","kind":"ml_security","coverage":["evasion","poisoning","extraction","adversarial ML"],"profile":"isolated_ai_worker"},
    {"name":"HiddenLayer","kind":"model_security","coverage":["model security","ML supply chain","AI threat detection"],"profile":"approved_connector"},
    {"name":"Robust Intelligence","kind":"model_security","coverage":["AI validation","model security","runtime controls"],"profile":"approved_connector"},
    {"name":"NeMo Guardrails","kind":"guardrails","coverage":["policy","dialogue safety","tool controls"],"profile":"approved_worker"},
]

CONTROL_DOMAINS = [
    ("Prompt & Context Integrity","Direct/indirect prompt injection, jailbreaks, poisoned retrieved content, system-prompt leakage."),
    ("Agent Identity & Least Privilege","Per-agent identity, short-lived credentials, tool allowlists, delegated permissions and approval boundaries."),
    ("Tool & MCP Security","Tool inventory, schema validation, untrusted tool-result handling, SSRF/data-egress policy and runtime approvals."),
    ("Memory Security","Short/long-term memory poisoning, provenance, retention, rollback and cross-tenant isolation."),
    ("RAG & Data Security","Document provenance, retrieval authorization, sensitive-data filtering, vector-store isolation and poisoning detection."),
    ("Model & Supply Chain","Model provenance, hashes, model registry, AIBOM/AI-SBOM, dataset lineage, dependency and artifact scanning."),
    ("Training & Fine-tuning","Poisoning, backdoors, unsafe adapters, unauthorized datasets and reproducibility checks."),
    ("Agent-to-Agent Trust","Message authentication, identity, delegation, replay protection and policy enforcement for A2A workflows."),
    ("Observability & Evidence","OpenTelemetry GenAI traces, tool calls, model metadata, approvals, decisions and evidence bundles."),
    ("Runtime Governance","OWASP ACS-style middleware controls, circuit breakers, cost limits, human approval and kill switches."),
]

def catalog():
    return AI_SECURITY_TOOLS

def controls():
    return [{"domain":d,"description":desc} for d,desc in CONTROL_DOMAINS]

def assess_agent(agent: dict) -> dict:
    """Deterministic posture assessment; no attack payloads are generated."""
    checks=[]
    def check(name, ok, severity, rationale): checks.append({"control":name,"pass":bool(ok),"severity":severity,"rationale":rationale})
    check("Approval boundary", agent.get("approval_boundary", False), "HIGH", "High-impact actions should require an explicit approval boundary.")
    check("Tool allowlist", bool(agent.get("tool_allowlist")), "HIGH", "Agents should not receive an unrestricted tool set.")
    check("Short-lived identity", agent.get("short_lived_identity", False), "HIGH", "Agent credentials should be short-lived and scoped.")
    check("Memory provenance", agent.get("memory_provenance", False), "MEDIUM", "Memory writes should retain source and integrity metadata.")
    check("RAG authorization", agent.get("rag_authorization", False), "HIGH", "Retrieval must enforce document/tenant authorization before context assembly.")
    check("Runtime telemetry", agent.get("otel", False), "MEDIUM", "Trace model, tool, MCP/A2A and side-effect events.")
    check("Human approval for side effects", agent.get("human_approval", False), "HIGH", "High-impact external side effects should be approval-gated.")
    check("Supply-chain provenance", agent.get("supply_chain_provenance", False), "MEDIUM", "Track model, prompt, skill, tool, dataset and dependency provenance.")
    failed=sum(not x["pass"] for x in checks)
    return {"evaluated_at":datetime.now(timezone.utc).isoformat(),"risk_score":min(100, failed*12+10),"checks":checks,"recommendation":"Prioritize failed HIGH controls before granting autonomous side effects." if failed else "Baseline controls present; continue continuous validation."}
