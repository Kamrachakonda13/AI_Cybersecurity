# github-advanced-security

**Category:** AI AppSec  
**Purpose:** Code, secret and dependency security connector  
**VEYRA access:** admin  
**Execution boundary:** approved_ai_worker

## What is it?
Code, secret and dependency security connector

## Why VEYRA includes it
Provides a governed, auditable capability with scope and evidence controls.

## When should the team use it?
Use it when the security objective matches **Code, secret and dependency security connector** and the target is owned, explicitly authorized, and inside the recorded scope.

## VEYRA UI workflow
1. Open **Tool Runner / Sudo Security Arsenal**.
2. Search for **github-advanced-security** and read this guide before execution.
3. Confirm the target/scope and business purpose.
4. Confirm the user's entitlement and Sudo/approval requirements.
5. Select the appropriate managed worker and execution profile.
6. Run only the approved test; collect normalized evidence.
7. Review results in the Security Graph/SOC where applicable.
8. Remediate confirmed issues and schedule revalidation.

## Terminal starting point
Start with local discovery/help only on an enrolled worker:

```bash
github-advanced-security --help
github-advanced-security --version
```

If the binary is not installed, use the VEYRA Tool Marketplace/install workflow rather than installing unapproved software manually. For SaaS/API-only capabilities, use the VEYRA connector/worker documented for that integration.

**Do not substitute arbitrary attack commands for the approved worker profile.** Tool-specific commands that can change security state require explicit authorization, scope and approval.

## Safe workflow
Select an approved AI asset, define scope, run the governed evaluation on a managed worker, review evidence, then map results to AI security controls.

## Evidence to collect
- tool output
- timestamp
- scope
- provenance

## How to interpret results
Treat tool output as a signal or measurement. Confirm affected assets, ownership, scope, timestamps and reproducibility before declaring a security issue. Correlate with other telemetry where possible.

## Remediation and verification
Correlate the finding with VEYRA AI Security, Security Graph, MITRE ATLAS and governance controls.

## Common mistakes
- Testing an unapproved model
- Mixing production secrets into test prompts
- Treating a benchmark score as proof of security

## Team teaching summary
**One sentence:** github-advanced-security is used to help the team achieve **Code, secret and dependency security connector** under an approved and auditable VEYRA workflow.

## Security boundary
Educational and defensive guidance only. VEYRA does not provide hack-back, unrestricted credential attacks, payload deployment, persistence, C2, evasion or disruptive instructions.
