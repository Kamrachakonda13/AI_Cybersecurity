# VEYRA v2.8 — AI Security Ecosystem

## Purpose

VEYRA v2.8 adds a dedicated AI security ecosystem layer on top of the existing 477-tool security catalog. The AI catalog contains 111 integration candidates covering LLM security, agent security, MCP/A2A, RAG, vector databases, model supply chain, adversarial ML, observability, governance and AI incident response.

The catalog is intentionally larger than the set of packages that can be installed immediately. Some entries are open-source projects, some are standards/control mappings, and some are commercial connector candidates. A managed worker must verify licensing, platform compatibility, provenance and availability before installation.

## Current counts

- Core/extended security tools: 477
- AI ecosystem integrations: 111
- Combined catalog surface: 588 entries
- API routes: 138
- Application version: 2.8.0

## AI security domains

### LLM red teaming and evaluation

Examples: Garak, Promptfoo, PyRIT, Inspect AI, Giskard, DeepEval, HELM and CyberSecEval.

Use these to measure unsafe behavior, prompt-injection resistance, policy adherence, hallucination/groundedness and security regression across models and prompts.

### Agent security

VEYRA treats an agent as an identity-bearing workload rather than simply a chat interface. The platform tracks:

- agent identity
- model identity
- tool identity
- tool authorization
- memory provenance
- RAG authorization
- external effects
- human approval
- runtime traces
- emergency disablement

This is especially important as agentic systems become more autonomous and increasingly interact with external systems. Recent security work emphasizes that authorization alone is insufficient if execution-time workload identity or security context can change between authorization and effect. VEYRA therefore reserves a capability-lease/execution-gate integration point for high-impact agent calls.

### MCP and A2A

The ecosystem includes MCP inspection/security integration points and A2A security controls.

The platform should eventually inspect:

- server identity
- tool descriptions
- tool schemas
- declared capabilities
- transport
- authentication
- authorization
- downstream dependencies
- version pinning
- prompt/tool injection exposure
- data egress
- audit receipts

### RAG and vector security

The platform includes RAG evaluation and vector-store integrations. Security checks should include:

- retrieval authorization
- tenant isolation
- document classification
- embedding/model provenance
- poisoning detection
- cross-tenant retrieval
- stale-index detection
- deletion propagation
- citation/grounding validation
- vector database network exposure

### AI supply chain

The AI supply chain layer includes model scanning, pickle safety, SBOM/AIBOM, signing, SLSA, Sigstore, dependency scanning and provenance.

VEYRA should not allow an arbitrary model artifact to become a trusted production model solely because it passed a functional test. Provenance and artifact identity must be recorded.

### AI observability

Integrations include OpenTelemetry GenAI semantics, Langfuse, Phoenix/Arize, Traceloop, MLflow, Weights & Biases/Weave, Braintrust, LangSmith and gateway telemetry.

VEYRA should correlate:

`user → agent → model → prompt/context → tool → data → external effect`

into one trace.

### Governance

VEYRA maps controls to:

- OWASP LLM security
- OWASP Agentic Applications security
- MITRE ATLAS
- NIST AI RMF
- software supply-chain provenance
- organization-specific policies

## Managed worker architecture

```text
VEYRA UI
   |
   v
Policy / RBAC / Sudo
   |
   v
Approval + Scope
   |
   v
Signed Job / Install Contract
   |
   v
Managed Worker
   |
   +--> Kali tools
   +--> AI security tools
   +--> Cloud tools
   +--> DFIR tools
   +--> Network sensors
   |
   v
Normalized Evidence + Receipt
   |
   v
Security Graph / AI SOC / Governance
```

The SaaS API does **not** execute arbitrary shell commands. A worker receives an approved contract and is responsible for local package installation or tool execution. Production workers should use short-lived workload identity, signed requests and signed evidence receipts.

## UI

Use **AI Ecosystem** to browse the AI catalog and **Security Workers** to see registered worker nodes. Use **Tool Marketplace** for the unified 588-entry catalog.

## Important distinction

A catalog entry means **VEYRA knows how the capability fits into its governance model**. It does not mean the binary is bundled in the SaaS container or that a license has been purchased.

## Recommended production hardening

Before customer execution:

1. Replace shared admin tokens with OIDC/SSO + MFA + RBAC/ABAC.
2. Give workers short-lived identities.
3. Require signed installation manifests.
4. Pin package/artifact versions.
5. Verify publisher signatures and SHA-256.
6. Generate and retain SBOM/AIBOM data.
7. Record license acceptance.
8. Run tools in isolated workers.
9. Stream structured logs rather than raw unrestricted shell access.
10. Return normalized evidence plus a signed receipt.
11. Keep high-impact AI/agent operations behind Sudo/privileged approval.
12. Add an emergency AI-agent circuit breaker / kill switch.

## External ecosystem references

Kali's current metapackage inventory remains the authoritative source for the Kali package families represented by VEYRA's security catalog. Kali explicitly separates wireless, exploitation, forensics, vulnerability, web, cloud/hardware and other families. See the official Kali documentation before updating the generated catalog.

OWASP, MITRE ATLAS and NIST AI RMF should be treated as control/mapping sources rather than installable binaries.
