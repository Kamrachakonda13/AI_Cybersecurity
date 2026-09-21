# VEYRA v3.8 — AI Provider & Endpoint Security Radar

## Why this exists

The AI attack surface now spans model providers, coding agents, MCP/A2A, local agents, endpoint runtimes, cloud agent platforms and on-device AI. VEYRA therefore needs a continuously refreshed inventory and control layer rather than a static list of model names.

## Provider coverage

### OpenAI
Track frontier model capability tier, cyber capability classification, agent sandboxing, auto-review, hardware-key/strong-auth requirements, trajectory monitoring and approved defensive access.

### Anthropic
Track Claude model family, agent runtime access, cyber-evaluation exposure, internet/tool permissions, trajectory telemetry and incident-review status.

### Google
Track Gemini agentic/action capabilities, multimodal tools, identity and external tool access.

### Apple
Track Apple Foundation Models, on-device inference, Vision/OCR tools, Dynamic Profiles, Private Cloud Compute and macOS architecture. Apple Silicon and macOS 27 are strategic endpoint inventory attributes.

### Microsoft
Track Agent 365 registry/observability, Entra Agent IDs, Copilot/Foundry agents, Defender AI-agent telemetry and Windows/macOS endpoint correlation.

### AWS
Track Bedrock AgentCore agent identity, Consent Portal, gateway authorization and multi-framework evaluation coverage.

### Linux Foundation / open agent ecosystem
Track A2A, agentgateway, MCP conformance, DNS-AID, Agent Name Service concepts, OpenSharing and AI security projects.

## Required VEYRA controls

1. Agent identity and ownership.
2. Explicit capability profile.
3. Tool/MCP allowlist.
4. Network egress policy.
5. Secret boundary.
6. Data classification and retrieval boundary.
7. Runtime trace ID.
8. Prompt/tool provenance.
9. Model and tool artifact provenance.
10. Evaluation evidence before privilege expansion.
11. Human approval for consequential operations.
12. Kill/revoke path with audit evidence.

## Threat model

VEYRA should continuously test for:

- prompt injection and indirect prompt injection;
- URL/data exfiltration;
- malicious tool descriptions and parameter manipulation;
- agent identity confusion;
- cross-agent trust abuse;
- MCP/A2A supply-chain drift;
- unsafe computer-use actions;
- local agent compromise;
- model artifact tampering;
- insecure RAG/vector boundaries;
- excessive permissions;
- hidden network access;
- insufficient runtime telemetry.

## Governance

Provider releases are advisory intelligence. They never become a permission grant automatically. A new model may require a fresh evaluation, capability review, sandbox profile and evidence before it can operate inside an VEYRA managed worker.
