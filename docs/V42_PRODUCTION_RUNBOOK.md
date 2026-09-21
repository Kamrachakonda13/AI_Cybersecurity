# VEYRA v4.2 Production Runbook

## Before enabling autonomous promotion

- Configure workload identity for workers.
- Store update-signing keys in an external secrets manager/HSM.
- Pin TUF roots and maintain a documented root-rotation procedure.
- Configure Cosign/Sigstore verification policies.
- Generate and retain SBOMs.
- Gate releases with Grype/approved vulnerability policy.
- Require SLSA/in-toto provenance for artifacts where available.
- Use immutable object storage for the artifact vault.
- Configure canary worker cohorts.
- Test automatic rollback quarterly.
- Enable audit/evidence retention.
- Verify tenant isolation before multi-customer rollout.

## Emergency procedure

1. Arm the agent circuit breaker.
2. Deny external egress at the enforcement layer.
3. Revoke or quarantine the affected workload identity.
4. Freeze the affected tool/model release.
5. Preserve signed receipts and evidence hashes.
6. Roll back to the last verified immutable release.
7. Re-run health/security regression tests.
8. Review provenance and publisher trust.
9. Document the incident and policy decision.
10. Only then resume promotion.
