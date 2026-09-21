# VEYRA 2026 AI Security Baseline — Updated September 2026

VEYRA must treat AI security as a first-class security domain rather than an extension of RAG or application security.

## Current strategic baseline

1. **OWASP Top 10 for LLM Applications 2026** — keep the LLM application control/test matrix current.
2. **OWASP Top 10 for Agentic Applications** — model agent-specific risks such as behavior hijacking, tool misuse and identity/privilege abuse.
3. **OWASP Agent Control Standard (ACS)** — represent identity, capabilities, tool authorization, approvals, budgets, side effects and traceability as explicit controls.
4. **OWASP Agentic Skills Top 10** — add the execution-layer risk of agent skills to the VEYRA supply-chain and policy model.
5. **MCP security** — inventory MCP servers/tools, validate provenance and schemas, enforce authorization and record tool calls.
6. **A2A security** — model agent identity, peer trust, message provenance, delegation and authorization.
7. **OpenTelemetry GenAI/agent traces** — capture model calls, retrieval, memory, tool calls, policy decisions and external side effects.
8. **Agent runtime containment** — use deterministic worker/network/capability controls rather than relying on model instructions.
9. **Graph RAG** — combine Security Graph relationships with authorized hybrid retrieval.
10. **AI supply-chain security** — track model, dataset, prompt, skill, tool, package and connector provenance.
11. **AI SBOM/AIBOM** — maintain an inventory of AI components and dependencies.
12. **Memory security** — classify, authorize, version, monitor and roll back memory writes.
13. **AI red-team regression** — run repeatable Garak/PyRIT/Promptfoo/DeepTeam and evaluation suites for every meaningful release.
14. **AI data security** — detect poisoning, leakage, unauthorized retrieval and cross-tenant access.
15. **Model artifact security** — scan pickle/model artifacts and verify provenance/signatures.
16. **Adversarial ML** — maintain controlled robustness testing using ART, TextAttack, Foolbox, RobustBench and TrojAI.
17. **AI observability** — make security-relevant agent traces first-class evidence.
18. **AI incident response** — preserve prompts, context, tool calls, model/version, memory changes, identity and external effects.

## Required VEYRA 2026 catalog additions

The v3.1 catalog now includes the cutting-edge baseline across:

- PyRIT
- DeepTeam
- Giskard
- DeepEval
- Inspect AI
- OpenAI Evals
- LM Evaluation Harness
- HELM
- AgentDojo
- AgentBench
- CyberSecEval
- ART
- TextAttack
- Foolbox
- RobustBench
- TrojAI
- Counterfit
- ModelScan
- Fickling
- PickleScan
- MCP Inspector
- MCP security scanner
- Invariant
- OWASP Agentic Security Initiative samples
- OWASP Agentic Skills Top 10
- CyberAgents Exchange AI Inspector integration
- A2A security tests
- LlamaFirewall
- Llama Guard
- NeMo Guardrails
- Guardrails AI
- LiteLLM
- Portkey
- Lakera Guard
- NeuralTrust
- OpenTelemetry GenAI
- Langfuse
- Arize Phoenix
- Traceloop
- MLflow
- W&B Weave
- Braintrust
- LangSmith
- Ragas
- TruLens
- LlamaIndex
- Haystack
- Qdrant
- Milvus
- Weaviate
- Chroma
- Syft/SBOM integrations
- Cosign/Sigstore
- SLSA
- in-toto
- OSV-Scanner
- Gitleaks
- NIST AI RMF mapping
- MITRE ATLAS mapping

## Design rule

```text
LLM = advisory/reasoning component
Policy = deterministic authority
Identity = explicit
Capabilities = allowlisted
Tools = mediated
Network = segmented
Memory = controlled
Evidence = immutable/auditable
Human approval = required for high-impact actions
```

VEYRA must never rely on a system prompt as the sole enforcement mechanism for security scope or execution authority.

## Primary references

- OWASP GenAI Security Project — 2026 LLM and agentic security resources
- OWASP Agentic Skills Top 10
- NIST AI RMF / Generative AI Profile
- MITRE ATLAS
- OpenTelemetry GenAI semantic conventions and ecosystem
