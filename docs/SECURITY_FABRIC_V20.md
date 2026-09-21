# VEYRA v2.0 — AI Security Fabric

VEYRA v2.0 unifies the platform's five security planes:

1. **Observation** — endpoint, network, identity, cloud, AI/agent runtime and security-tool telemetry.
2. **Detection** — deterministic findings, risk scoring, signatures, threat intelligence and AI-security probes.
3. **Intelligence** — Security Graph, MITRE ATT&CK/ATLAS, RAG/vector security, provenance and cross-plane correlation.
4. **Response** — governed ethical-hacking workers, SOAR, approval gates and evidence-driven remediation.
5. **Governance** — identity, policy, scope, AI-agent controls, audit, evidence and compliance mapping.

## AI attack-path model

The fabric correlates organization-owned identities, agents, tools, AI applications, vector databases and cloud resources. It produces explainable paths rather than opaque LLM judgments.

Example:

`Privileged identity → internal agent → approved tool → AI application → vector database`

The graph is evidence-driven. LLMs may summarize or investigate the result, but cannot change authorization, severity, scope or evidence provenance.

## Runtime AI coverage

- GenAI / LLM applications
- internally developed/local agents
- autonomous and multi-agent workflows
- MCP-connected agents
- A2A workflows
- RAG and vector databases
- memory/context security
- tool authorization
- prompt-injection and secret-request signals
- model/provider telemetry
- OpenTelemetry-aligned agent traces
- AI supply-chain/provenance controls

## Current framework alignment

VEYRA v2.0 maps its AI security controls to OWASP GenAI guidance, OWASP Agent Control Standard, OWASP Agentic Applications 2026, MITRE ATLAS and NIST AI RMF / GenAI Profile. OWASP ACS emphasizes inspectable, traceable, instrumentable agents with runtime controls; NIST's GenAI profile provides lifecycle-oriented risk management guidance.

## API

- `GET /api/fabric/overview`
- `POST /api/fabric/events`
- `GET /api/fabric/events` — admin only
- `GET /api/fabric/ai-attack-paths` — admin only

## Security boundary

The fabric never turns an LLM into an unrestricted administrator. Authorization, approval, scope, tool allowlists and evidence integrity remain deterministic controls. High-impact operations must pass the existing admin/approval/isolated-worker pipeline.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
