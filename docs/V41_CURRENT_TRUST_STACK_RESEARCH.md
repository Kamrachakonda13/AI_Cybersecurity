# v4.1 Current Trust-Stack Research — 2026-09-11

## Sigstore / Cosign

Cosign's current verification documentation supports keyless and key-based signature verification, transparency-log evidence, and verification of in-toto attestations. Cosign bundles can carry signature, certificate and timestamp information for offline/portable verification workflows.

Official sources:
- https://docs.sigstore.dev/cosign/verifying/
- https://docs.sigstore.dev/cosign/verifying/verify/
- https://docs.sigstore.dev/cosign/verifying/attestation/

## SLSA

SLSA v1.2 is the current approved specification. Its provenance model provides verifiable information that can track an artifact back through the supply chain to how it was produced.

Official sources:
- https://slsa.dev/spec/v1.2/
- https://slsa.dev/spec/v1.2/provenance

## Design decision

VEYRA uses these systems as complementary controls rather than replacing one with another: update metadata, artifact identity, signature, provenance, SBOM, vulnerability state and runtime health answer different questions.
