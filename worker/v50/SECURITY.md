# VEYRA v5.0 Managed-Worker Verifier — Security Profile

**Last reviewed:** 2026-09-22
**Worker:** `worker/v50/veyra_trust_verifier.py`
**Contract:** [`CONTRACT.md`](CONTRACT.md)
**Schemas:** [`schema/request.schema.json`](schema/request.schema.json), [`schema/response.schema.json`](schema/response.schema.json)

## Design principles

The v5.0 worker is a **stateless, fail-closed verifier**:

1. **Stateless.** Reads JSON on stdin, writes JSON on stdout. No DB, no filesystem writes, no logs, no network listeners.
2. **Fail-closed.** `overall_status == "healthy"` requires digest match **AND** every check passed. Missing binaries, skipped checks, and placeholder verifiers all result in `overall_status == "failed"`.
3. **Allowlisted verifiers only.** Only the seven entries in `ALLOWED_VERIFIERS` can be invoked (`cosign`, `syft`, `grype`, `tuf-client`, `spiffe-verifier`, `aibom-validator`, `trajectory-validator`). No arbitrary commands, no shell.
4. **Immutable subject.** The artifact must be pinned by SHA-256 digest.
5. **Verifiable output.** Every receipt includes an `evidence_sha256` over the canonicalized response.

## Threat model

| Threat | Mitigation |
|---|---|
| Malicious request (path traversal, arbitrary command) | Request is validated against `request.schema.json`. Only allowlisted verifier names accepted. No shell, no `eval`, no `os.system`. |
| Artifact substitution | Digest is checked against caller-supplied `expected_sha256`. Mismatch ⇒ fail-closed. |
| Binary shadowing (PATH injection) | Uses `shutil.which()` on fixed binary names. Deployment profile runs with a controlled `PATH`. |
| Response tampering | Every receipt includes `evidence_sha256` — callers verify it. |
| Resource exhaustion | Container runs with memory/CPU limits. Worker uses a 180 s subprocess timeout. |
| Filesystem persistence | Container runs with `read_only: true`. Worker writes nothing to disk. |
| Network egress | Container has no network access by default. Verifier binaries run locally. |
| Privilege escalation | Container runs as UID 10001, non-root, no capabilities. |

## Deployment profile

The canonical deployment is a **container** built from [`Dockerfile`](Dockerfile):

| Control | Setting |
|---|---|
| Base image | `python:3.13-slim-bookworm` (pinned tag) |
| User | `worker` (UID 10001, GID 10001, no shell, no home) |
| Filesystem | `read_only: true` at runtime; `/tmp` mounted as `tmpfs` |
| Working dir | `/app` — owned by root, read-only for worker |
| Capabilities | `drop: [ALL]` |
| Privilege escalation | `no-new-privileges:true` |
| Network | none by default; explicit allowlist for verifier binaries |
| CPU / memory | limited (see `docker-compose.worker.yml`) |
| Healthcheck | import-level self-check |
| Restart | `no` (verifier is invoked per-request; a restart policy hides failures) |

## Deployment profile (docker-compose)

The worker is **not** part of the default compose stack. It runs on
**isolated worker hosts**, separate from the control plane:

```bash
# Build the image
docker build -t veyra-worker-v50:5.0 ./worker/v50

# Run one verification (interactive)
echo '{"worker_id":"w-1","release_id":"rel-1","artifact_path":"/work/artifact.tar.gz","expected_sha256":"...","verifiers":["cosign"]}' \
  | docker run --rm -i \
      --read-only \
      --tmpfs /tmp:rw,noexec,nosuid,size=64m \
      --cap-drop=ALL \
      --security-opt no-new-privileges:true \
      --network none \
      --memory 256m \
      --cpus 0.5 \
      -v /path/to/artifact:/work/artifact.tar.gz:ro \
      veyra-worker-v50:5.0

      For a full deployment, use docker-compose.worker.yml
as an overlay on the main compose file.

Inputs and outputs
See CONTRACT.md for the full request and response schemas.

The worker never:

Executes shell commands

Downloads from arbitrary URLs

Writes to disk

Opens network listeners

Reads environment variables that carry secrets (no SMTP, no DB URLs)

Persists state between invocations

Trust relationships
The worker trusts the filesystem path given to it only enough to hash the file at that path.

The worker trusts the caller-supplied expected_sha256 — it is the caller's job to populate this correctly.

The worker trusts the verifier binaries (cosign, syft, etc.) present in the image. Deployment must ensure these are authentic; consider pinning their versions and hashes.

Removing the worker
To retire the v5.0 worker:

Confirm no callers reference worker_id entries originating from it.

Archive the artifacts it produced if retention policy requires.

Delete the image and remove the compose overlay.

Do not reuse the veyra-worker-v50 tag for a different implementation.

Reporting vulnerabilities
Report suspected vulnerabilities in the worker or its deployment profile to
your organization's security team. Do not file public issues for a private
deployment.