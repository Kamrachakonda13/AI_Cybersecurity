# VEYRA v2.2 — Continuous Detection & Response Mesh

VEYRA v2.2 connects telemetry ingestion to deterministic detection, AI-assisted investigation, human approval, governed response and verification.

## Flow

```text
SIEM / EDR / Cloud / Identity / Network / AI
                  ↓
             Normalize
                  ↓
          Detection Rules
                  ↓
        Security Fabric Event
                  ↓
       Deterministic Correlation
                  ↓
          Autonomous SOC
                  ↓
        Evidence + Risk + Graph
                  ↓
           Human Approval
                  ↓
       Governed Response Adapter
                  ↓
             Verification
                  ↓
        Case Closure / Learning
```

## Design principles

- AI is advisory for investigation, summarization and hypothesis generation.
- Detection thresholds, authorization, approval and evidence provenance are deterministic.
- Response actions are allowlisted and approval-gated.
- The POC does not execute host/network changes.
- Every response can be verified against observed state and evidence.
- Duplicate alert IDs are idempotent.
- SHA-256 evidence fingerprints support provenance.

## Built-in detection rules

- High-risk AI tool invocation
- Privileged anomalous session
- High-risk network transfer
- Endpoint execution anomaly
- High-risk cloud control-plane activity

## API surface

- `GET /api/detection-mesh/overview`
- `GET /api/detection-mesh/rules`
- `POST /api/detection-mesh/alerts`
- `GET /api/detection-mesh/response-actions`
- `POST /api/detection-mesh/cases/{case_id}/response`
- `POST /api/detection-mesh/response-actions/{action_id}/verify`

## Production evolution

Replace the POC response boundary with separately deployed, authenticated adapters for EDR, IAM, network controls and cloud security controls. Each adapter should enforce scope, idempotency, least privilege, change tickets and rollback/verification contracts.

NIST's current AI security work explicitly includes controls for single-agent and multi-agent systems, and its 2026 agent-security work highlights the need to adapt traditional cybersecurity practices for agent systems. VEYRA keeps those controls at the governance and enforcement boundary rather than allowing an LLM to directly execute security changes.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
