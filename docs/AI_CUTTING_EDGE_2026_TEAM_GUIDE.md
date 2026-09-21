# VEYRA — Cutting-Edge AI Hacking, Red-Team & Defensive Security Team Guide (2026)

## Purpose

This guide defines the minimum AI-security knowledge and tooling baseline for an VEYRA security team. The goal is **understand → test safely → detect → investigate → harden → verify**.

Do not interpret “AI hacking” as permission to attack third-party systems. VEYRA is designed for owned systems, explicitly authorized assessments and isolated labs.

## Why this area is now mandatory

Modern AI systems are no longer only chat interfaces. They can retrieve data, call tools, maintain memory, delegate to other agents and operate with enterprise permissions. That creates a security boundary similar to an application, identity system and network service combined.

The current VEYRA baseline therefore covers:

- LLM prompt injection and jailbreak resistance
- agent behavior hijacking
- tool misuse and excessive agency
- identity and privilege abuse
- MCP server/tool security
- A2A identity and trust
- agent skills and skill supply chain
- memory poisoning and unauthorized memory writes
- RAG poisoning/leakage and retrieval authorization
- model/artifact supply-chain risks
- unsafe Python/model serialization artifacts
- AI gateway and deterministic policy enforcement
- runtime traces and evidence
- model evaluation and regression
- adversarial ML and robustness
- AI SBOM/AIBOM and provenance
- AI-specific incident response and threat intelligence

## Tier 1 — learn first

| Area | VEYRA tools | Team outcome |
|---|---|---|
| LLM red teaming | Garak, PyRIT, Promptfoo, DeepTeam | Detect prompt injection, jailbreak and unsafe-output weaknesses |
| LLM evaluation | DeepEval, Giskard, Inspect AI, OpenAI Evals | Build repeatable security regressions |
| Agent security | AgentDojo, AgentBench, Invariant, OWASP Agentic Security samples | Understand tool misuse, privilege and autonomy risks |
| MCP | MCP Inspector, MCP Security Scanner | Inventory and test tool interfaces and authorization |
| Guardrails | LlamaFirewall, Llama Guard, NeMo Guardrails, Guardrails AI | Put deterministic controls around model/tool execution |
| Observability | OpenTelemetry GenAI, Langfuse, Phoenix, Traceloop | Trace model → retrieval → tool → side effect chains |
| RAG | Ragas, TruLens, LlamaIndex, Haystack | Test retrieval quality, authorization and poisoning defenses |
| Model security | ModelScan, Fickling, PickleScan | Detect unsafe model artifacts and serialization risks |
| Adversarial ML | ART, TextAttack, Foolbox, RobustBench, TrojAI | Understand robustness and evasion research |
| Supply chain | Syft, Cosign/Sigstore, SLSA, in-toto, OSV-Scanner, Gitleaks | Prove what entered the AI system and whether it was tampered with |

## Tier 2 — advanced team capability

- CyberSecEval
- CyberAgents Exchange AI Inspector integration
- OWASP Agentic Skills Top 10 assessment
- A2A security testing
- LiteLLM / Portkey gateway controls
- NeuralTrust / Lakera Guard integrations
- MLflow / W&B Weave / Braintrust / LangSmith
- MITRE ATLAS mapping
- NIST AI RMF control mapping
- vector database security testing across Qdrant, Milvus, Weaviate and Chroma

## Tier 3 — research / specialist capability

- Agentic penetration-testing orchestration
- adversarial ML research
- model backdoor/trojan analysis
- AI malware-analysis assistants
- agent-to-agent trust analysis
- skill/package provenance analysis
- AI-specific reverse engineering benchmarks
- autonomous SOC investigation with deterministic enforcement

## Standard VEYRA learning workflow

```text
1. Inventory AI assets
2. Identify model / agent / tool / MCP / RAG / memory dependencies
3. Build AI SBOM / provenance record
4. Establish baseline evaluation
5. Run controlled red-team tests
6. Capture traces and evidence
7. Correlate with Security Graph
8. Map to OWASP / NIST / MITRE ATLAS
9. Apply deterministic controls
10. Re-test and compare the security score
```

## Team roles

### AI Security Analyst

Focus on Garak, Promptfoo, PyRIT, DeepEval, Ragas, TruLens, traces and evidence.

### AI Red Team Engineer

Focus on AgentDojo, Inspect AI, CyberSecEval, MCP Inspector, adversarial testing and isolated labs.

### AI Platform Security Engineer

Focus on LiteLLM, gateway policy, identity, MCP/A2A, OpenTelemetry, secrets and supply chain.

### AI SOC / DFIR Analyst

Focus on traces, agent actions, tool calls, identity, memory changes, data access and incident timelines.

### AI Governance Engineer

Focus on NIST AI RMF, OWASP controls, ATLAS mappings, approvals, evidence and auditability.

## Team rule

Never allow an LLM prompt to be the only security boundary. Authorization, capability limits, network policy, identity, approval, logging and worker isolation must be enforced outside the model.
