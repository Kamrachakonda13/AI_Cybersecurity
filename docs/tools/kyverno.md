# Kyverno

## What is it?
Kubernetes-native policy, validation, mutation and image verification

## Why VEYRA includes it
It extends VEYRA coverage for current AI-native, cloud-native or supply-chain security concerns.

## When should the team use it?
Use it when the relevant asset, cluster, agent, repository or supply-chain scope is explicitly enrolled and authorized.

## Who can use it?
Administrative/security users through the governed worker model. Experimental tools require an isolated worker and explicit approval.

## VEYRA UI workflow
1. Open the Security Radar or Tool Academy.
2. Confirm provenance, maturity, version and worker compatibility.
3. Select an approved scope.
4. Request the governed worker job; privileged or experimental use requires the appropriate approval/Sudo gate.
5. Review normalized evidence, provenance and policy decisions.

## Terminal starting point
```bash
kyverno --help
```
Run only from an enrolled VEYRA managed worker. Prefer help/version first and use only VEYRA-generated approved command profiles for active assessment.

## Safe workflow
Start with read-only inventory or policy evaluation. Do not test production secrets, credentials, unrelated tenants or unapproved targets.

## Evidence to collect
- target/asset/cluster/agent identifier
- scope and authorization
- tool version and worker identity
- configuration/policy revision
- timestamps and trace ID
- stdout/stderr or connector response
- artifact hash/SBOM where applicable

## How to interpret the result
Treat a finding as evidence requiring correlation with VEYRA assets, identities, controls, Security Graph and threat intelligence. A benchmark or single alert is not proof of compromise or security.

## Remediation and verification
Create a governed remediation plan, apply the smallest safe change, record the change and rerun the same control/test to verify closure and detect drift.

## Common mistakes
- promoting an experimental tool directly to production
- skipping provenance/version pinning
- treating a policy violation as proof of exploitation
- running against assets outside the approved scope

## Security boundary
VEYRA does not expose arbitrary browser shell access, hack-back, credential theft, persistence, C2, destructive disruption or unauthorized testing. Execution is restricted to authorized managed workers with RBAC/Sudo, scope, approval and evidence controls.

## Team teaching summary
Use Kyverno as one evidence-producing control in the lifecycle: **Discover → Understand → Validate → Investigate → Correlate → Contain → Recover → Prove → Learn → Continuously revalidate.**
