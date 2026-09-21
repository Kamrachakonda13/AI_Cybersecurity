# VEYRA v4.1 — Production Trust Stack

VEYRA's production tool supply chain should use independent layers:

1. **TUF** — trusted update metadata, freshness and rollback/freeze resistance.
2. **Cosign/Sigstore** — artifact signatures, attestations and transparency evidence.
3. **Syft** — SBOM generation.
4. **Grype** — vulnerability analysis of artifacts/SBOMs.
5. **SLSA v1.2 / in-toto** — verifiable build provenance.
6. **VEYRA worker receipts** — tool-specific health, parser and security regression evidence.
7. **Immutable artifact storage** — preserve the exact bytes identified by digest.

The trust chain should be AND-based for stable promotion: a release does not become stable because one signal is green while another is missing.

Official references checked September 11, 2026:

- Sigstore Cosign verification supports signatures, transparency-log evidence and in-toto attestations.
- SLSA v1.2 is the current approved specification and defines provenance as verifiable information describing where, when and how artifacts were produced.

See the official documentation linked from the VEYRA release research record.
