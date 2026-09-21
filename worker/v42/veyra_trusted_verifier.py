#!/usr/bin/env python3
"""VEYRA v4.2 managed-worker verifier.

Only fixed verifier programs are callable. No shell, eval, package-manager
or arbitrary command execution.

Exit codes:
    0  healthy  (digest matches AND verifier actually ran AND passed)
    2  failed   (any check failed, or verifier unavailable)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

TOOLS = {
    "cosign": "cosign",
    "syft": "syft",
    "grype": "grype",
    "tuf": "tuf-client",
}

# Tools whose absence is a hard failure. Do not weaken without an ADR.
STRICT_TOOLS = {"cosign", "grype"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_fixed(tool: str, path: str) -> dict:
    binary = shutil.which(TOOLS[tool])
    if not binary:
        return {
            "status": "not_installed",
            "tool": tool,
            "strict": tool in STRICT_TOOLS,
        }

    if tool == "syft":
        args = [binary, path, "-o", "json"]
    elif tool == "grype":
        args = [binary, path, "-o", "json"]
    elif tool == "cosign":
        args = [binary, "verify-blob", path]
    else:
        args = [binary, "--version"]

    p = subprocess.run(
        args, capture_output=True, text=True, timeout=180, check=False
    )
    return {
        "status": "passed" if p.returncode == 0 else "failed",
        "tool": tool,
        "returncode": p.returncode,
        "stdout_sha256": hashlib.sha256(p.stdout.encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256(p.stderr.encode()).hexdigest(),
    }


def is_healthy(digest_match: bool, verification: dict) -> bool:
    """Fail-closed decision.

    - digest MUST match
    - verification.status MUST be exactly "passed"
    - any other state (not_installed, failed, missing) is a failure
    """
    if not digest_match:
        return False
    if verification.get("status") != "passed":
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", required=True)
    ap.add_argument("--expected-sha256", required=True)
    ap.add_argument("--verifier", choices=sorted(TOOLS), required=True)
    a = ap.parse_args()

    path = Path(a.artifact).resolve()
    if not path.is_file():
        print(json.dumps({"status": "failed", "reason": "artifact not found"}))
        return 2

    observed = digest(path)
    digest_match = observed.lower() == a.expected_sha256.lower()
    verification = run_fixed(a.verifier, str(path))
    healthy = is_healthy(digest_match, verification)

    result = {
        "contract_version": "4.2",
        "artifact": str(path),
        "observed_sha256": observed,
        "expected_sha256": a.expected_sha256,
        "digest_match": digest_match,
        "verification": verification,
        "status": "healthy" if healthy else "failed",
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if healthy else 2


if __name__ == "__main__":
    raise SystemExit(main())
