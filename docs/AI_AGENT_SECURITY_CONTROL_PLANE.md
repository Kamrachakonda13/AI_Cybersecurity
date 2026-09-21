# VEYRA AI / Agent Security Control Plane

VEYRA v1.8 adds a dedicated security layer for enterprise GenAI, agentic AI, MCP-connected agents, A2A workflows, RAG/vector stores, and locally developed/internal agents.

## Coverage

- LLM and GenAI applications
- Autonomous and semi-autonomous agents
- Internal/local agents created by engineering teams
- RAG and vector databases
- Tool-calling and MCP integrations
- Agent-to-agent (A2A) communication
- Agent memory and context
- Model, dataset, prompt, skill and tool supply chain
- Runtime telemetry and evidence
- Human approval and kill-switch boundaries

## Tool integrations

The catalog supports governed integration points for:

- Garak
- Promptfoo
- NeuralTrust
- Lakera Guard / Check Point AI Guardrails
- TrojAI
- CalypsoAI / F5 AI Security
- Adversarial Robustness Toolbox
- HiddenLayer
- Robust Intelligence
- NeMo Guardrails

These are cataloged as connector/worker integrations. VEYRA does not embed vendor credentials or bypass their authorization models.

## Security domains

1. Prompt/context integrity
2. Agent identity and least privilege
3. Tool/MCP security
4. Memory security
5. RAG/data security
6. Model and AI supply-chain provenance
7. Training/fine-tuning security
8. Agent-to-agent trust
9. OpenTelemetry/evidence
10. Runtime governance

## Framework alignment

VEYRA maps its control plane to OWASP GenAI LLM Top 10 2026, OWASP Top 10 for Agentic Applications 2026, OWASP Agent Control Standard (ACS), MITRE ATLAS and NIST AI RMF.

## Local-agent posture

Every internally developed agent should have an inventory record and posture assessment covering:

- explicit tool allowlist
- agent identity
- short-lived credentials
- approval boundary
- RAG authorization
- memory provenance
- OpenTelemetry instrumentation
- human approval for high-impact side effects
- model/prompt/skill/tool/dataset provenance

The posture API is deterministic and advisory. It does not generate attack payloads.

## Offensive testing boundary

AI red teaming is restricted to approved targets and isolated workers. VEYRA does not expose arbitrary shell access, unrestricted exploit execution, credential attacks, persistence, C2, or hack-back functionality through the web console.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
