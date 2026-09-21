# DeepTeam

**Category:** LLM Red Team  
**Purpose:** LLM and agent red-team test orchestration  
**VEYRA access:** admin  
**Execution boundary:** approved_ai_worker

## What is it?
LLM and agent red-team test orchestration

## Why VEYRA includes it
Provides a governed, auditable capability with scope and evidence controls.

## When should the team use it?
Use it when the security objective matches **LLM and agent red-team test orchestration** and the target is owned, explicitly authorized, and inside the recorded scope.

## VEYRA UI workflow
1. Open **Tool Runner / Sudo Security Arsenal**.
2. Search for **DeepTeam** and read this guide before execution.
3. Confirm the target/scope and business purpose.
4. Confirm the user's entitlement and Sudo/approval requirements.
5. Select the appropriate managed worker and execution profile.
6. Run only the approved test; collect normalized evidence.
7. Review results in the Security Graph/SOC where applicable.
8. Remediate confirmed issues and schedule revalidation.

## Terminal starting point
Start with local discovery/help only on an enrolled worker:

```bash
deepteam --help
deepteam --version
```

If the binary is not installed, use the VEYRA Tool Marketplace/install workflow rather than installing unapproved software manually. For SaaS/API-only capabilities, use the VEYRA connector/worker documented for that integration.

**Do not substitute arbitrary attack commands for the approved worker profile.** Tool-specific commands that can change security state require explicit authorization, scope and approval.

## Safe workflow
Define an approved AI asset/test scope, run the evaluation or inspection on a managed worker or approved connector, review evidence, then map findings to VEYRA controls.

## Evidence to collect
- tool output
- timestamp
- scope
- provenance

## How to interpret results
Treat tool output as a signal or measurement. Confirm affected assets, ownership, scope, timestamps and reproducibility before declaring a security issue. Correlate with other telemetry where possible.

## Remediation and verification
Correlate findings with VEYRA AI Security, Security Graph, OWASP, NIST AI RMF and MITRE ATLAS controls.

## Common mistakes
- Testing production secrets or unapproved models
- Treating one benchmark as proof of security
- Failing to preserve model/tool/config versions

## Team teaching summary
**One sentence:** DeepTeam is used to help the team achieve **LLM and agent red-team test orchestration** under an approved and auditable VEYRA workflow.

## Security boundary
Defensive/authorized testing only; no credential theft, payload delivery, persistence, C2, evasion or hack-back instructions.
