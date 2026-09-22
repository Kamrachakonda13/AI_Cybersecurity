# Sigma CLI

**Category:** Threat Intelligence  
**Purpose:** Advanced threat intelligence capability: Sigma CLI  
**VEYRA access:** admin  
**Execution boundary:** approved_worker

## What is it?
Advanced threat intelligence capability: Sigma CLI

## Why VEYRA includes it
Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.

## When should the team use it?
Use it when the security objective matches **Advanced threat intelligence capability: Sigma CLI** and the target is owned, explicitly authorized, and inside the recorded scope.

## VEYRA UI workflow
1. Open **Tool Runner / Sudo Security Arsenal**.
2. Search for **Sigma CLI** and read this guide before execution.
3. Confirm the target/scope and business purpose.
4. Confirm the user's entitlement and Sudo/approval requirements.
5. Select the appropriate managed worker and execution profile.
6. Run only the approved test; collect normalized evidence.
7. Review results in the Security Graph/SOC where applicable.
8. Remediate confirmed issues and schedule revalidation.

## Terminal starting point
Start with local discovery/help only on an enrolled worker:

```bash
Sigma CLI --help
Sigma CLI --version
```

If the binary is not installed, use the VEYRA Tool Marketplace/install workflow rather than installing unapproved software manually. For SaaS/API-only capabilities, use the VEYRA connector/worker documented for that integration.

**Do not substitute arbitrary attack commands for the approved worker profile.** Tool-specific commands that can change security state require explicit authorization, scope and approval.

## Safe workflow
Normalize indicators with source and confidence, correlate against internal telemetry, and keep attribution hypotheses separate from confirmed facts.

## Evidence to collect
- tool output
- target/scope
- timestamp
- provenance

## How to interpret results
Treat tool output as a signal or measurement. Confirm affected assets, ownership, scope, timestamps and reproducibility before declaring a security issue. Correlate with other telemetry where possible.

## Remediation and verification
Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.

## Common mistakes
- Using an asset outside the approved scope
- Treating tool output as proof without validation
- Ignoring evidence provenance or timestamps

## Team teaching summary
**One sentence:** Sigma CLI is used to help the team achieve **Advanced threat intelligence capability: Sigma CLI** under an approved and auditable VEYRA workflow.

## Security boundary
Governed security operations. VEYRA enables authorized security testing, red-team, blue-team, and defensive work on owned or explicitly permitted targets. Tools are tiered by risk: Standard (discovery, analysis, defensive verification), Privileged (high-impact testing requires privileged_admin and an approved engagement), and Isolated Lab Only (attack-capable tools may only run against lab/sandbox targets). All executions are scope-bound, evidence-captured, and audited. Out-of-scope activity, unowned targets, and unauthorized use are prohibited.
