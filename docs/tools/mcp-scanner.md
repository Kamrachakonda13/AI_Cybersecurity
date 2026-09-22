# MCP Security Scanner

**Category:** MCP Security  
**Purpose:** Inventory and assess MCP server/tool configurations  
**VEYRA access:** admin  
**Execution boundary:** approved_ai_worker

## What is it?
Inventory and assess MCP server/tool configurations

## Why VEYRA includes it
Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.

## When should the team use it?
Use it when the security objective matches **Inventory and assess MCP server/tool configurations** and the target is owned, explicitly authorized, and inside the recorded scope.

## VEYRA UI workflow
1. Open **Tool Runner / Sudo Security Arsenal**.
2. Search for **MCP Security Scanner** and read this guide before execution.
3. Confirm the target/scope and business purpose.
4. Confirm the user's entitlement and Sudo/approval requirements.
5. Select the appropriate managed worker and execution profile.
6. Run only the approved test; collect normalized evidence.
7. Review results in the Security Graph/SOC where applicable.
8. Remediate confirmed issues and schedule revalidation.

## Terminal starting point
Start with local discovery/help only on an enrolled worker:

```bash
MCP Security Scanner --help
MCP Security Scanner --version
```

If the binary is not installed, use the VEYRA Tool Marketplace/install workflow rather than installing unapproved software manually. For SaaS/API-only capabilities, use the VEYRA connector/worker documented for that integration.

**Do not substitute arbitrary attack commands for the approved worker profile.** Tool-specific commands that can change security state require explicit authorization, scope and approval.

## Safe workflow
Define an approved AI asset/test scope, run the evaluation or inspection on a managed worker or approved connector, review evidence, then map findings to VEYRA controls.

## Evidence to collect
- tool output
- target/scope
- timestamp
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
**One sentence:** MCP Security Scanner is used to help the team achieve **Inventory and assess MCP server/tool configurations** under an approved and auditable VEYRA workflow.

## Security boundary
Governed security operations. VEYRA enables authorized security testing, red-team, blue-team, and defensive work on owned or explicitly permitted targets. Tools are tiered by risk: Standard (discovery, analysis, defensive verification), Privileged (high-impact testing requires privileged_admin and an approved engagement), and Isolated Lab Only (attack-capable tools may only run against lab/sandbox targets). All executions are scope-bound, evidence-captured, and audited. Out-of-scope activity, unowned targets, and unauthorized use are prohibited.
