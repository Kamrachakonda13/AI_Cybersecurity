# httpx

**Category:** Attack Surface  
**Purpose:** HTTP service inventory  
**VEYRA access:** admin  
**Execution boundary:** approved_scope

## What is it?
HTTP service inventory

## Why VEYRA includes it
Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.

## When should the team use it?
Use it when the security objective matches **HTTP service inventory** and the target is owned, explicitly authorized, and inside the recorded scope.

## VEYRA UI workflow
1. Open **Tool Runner / Sudo Security Arsenal**.
2. Search for **httpx** and read this guide before execution.
3. Confirm the target/scope and business purpose.
4. Confirm the user's entitlement and Sudo/approval requirements.
5. Select the appropriate managed worker and execution profile.
6. Run only the approved test; collect normalized evidence.
7. Review results in the Security Graph/SOC where applicable.
8. Remediate confirmed issues and schedule revalidation.

## Terminal starting point
Start with local discovery/help only on an enrolled worker:

```bash
httpx --help
httpx --version
```

If the binary is not installed, use the VEYRA Tool Marketplace/install workflow rather than installing unapproved software manually. For SaaS/API-only capabilities, use the VEYRA connector/worker documented for that integration.

**Do not substitute arbitrary attack commands for the approved worker profile.** Tool-specific commands that can change security state require explicit authorization, scope and approval.

## Safe workflow
Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.

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
**One sentence:** httpx is used to help the team achieve **HTTP service inventory** under an approved and auditable VEYRA workflow.

## Security boundary
Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.
