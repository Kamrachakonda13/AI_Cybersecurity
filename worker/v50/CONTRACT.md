# VEYRA v5.0 Managed-Worker Verification Contract

**Status:** authoritative
**Applies to:** `worker/v50/veyra_trust_verifier.py`
**Supersedes:** v4.1 (`receipt_version`), v4.2 (`contract_version`)

## Invocation
echo '<json request>' | python worker/v50/veyra_trust_verifier.py


The worker reads a single JSON object from **stdin** and writes a single JSON
object to **stdout**. It is **stateless** — no filesystem writes, no database,
no logs. Callers own persistence.

**Exit codes**
- `0` — `overall_status == "healthy"`
- `2` — any other outcome (invalid request, failed check, missing artifact)

## Request schema

| Field | Type | Required | Notes |
|---|---|---|---|
| `worker_id` | string | ✅ | Identity of the calling worker |
| `release_id` | string | ✅ | Release identifier being verified |
| `artifact_path` | string | ✅ | Absolute path to the artifact |
| `expected_sha256` | string (64 hex) | ✅ | Immutable subject digest |
| `verifiers` | string[] (non-empty) | ✅ | Subset of `ALLOWED_VERIFIERS` |
| `cosign_key` | string | ⚠️ | Required if `"cosign"` in `verifiers` |
| `cosign_bundle` | string | ⚠️ | Required if `"cosign"` in `verifiers` |

## Machine-readable schemas

The request and response shapes below are enforced by JSON Schemas:

- **Request:** [`schema/request.schema.json`](schema/request.schema.json)
- **Response:** [`schema/response.schema.json`](schema/response.schema.json)

CI validates every worker response against the response schema (see
`backend/tests/test_v50_worker.py`). If you change the worker's output shape,
you **must** update the schema in the same commit — otherwise tests fail.

The prose tables below describe the same contract in human-readable form.

## Response schema

| Field | Type | Notes |
|---|---|---|
| `contract_version` | `"5.0"` | Always |
| `worker_id` | string | Echoed from request |
| `release_id` | string | Echoed from request |
| `artifact.path` | string | Absolute resolved path |
| `artifact.observed_sha256` | string | Actual hash |
| `artifact.expected_sha256` | string | Expected hash (lowercased) |
| `artifact.digest_match` | boolean | `observed == expected` |
| `checks` | object<string, check> | One entry per requested verifier |
| `overall_status` | `"healthy"` \| `"failed"` | Fail-closed |
| `evidence_sha256` | string | SHA-256 over the receipt (excluding this field) |
| `execution` | `"managed_worker_only"` | Always |

### Check object

| Field | Type | Notes |
|---|---|---|
| `verifier` | string | Name of the verifier (echoed) |
| `status` | enum | `passed` \| `failed` \| `not_installed` \| `not_implemented` |
| `returncode` | int | Optional, from the subprocess |
| `stdout_sha256` | string | Optional, hash of the verifier's stdout |
| `stderr_sha256` | string | Optional, hash of the verifier's stderr |
| `reason` | string | Optional, human-readable explanation |

## Fail-closed rule

`overall_status == "healthy"` **if and only if**:

1. `artifact.digest_match == true`, AND
2. Every entry in `checks` has `status == "passed"`

Any other state (`failed`, `not_installed`, `not_implemented`, missing checks,
empty `checks`) results in `overall_status == "failed"` and exit code `2`.

## Allowed verifiers

| Verifier | Binary | Notes |
|---|---|---|
| `cosign` | `cosign` | Sigstore signature verification |
| `syft` | `syft` | SBOM generation (Anchore) |
| `grype` | `grype` | Vulnerability scan (Anchore) |
| `tuf-client` | `tuf-client` | The Update Framework metadata |
| `spiffe-verifier` | `spiffe-verifier` | SPIFFE/SPIRE workload identity |
| `aibom-validator` | (placeholder) | Reserved — returns `not_implemented` |
| `trajectory-validator` | (placeholder) | Reserved — returns `not_implemented` |

No shell. No eval. No package manager. No arbitrary commands.

## Example request

```json
{
  "worker_id": "w-01",
  "release_id": "rel-2026-09-21-001",
  "artifact_path": "/tmp/artifact.tar.gz",
  "expected_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "verifiers": ["cosign", "grype"]
}