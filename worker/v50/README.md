# worker/v50 — Managed-Worker Verifier

The authoritative verification worker for VEYRA v5.0+.

## Quick start

```bash
echo '{
  "worker_id": "w-01",
  "release_id": "rel-001",
  "artifact_path": "/tmp/artifact.tar.gz",
  "expected_sha256": "<64-hex>",
  "verifiers": ["syft"]
}' | python worker/v50/veyra_trust_verifier.py

Contract
See CONTRACT.md for the full request/response schema.

Design guarantees
Stateless — JSON in, JSON out. No DB, no logs.

Fail-closed — healthy requires digest match AND every check passed.

Allowlisted — only the seven verifiers in ALLOWED_VERIFIERS can be invoked.

Immutable subject — the artifact must be pinned by sha256.

