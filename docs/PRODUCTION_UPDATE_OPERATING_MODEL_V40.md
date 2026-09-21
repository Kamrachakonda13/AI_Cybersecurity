# VEYRA v4.0 — Production Update Operating Model

## Recommended default

**Do not auto-update security tools directly from public package repositories.** Public sources provide discovery signals. VEYRA promotes only immutable, verified artifacts.

### Daily

- advisory refresh: CISA KEV, NVD, OSV, GitHub/vendor advisories
- upstream release metadata refresh
- update candidate scoring
- vulnerability-to-installed-tool correlation

### Weekly

- stable tool promotion window
- worker compatibility/health regression review
- stale pin review
- failed/quarantined release review

### Immediate

- actively exploited vulnerability affecting a deployed tool
- compromised publisher/artifact signal
- critical tool security advisory

Immediate does not mean blind. It means create a high-priority candidate, verify it, canary it, then promote or force-roll back according to policy.

## Forced update

1. Select exact release.
2. Verify digest/signature/provenance/SBOM.
3. Generate deployment contract.
4. Require Sudo/security-admin authorization.
5. Canary controlled workers.
6. Promote or force to the approved worker cohort.
7. Collect receipt and health evidence.

## Rollback

Rollback must point to an immutable prior release that is still retained in the artifact vault. Never reconstruct a rollback by asking an upstream repository for an old package.

## Degradation / compatibility

Use pinned or immutable mode for tools that have parser regressions, changed CLI output, performance regressions or compatibility issues. Keep the pin reason and expiry date. Security-critical exceptions should trigger a risk exception and compensating controls.

## Tenant safety

Customer-specific update policy is required before automatic stable promotion: channel, maintenance window, pin, canary cohort, rollback target and critical-vulnerability override.
