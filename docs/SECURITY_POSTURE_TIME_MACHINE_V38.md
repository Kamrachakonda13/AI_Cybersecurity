# VEYRA v3.8 — Security Posture Time Machine

## Purpose

v3.8 turns the Security Graph into a temporal security operating system: capture signed posture baselines, compare before/after states, surface deterministic drift, and connect remediation claims to evidence.

## UI workflow

1. Open **Posture Time Machine**.
2. Review the current posture/risk score and inventory counts.
3. Capture a baseline snapshot after an authorized inventory/telemetry refresh.
4. Capture another snapshot after a change window, patch cycle, incident, or remediation.
5. Review **What changed / drift**.
6. Open the related asset/finding/evidence in the existing Security Graph and Governance views.
7. Treat a finding as remediated only when deterministic endpoint or worker evidence verifies the new state.

## APIs

- `GET /api/v38/posture/current`
- `GET /api/v38/posture/history`
- `GET /api/v38/posture/changes`
- `GET /api/v38/posture/drift`
- `GET /api/v38/posture/remediation-proof`
- `POST /api/v38/posture/snapshot`
- `GET /api/v38/ai-endpoint-radar`

## Endpoint security model

VEYRA should not call a Windows, macOS, or Linux host vulnerable merely because an OS family is present. The production determination is:

`vendor advisory + installed build/package/application evidence + asset criticality/exposure + exploit intelligence + remediation evidence`

The v3.8 radar seeds current ecosystem awareness:

- **Windows:** Microsoft September 2026 security updates; supported Windows 11 families include v26H1/v25H2/v24H2/v23H2. Microsoft published a Critical RCE maximum-severity cohort and updated multiple Windows server vulnerabilities.
- **macOS:** Apple published macOS 27.0 RC on September 9, 2026. The new Apple Foundation Models framework and Private Cloud Compute boundary make local model/tool inventory and provenance important security assets.
- **Linux:** Ubuntu Security Notices are actively publishing September 2026 kernel, glibc, Flatpak, FFmpeg, curl and other advisories. Production workers should correlate installed package versions with the appropriate distribution advisory rather than using generic CVE matching.

## AI provider model

The provider radar intentionally treats frontier models as security-relevant infrastructure, not simply API endpoints. Inventory should include provider, model family, capability tier, deployment location, tool access, agent identity, network egress, data classes, evaluation state, and safety-control evidence.

Current strategic coverage includes OpenAI GPT-6 Astra/Daybreak, Anthropic Claude Fable/Mythos 5.1, Google Gemini 3.5, Apple Foundation Models, Microsoft Agent 365, AWS Bedrock AgentCore, and Linux Foundation agent interoperability initiatives.

## Evidence expectations

A production remediation proof should contain:

- endpoint hostname/device ID;
- OS build or package manifest;
- advisory/CVE identifier and affected/fixed range;
- collection timestamp;
- collector/worker identity;
- evidence SHA-256;
- before/after snapshot IDs;
- change window or approval reference;
- verification result.

## AI safety boundary

AI can rank, summarize, explain and propose investigation hypotheses. It must not author authorization policy, silently change endpoint state, disable controls, or execute destructive remediation. Any active validation remains behind the existing VEYRA scope/RBAC/Sudo/approval/managed-worker/evidence chain.
