# Deprecation Notices

This document tracks deprecated components in VEYRA and their migration paths.

## Policy

- Deprecated components continue to function for **at least one major version**.
- They emit a `DeprecationWarning` at import or execution time.
- Removal happens in the **next major version** after deprecation.
- Every removal is documented here, with a migration guide.

---

## v4.1 managed-worker verifier

**Status:** Deprecated as of VEYRA v5.0
**Planned removal:** VEYRA v6.0
**File:** `worker/v41/veyra_verify_artifact.py`
**Successor:** `worker/v50/veyra_trust_verifier.py`

### Why deprecated

The v4.1 worker used a per-check shape (`checks: {name: {...}}`) but
hard-coded three checks to `passed: true` (`smoke_test`, `parser_regression`,
`security_regression`) with placeholder method strings. This was a **fail-open**
pattern: a receipt could report `healthy` even though those three checks were
never actually performed.

The v5.0 worker enforces fail-closed semantics: `overall_status == "healthy"`
requires **every** check to actually run and pass. Missing binaries, skipped
checks, and placeholder verifiers all result in `overall_status == "failed"`.

### Migration

**Before (v4.1)**

```bash
python worker/v41/veyra_verify_artifact.py \
  --artifact /path/to/artifact \
  --expected-sha256 <hex> \
  --worker-id w-01 \
  --release-id rel-001 \
  --cosign-key /path/key.pub \
  --cosign-bundle /path/bundle.sig \
  --enable-grype --enable-syft

After (v5.0)

echo '{
  "worker_id": "w-01",
  "release_id": "rel-001",
  "artifact_path": "/path/to/artifact",
  "expected_sha256": "<hex>",
  "verifiers": ["cosign", "grype", "syft"],
  "cosign_key": "/path/key.pub",
  "cosign_bundle": "/path/bundle.sig"
}' | python worker/v50/veyra_trust_verifier.py

Schema change: see worker/v50/CONTRACT.md for
the full v5.0 request and response schemas.

v4.2 managed-worker verifier
Status: Deprecated as of VEYRA v5.0
Planned removal: VEYRA v6.0
File: worker/v42/veyra_trusted_verifier.py
Successor: worker/v50/veyra_trust_verifier.py

Why deprecated
The v4.2 worker only supports a single verifier per invocation
(--verifier cosign). Producing a full audit receipt for a release with
multiple checks requires invoking it multiple times, producing multiple
receipts — harder to correlate.

The v5.0 worker supports multiple verifiers per invocation, producing a
single unified receipt with per-check results. This is the recommended
shape for audit records.

Migration
Before (v4.2)

bash
python worker/v42/veyra_trusted_verifier.py \
  --artifact /path/to/artifact \
  --expected-sha256 <hex> \
  --verifier cosign
After (v5.0)

bash
echo '{
  "worker_id": "w-01",
  "release_id": "rel-001",
  "artifact_path": "/path/to/artifact",
  "expected_sha256": "<hex>",
  "verifiers": ["cosign"]
}' | python worker/v50/veyra_trust_verifier.py
Schema change: the v5.0 receipt replaces the v4.2 top-level verification
object with a checks object keyed by verifier name. See
worker/v50/CONTRACT.md.

What does not get deprecated
worker/v50/veyra_trust_verifier.py — current, supported.

backend/app/services/v40_tool_supply_chain.py — the backend service that
consumes receipts. It supports all receipt versions and does not need to
change.

backend/app/services/v41_supply_chain_runtime.py,
backend/app/services/v42_trusted_supply_chain.py,
backend/app/services/v50_trust_control_plane.py — backend-side data models.
They consume receipts, they don't execute workers, so they're not affected
by worker deprecation.

Timeline
Release	Action
v5.0 (current)	v4.1 and v4.2 marked deprecated; warnings emitted; v5.0 is the recommended worker.
v5.x	Both v4.x workers continue to function. Bug fixes only; no new features.
v6.0	v4.1 and v4.2 removed. Any remaining callers will fail.
ENDOFDEPRECATION	
