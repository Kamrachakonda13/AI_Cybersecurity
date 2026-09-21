# VEYRA v4.0 — Tool Supply Chain & Autonomous Update Fabric

## Purpose

VEYRA now treats security tooling as a software supply chain rather than a collection of packages. A tool is not trusted merely because an upstream repository published a new version.

## Lifecycle

```text
Advisories / Releases / Registries
             |
             v
       UPDATE SCOUT
             |
             v
   Candidate Release Record
             |
             v
 Signature + Digest + Provenance + SBOM + License
             |
             v
        ARTIFACT VAULT
             |
             v
      VALIDATION LAB
   smoke + parser + security regression
             |
             v
           CANARY
             |
             v
          STABLE
             |
             v
      Managed Workers
             |
             v
 Signed execution receipt + evidence hash
```

## Update frequency

| Signal | Discovery | Promotion |
|---|---|---|
| Actively exploited vulnerability | continuous / immediate | emergency canary or controlled forced rollout |
| High-severity security update | daily | 24–72h after validation |
| Normal patch/minor | daily | weekly |
| Major release | daily metadata | planned / monthly |
| VEYRA dependencies | PR automation | CI-controlled |

## Channels

- **Candidate:** newly discovered, not trusted for production.
- **Canary:** verified release on a controlled worker cohort.
- **Stable:** default production channel.
- **Extended Stable:** slower-moving tenants/workers that need change minimization.

## Version controls

- `floating`: follow the selected channel.
- `pinned`: exact version.
- `immutable`: exact version plus artifact digest.

A freeze can pause promotion for a tool. Quarantine blocks promotion. Force update creates an explicit signed worker contract. Rollback targets a previously verified immutable release.

## Verification

Production should integrate:

- **TUF** for repository metadata, freshness and rollback protection.
- **Sigstore/Cosign** for artifact signatures and attestations.
- **Syft** for SBOM generation.
- **Grype** for artifact/SBOM vulnerability scanning.
- **SLSA/in-toto** provenance for build origin and reproducibility evidence.

VEYRA records the evidence and refuses production promotion when mandatory verification fields are missing.

## Health gate

A release is promoted only after:

1. binary integrity
2. dependency integrity
3. version/help/API smoke test
4. known-safe fixture
5. output parser regression
6. security regression suite
7. canary worker observation

A failed canary must stop promotion and produce rollback evidence.

## Worker contract

The worker receives a typed manifest containing:

- tenant/worker identity
- tool/release identity
- exact version
- artifact URI and digest
- signature/provenance/SBOM references
- operation (`install_or_update` or `rollback`)
- policy hash
- scope/expiration
- approval state

The worker returns a signed execution receipt, artifact hashes, SBOM reference, start/end timestamps, tool version and policy hash.

## Security boundary

The SaaS API never executes `apt`, `pip`, arbitrary shell, package-manager commands or third-party binaries. It plans and verifies. Installation and execution happen only inside managed workers.
