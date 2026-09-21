# VEYRA AI Security Gateway & Agent Runtime (introduced v1.9)

The original v1.9 implementation added a deterministic runtime control plane for organization-owned GenAI applications, agentic AI, MCP-connected agents, A2A workflows and local agents.

## Design principle

The gateway is a **policy and telemetry boundary**, not a model provider. It evaluates a request before a model/tool/memory side effect and records an auditable decision. It never executes arbitrary commands and does not generate offensive payloads.

```text
Internal Agent / Local Agent
        |
        v
VEYRA AI Gateway
  | identity / enrollment
  | operation policy
  | tool allowlist
  | prompt/context risk
  | approval boundary
  v
Allow | Approval Required | Deny
        |
        v
Model / RAG / Memory / MCP / A2A / Tool
        |
        v
OpenTelemetry-style Runtime Evidence
        |
        v
Security Graph -> AI SOC -> SOAR
```

## Runtime operations

The gateway recognizes `chat`, `retrieval`, `plan` and `execute_tool` as first-class operations. Runtime events record agent identity, provider, model, tool, decision, risk score, trace ID and an event SHA-256.

The implementation follows the direction of the OWASP Agent Control Standard: enterprise agents should be inspectable, traceable, instrumentable and controllable at runtime. It also aligns its event vocabulary with the emerging OpenTelemetry GenAI conventions for agent invocation, planning, retrieval, memory and tool execution.

## Controls

- Agent enrollment
- Allowed operations
- Tool allowlists
- High-impact tool approval requirements
- Risk thresholds
- Prompt-injection / secret-request detection
- Runtime telemetry
- Trace correlation
- Event integrity hashing
- Human approval boundary
- No side effects performed by the gateway

## Internal/local agents

An organization can enroll agents built with LangChain/LangGraph, CrewAI, ADK, custom Python/Node services, local models or other internal frameworks. The integration pattern is to call the gateway before model/tool side effects and emit the returned trace ID into the agent's telemetry context.

For production, replace the POC shared token with workload identity/mTLS/OIDC, per-agent credentials, short-lived tokens, service-to-service authorization and a policy decision point.

## MCP / A2A

MCP and A2A calls should be represented as tool/message operations and evaluated against the same agent identity, target, authorization, provenance and approval boundary. Do not trust a tool merely because it is discoverable; maintain an inventory and explicit allowlist.

## Privacy

Do not store raw prompts, completions, secrets or sensitive retrieved documents in telemetry by default. Prefer metadata, hashes, classifications and references to protected evidence stores. Production implementations should support configurable content capture and redaction.

## Local agent integration

See `examples/local_agent_gateway.py`. The example demonstrates the control-plane call pattern without executing tools. Production deployments should use workload identity/mTLS/OIDC rather than a static shared token.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
