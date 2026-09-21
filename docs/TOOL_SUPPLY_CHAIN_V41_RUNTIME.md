# VEYRA v4.1 — Verified Tool Supply Chain Runtime

## Purpose

v4.1 moves VEYRA from a tool-update control plane toward a verified worker runtime. The SaaS control plane never executes arbitrary package-manager commands or downloaded binaries.

## Worker verification contract

A managed verification worker returns:

- worker identity;
- release ID;
- exact tool version;
- exact SHA-256 digest;
- signature result;
- provenance result;
- SBOM result;
- vulnerability scan result;
- smoke-test result;
- parser regression result;
- security regression result;
- policy hash;
- signed receipt/evidence hash.

The release cannot become healthy unless every required gate passes.

## Automatic rollback

A failed health/canary report can produce a rollback plan to the most recent active, different release for the same tool and worker. The SaaS layer creates the signed contract; the managed worker performs the actual binary operation.

## Promotion

Only healthy releases can be promoted to canary, stable or extended stable. A frozen tool cannot be promoted until the freeze expires.

## Production verification stack

VEYRA should integrate the managed verification plane with TUF for update metadata/freshness/rollback protection, Cosign/Sigstore for signatures and attestations, Syft for SBOM generation, Grype for artifact/SBOM vulnerability analysis, and SLSA v1.2/in-toto provenance.

Current official documentation confirms Cosign verification of signatures and in-toto attestations, while SLSA v1.2 is the current approved specification for provenance. See the release research notes for references.
