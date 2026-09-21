# rebuffai

**Category:** Prompt Injection  
**Purpose:** Prompt-injection detection integration candidate  
**VEYRA access:** admin  
**Execution boundary:** approved_ai_worker

## What is it?
Prompt-injection detection integration candidate

## Why VEYRA includes it
Provides a governed, auditable capability with scope and evidence controls.

## When should the team use it?
Use it when the security objective matches **Prompt-injection detection integration candidate** and the target is owned, explicitly authorized, and inside the recorded scope.

## VEYRA UI workflow
1. Open **Tool Runner / Sudo Security Arsenal**.
2. Search for **rebuffai** and read this guide before execution.
3. Confirm the target/scope and business purpose.
4. Confirm the user's entitlement and Sudo/approval requirements.
5. Select the appropriate managed worker and execution profile.
6. Run only the approved test; collect normalized evidence.
7. Review results in the Security Graph/SOC where applicable.
8. Remediate confirmed issues and schedule revalidation.

## Terminal starting point
Start with local discovery/help only on an enrolled worker:

```bash
rebuffai --help
rebuffai --version
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
**One sentence:** rebuffai is used to help the team achieve **Prompt-injection detection integration candidate** under an approved and auditable VEYRA workflow.

## Security boundary
Governed security operations. VEYRA enables authorized security testing, red-team, blue-team, and defensive work on owned or explicitly permitted targets. Tools are tiered by risk: Standard (discovery, analysis, defensive verification), Privileged (high-impact testing requires privileged_admin and an approved engagement), and Isolated Lab Only (attack-capable tools may only run against lab/sandbox targets). All executions are scope-bound, evidence-captured, and audited. Out-of-scope activity, unowned targets, and unauthorized use are prohibited.
