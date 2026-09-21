# VEYRA v2.1 — Autonomous Security Operations Fabric

VEYRA v2.1 connects alert ingestion to evidence preservation, deterministic correlation, attack-path reasoning, AI-assisted investigation, human approval, governed SOAR, verification and learning.

## Control boundary

**AI may:** summarize telemetry, correlate evidence, propose hypotheses and recommend containment.

**AI may not:** silently change severity, authorize access, execute arbitrary commands, deploy payloads, establish persistence/C2, or bypass approval.

Consequential actions remain behind deterministic policy and explicit human approval. The POC's containment step records the approved intent and hands it to the governed SOAR boundary; it does not make external firewall/host changes.

## Pipeline

`Alert → Evidence Preservation → Deterministic Correlation → Security Graph / Attack Path → AI Investigation → Evidence Bundle → Risk + Confidence → Human Approval → SOAR / Containment → Verification → Closure / Learning`

## Evidence model

Each case preserves the triggering unified event, its SHA-256 provenance, source reference, investigation steps, confidence and approval history. This creates an auditable chain from alert to decision.

## Framework alignment

The design maps to the current OWASP Top 10 for Agentic Applications 2026, OWASP Agent Control Standard direction, MITRE ATT&CK/ATLAS concepts and NIST AI RMF. OWASP's 2026 agentic guidance emphasizes risks such as goal hijack, tool misuse, identity/privilege abuse, supply-chain vulnerabilities and unexpected code execution. NIST AI RMF provides a lifecycle-oriented risk-management foundation.

## API

- `GET /api/autonomous-soc/overview`
- `GET /api/autonomous-soc/cases`
- `POST /api/autonomous-soc/investigate`
- `POST /api/autonomous-soc/cases/{case_id}/containment` — admin only
- `POST /api/autonomous-soc/approvals/{approval_id}` — admin only

## Production hardening

Use OIDC/SSO + MFA, RBAC/ABAC/PAM, signed worker identities, immutable evidence storage/WORM, an external queue, Postgres, OpenTelemetry traces, SIEM/EDR/CSPM integrations, policy-as-code and a dedicated approval service. Keep external enforcement adapters separate from the AI reasoning layer.

## v2.1 validation
- Backend tests: 46 passed
- Frontend build: not run in this environment because frontend/node_modules is not installed

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
