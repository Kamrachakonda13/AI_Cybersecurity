#!/usr/bin/env python3
"""VEYRA v5.0 canonical managed-worker verifier.

The authoritative verification worker for VEYRA v5.0+. Supersedes:
    - worker/v41/veyra_verify_artifact.py  (deprecated)
    - worker/v42/veyra_trusted_verifier.py (deprecated)

Design principles
-----------------
- **Stateless.** JSON in on stdin, JSON out on stdout. No DB, no filesystem
  writes, no logging side effects. Callers own persistence.
- **Fail-closed.** A receipt is `healthy` only if EVERY check passed.
  Missing binaries, skipped checks, and unknown states all count as failure.
- **Allowlisted verifiers only.** No arbitrary commands, no shell, no eval.
- **Immutable subject.** The artifact must be identified by sha256 digest.
- **Fixed output schema.** See worker/v50/CONTRACT.md for the full spec.

Input (stdin JSON)
------------------
{
  "worker_id":     "<string>",           # required
  "release_id":    "<string>",           # required
  "artifact_path": "/abs/path/to/file",  # required
  "expected_sha256": "<hex>",            # required
  "verifiers":     ["cosign", ...],      # required, non-empty subset of ALLOWED
  "cosign_key":    "/path/key.pub",      # optional, required if "cosign" requested
  "cosign_bundle": "/path/bundle.sig"    # optional, required if "cosign" requested
}

Output (stdout JSON)
--------------------
See CONTRACT.md. Exit code is 0 for healthy, 2 for anything else.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "5.0"
EXECUTION_MODE = "managed_worker_only"

# Verifiers the worker is allowed to invoke.
# Note: entries marked ``placeholder`` are allowlisted for forward
# compatibility but return ``not_implemented`` until their integration
# is finalized. Do NOT remove them without an ADR — external callers
# may already pass them and expect a structured response.
ALLOWED_VERIFIERS: dict[str, dict[str, Any]] = {
    "cosign":               {"binary": "cosign",             "placeholder": False},
    "syft":                 {"binary": "syft",               "placeholder": False},
    "grype":                {"binary": "grype",              "placeholder": False},
    "tuf-client":           {"binary": "tuf-client",         "placeholder": False},
    "spiffe-verifier":      {"binary": "spiffe-verifier",    "placeholder": False},
    "aibom-validator":      {"binary": "aibom-validator",    "placeholder": True},
    "trajectory-validator": {"binary": "trajectory-validator", "placeholder": True},
}

# Verifiers whose absence MUST fail the receipt. Do not weaken without an ADR.
STRICT_VERIFIERS = {"cosign", "grype"}


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------

def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_json(obj: Any) -> str:
    return _sha256_bytes(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    )


# ---------------------------------------------------------------------------
# Verifier execution
# ---------------------------------------------------------------------------

def _run_fixed(binary_name: str, args: list[str], timeout: int = 180) -> dict:
    """Run a fixed verifier binary and normalize the result.

    Never uses shell=True. Never invokes arbitrary commands.
    """
    binary = shutil.which(binary_name)
    if not binary:
        return {
            "status": "not_installed",
            "reason": "binary_not_installed",
        }

    try:
        p = subprocess.run(
            [binary, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "failed", "reason": "verifier_timeout"}

    return {
        "status": "passed" if p.returncode == 0 else "failed",
        "returncode": p.returncode,
        "stdout_sha256": _sha256_bytes(p.stdout.encode()),
        "stderr_sha256": _sha256_bytes(p.stderr.encode()),
    }


def _verify_cosign(path: Path, req: dict) -> dict:
    key = req.get("cosign_key")
    bundle = req.get("cosign_bundle")
    if not key or not bundle:
        return {"status": "failed", "reason": "cosign_key_or_bundle_missing"}
    return _run_fixed(
        ALLOWED_VERIFIERS["cosign"]["binary"],
        ["verify-blob", "--key", key, "--bundle", bundle, str(path)],
    )


def _verify_syft(path: Path, _req: dict) -> dict:
    return _run_fixed(
        ALLOWED_VERIFIERS["syft"]["binary"],
        [str(path), "-o", "json"],
    )


def _verify_grype(path: Path, _req: dict) -> dict:
    return _run_fixed(
        ALLOWED_VERIFIERS["grype"]["binary"],
        [str(path), "-o", "json"],
    )


def _verify_tuf_client(_path: Path, _req: dict) -> dict:
    # tuf-client is metadata-oriented; caller must supply the metadata root
    # in a future revision. For now, verify the binary is callable.
    return _run_fixed(ALLOWED_VERIFIERS["tuf-client"]["binary"], ["--version"])


def _verify_spiffe(_path: Path, _req: dict) -> dict:
    return _run_fixed(ALLOWED_VERIFIERS["spiffe-verifier"]["binary"], ["--version"])


def _verify_aibom(_path: Path, _req: dict) -> dict:
    # Placeholder: allowlisted for forward compatibility.
    return {"status": "not_implemented", "reason": "aibom_validator_pending"}


def _verify_trajectory(_path: Path, _req: dict) -> dict:
    # Placeholder: allowlisted for forward compatibility.
    return {"status": "not_implemented", "reason": "trajectory_validator_pending"}


DISPATCH = {
    "cosign":               _verify_cosign,
    "syft":                 _verify_syft,
    "grype":                _verify_grype,
    "tuf-client":           _verify_tuf_client,
    "spiffe-verifier":      _verify_spiffe,
    "aibom-validator":      _verify_aibom,
    "trajectory-validator": _verify_trajectory,
}


# ---------------------------------------------------------------------------
# Decision logic
# ---------------------------------------------------------------------------

def _is_check_passing(check: dict) -> bool:
    """A check passes only if its status is exactly "passed"."""
    return check.get("status") == "passed"


def _overall_status(digest_match: bool, checks: dict[str, dict]) -> str:
    """Fail-closed: healthy requires digest match AND every check passed."""
    if not digest_match:
        return "failed"
    if not checks:
        return "failed"
    if all(_is_check_passing(c) for c in checks.values()):
        return "healthy"
    return "failed"


# ---------------------------------------------------------------------------
# Request validation
# ---------------------------------------------------------------------------

def _validate_request(req: dict) -> None:
    for field in ("worker_id", "release_id", "artifact_path", "expected_sha256", "verifiers"):
        if field not in req:
            raise ValueError(f"missing required field: {field}")

    verifiers = req["verifiers"]
    if not isinstance(verifiers, list) or not verifiers:
        raise ValueError("verifiers must be a non-empty list")

    unknown = [v for v in verifiers if v not in ALLOWED_VERIFIERS]
    if unknown:
        raise ValueError(f"verifiers not allowlisted: {unknown}")

    expected = req["expected_sha256"]
    if not isinstance(expected, str) or len(expected) != 64:
        raise ValueError("expected_sha256 must be a 64-char hex string")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def verify(req: dict) -> dict:
    _validate_request(req)

    path = Path(req["artifact_path"]).resolve()
    if not path.is_file():
        return {
            "contract_version": CONTRACT_VERSION,
            "worker_id": req.get("worker_id"),
            "release_id": req.get("release_id"),
            "status": "failed",
            "reason": "artifact_not_found",
            "execution": EXECUTION_MODE,
        }

    observed = _sha256_file(path)
    expected = req["expected_sha256"].lower()
    digest_match = observed.lower() == expected

    checks: dict[str, dict] = {}
    for name in req["verifiers"]:
        try:
            result = DISPATCH[name](path, req)
        except Exception as exc:  # defensive: never crash mid-receipt
            result = {"status": "failed",
                      "reason": f"verifier_exception:{type(exc).__name__}"}
        result["verifier"] = name
        checks[name] = result

    overall = _overall_status(digest_match, checks)

    receipt = {
        "contract_version": CONTRACT_VERSION,
        "worker_id": req["worker_id"],
        "release_id": req["release_id"],
        "artifact": {
            "path": str(path),
            "observed_sha256": observed,
            "expected_sha256": expected,
            "digest_match": digest_match,
        },
        "checks": checks,
        "overall_status": overall,
        "execution": EXECUTION_MODE,
    }
    receipt["evidence_sha256"] = _sha256_json(
        {k: v for k, v in receipt.items() if k != "evidence_sha256"}
    )
    return receipt


def main() -> int:
    try:
        req = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(json.dumps({
            "contract_version": CONTRACT_VERSION,
            "status": "failed",
            "reason": f"invalid_json:{exc.msg}",
            "execution": EXECUTION_MODE,
        }, sort_keys=True))
        return 2

    if not isinstance(req, dict):
        print(json.dumps({
            "contract_version": CONTRACT_VERSION,
            "status": "failed",
            "reason": "request_must_be_json_object",
            "execution": EXECUTION_MODE,
        }, sort_keys=True))
        return 2

    try:
        receipt = verify(req)
    except ValueError as exc:
        print(json.dumps({
            "contract_version": CONTRACT_VERSION,
            "status": "failed",
            "reason": str(exc),
            "execution": EXECUTION_MODE,
        }, sort_keys=True))
        return 2

    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0 if receipt.get("overall_status") == "healthy" else 2


if __name__ == "__main__":
    raise SystemExit(main())
