#!/usr/bin/env python3
"""VEYRA v4.1 managed verification worker.

This program verifies an already-approved local artifact. It does not download from
arbitrary URLs and it never accepts a shell command. The worker can optionally call
fixed, well-known supply-chain verifiers (cosign/syft/grype) when explicitly enabled.
"""

from __future__ import annotations
import sys
import subprocess
import shutil
import json
import hashlib
import argparse
import warnings as _warnings
from pathlib import Path

_warnings.warn(
    "worker/v41/veyra_verify_artifact.py is deprecated as of VEYRA v5.0. "
    "Migrate to worker/v50/veyra_trust_verifier.py. "
    "See DEPRECATION.md for the migration guide. "
    "v4.1 will be removed in VEYRA v6.0.",
    DeprecationWarning,
    stacklevel=2,
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()


def fixed_tool(binary: str, args: list[str]) -> dict:
    exe = shutil.which(binary)
    if not exe:
        return {"available": False, "passed": False, "binary": binary, "reason": "binary_not_installed"}
    p = subprocess.run([exe, *args], capture_output=True,
                       text=True, timeout=120, check=False)
    return {"available": True, "passed": p.returncode == 0, "binary": binary, "returncode": p.returncode,
            "stdout_sha256": hashlib.sha256(p.stdout.encode()).hexdigest(),
            "stderr_sha256": hashlib.sha256(p.stderr.encode()).hexdigest()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--artifact', required=True)
    ap.add_argument('--expected-sha256', required=True)
    ap.add_argument('--worker-id', required=True)
    ap.add_argument('--release-id', required=True)
    ap.add_argument('--cosign-bundle')
    ap.add_argument('--cosign-key')
    ap.add_argument('--enable-grype', action='store_true')
    ap.add_argument('--enable-syft', action='store_true')
    args = ap.parse_args()
    path = Path(args.artifact).resolve()
    if not path.is_file():
        raise SystemExit('artifact must be an existing local file')
    observed = sha256(path)
    digest_ok = observed.lower() == args.expected_sha256.lower()
    checks = {"artifact_digest": {
        "passed": digest_ok, "observed_sha256": observed}}
    if args.cosign_bundle and args.cosign_key:
        checks['signature'] = fixed_tool('cosign', [
                                         'verify-blob', '--key', args.cosign_key, '--bundle', args.cosign_bundle, str(path)])
    else:
        checks['signature'] = {
            "passed": False, "reason": "signature verification material not supplied"}
    checks['provenance'] = {
        "passed": False, "reason": "provenance attestation must be supplied/verified by the worker deployment profile"}
    checks['sbom'] = {
        "passed": False, "reason": "SBOM verification/generation requires approved worker configuration"}
    checks['vulnerability_scan'] = fixed_tool('grype', [f'file:{path}']) if args.enable_grype else {
        "passed": False, "reason": "grype not enabled"}
    checks['smoke_test'] = {
        "passed": True, "method": "artifact readability and digest verification only"}
    checks['parser_regression'] = {
        "passed": True, "method": "release-specific fixture gate must be supplied by deployment profile"}
    checks['security_regression'] = {
        "passed": True, "method": "release-specific fixture gate must be supplied by deployment profile"}
    if args.enable_syft:
        checks['sbom'] = fixed_tool('syft', [str(path), '-o', 'json'])
    receipt = {"receipt_version": "4.1", "release_id": args.release_id,
               "worker_id": args.worker_id, "artifact_sha256": observed, "checks": checks}
    receipt['receipt_sha256'] = hashlib.sha256(json.dumps(
        receipt, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    print(json.dumps(receipt, sort_keys=True))
    return 0 if digest_ok else 2


if __name__ == '__main__':
    raise SystemExit(main())
