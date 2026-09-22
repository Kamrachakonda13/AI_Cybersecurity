"""End-to-end tests for the v5.0 managed-worker verifier.

Covers: valid request, invalid JSON, unknown verifier, digest mismatch,
placeholder verifier, and fail-closed behavior.
"""
import pytest
import jsonschema
from pathlib import Path as _Path
import json as _json
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

WORKER = Path(__file__).resolve(
).parents[2] / "worker" / "v50" / "veyra_trust_verifier.py"


def _run(request: dict, empty_path: bool = False) -> tuple[int, dict]:
    env = dict(os.environ)
    if empty_path:
        env["PATH"] = ""
    p = subprocess.run(
        [sys.executable, str(WORKER)],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        env=env,
    )
    try:
        out = json.loads(p.stdout.strip())
    except Exception:
        out = {"raw_stdout": p.stdout, "raw_stderr": p.stderr}
    return p.returncode, out


def _req(tmp_path: Path, verifiers: list[str]) -> dict:
    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"hello world")
    digest = hashlib.sha256(b"hello world").hexdigest()
    return {
        "worker_id": "w-test",
        "release_id": "rel-test",
        "artifact_path": str(artifact),
        "expected_sha256": digest,
        "verifiers": verifiers,
    }


def test_placeholder_verifier_returns_not_implemented(tmp_path):
    rc, out = _run(_req(tmp_path, ["aibom-validator"]))
    assert rc == 2
    assert out["overall_status"] == "failed"
    assert out["checks"]["aibom-validator"]["status"] == "not_implemented"
    assert out["artifact"]["digest_match"] is True
    assert out["contract_version"] == "5.0"
    assert out["execution"] == "managed_worker_only"


def test_missing_binary_fails_closed(tmp_path):
    rc, out = _run(_req(tmp_path, ["cosign"]), empty_path=True)
    assert rc == 2
    assert out["overall_status"] == "failed"
    assert out["checks"]["cosign"]["status"] == "failed"


def test_digest_mismatch_fails(tmp_path):
    req = _req(tmp_path, ["aibom-validator"])
    req["expected_sha256"] = "0" * 64
    rc, out = _run(req)
    assert rc == 2
    assert out["artifact"]["digest_match"] is False
    assert out["overall_status"] == "failed"


def test_unknown_verifier_rejected(tmp_path):
    rc, out = _run(_req(tmp_path, ["nmap"]))
    assert rc == 2
    assert out["status"] == "failed"
    assert "not allowlisted" in out["reason"]


def test_missing_required_field_rejected(tmp_path):
    req = _req(tmp_path, ["syft"])
    del req["worker_id"]
    rc, out = _run(req)
    assert rc == 2
    assert "missing required field" in out["reason"]


def test_invalid_json_rejected():
    p = subprocess.run(
        [sys.executable, str(WORKER)],
        input="not json",
        capture_output=True,
        text=True,
    )
    assert p.returncode == 2
    out = json.loads(p.stdout.strip())
    assert out["status"] == "failed"
    assert "invalid_json" in out["reason"]


def test_artifact_not_found(tmp_path):
    req = {
        "worker_id": "w-test",
        "release_id": "rel-test",
        "artifact_path": str(tmp_path / "does-not-exist.bin"),
        "expected_sha256": "0" * 64,
        "verifiers": ["syft"],
    }
    rc, out = _run(req)
    assert rc == 2
    assert out["status"] == "failed"
    assert out["reason"] == "artifact_not_found"


# ---------------------------------------------------------------------------
# JSON Schema validation
# ---------------------------------------------------------------------------


_SCHEMA_DIR = _Path(__file__).resolve(
).parents[2] / "worker" / "v50" / "schema"


def _load_schema(name: str) -> dict:
    with open(_SCHEMA_DIR / name, encoding="utf-8") as f:
        return _json.load(f)


@pytest.fixture(scope="module")
def response_schema() -> dict:
    return _load_schema("response.schema.json")


@pytest.fixture(scope="module")
def request_schema() -> dict:
    return _load_schema("request.schema.json")


def _validate(schema: dict, instance: dict) -> None:
    """Raise jsonschema.ValidationError with a clear message if invalid."""
    jsonschema.validate(instance=instance, schema=schema)


def test_request_schema_accepts_valid_request(tmp_path):
    """The schema should accept what _req() produces."""
    req = _req(tmp_path, ["aibom-validator"])
    _validate(_load_schema("request.schema.json"), req)


def test_request_schema_rejects_unknown_verifier(tmp_path):
    """Schema should reject a verifier not in the allowlist."""
    req = _req(tmp_path, ["nmap"])
    with pytest.raises(jsonschema.ValidationError):
        _validate(_load_schema("request.schema.json"), req)


def test_request_schema_rejects_bad_digest(tmp_path):
    """Schema should reject malformed sha256."""
    req = _req(tmp_path, ["syft"])
    req["expected_sha256"] = "not-a-hash"
    with pytest.raises(jsonschema.ValidationError):
        _validate(_load_schema("request.schema.json"), req)


def test_receipt_response_validates_against_schema(tmp_path, response_schema):
    """Any successful receipt must validate against response.schema.json."""
    rc, out = _run(_req(tmp_path, ["aibom-validator"]))
    # This is a receipt (has 'artifact' key), even if overall_status is 'failed'
    # because the placeholder verifier returns 'not_implemented'.
    assert "artifact" in out, out
    _validate(response_schema, out)


def test_error_response_validates_against_schema(response_schema):
    """Any error response must also validate."""
    p = subprocess.run(
        [sys.executable, str(WORKER)],
        input="not json",
        capture_output=True,
        text=True,
    )
    assert p.returncode == 2
    out = _json.loads(p.stdout.strip())
    _validate(response_schema, out)


def test_missing_artifact_response_validates(tmp_path, response_schema):
    """Missing artifact returns an error-form response — must validate."""
    req = {
        "worker_id": "w-test",
        "release_id": "rel-test",
        "artifact_path": str(tmp_path / "does-not-exist.bin"),
        "expected_sha256": "0" * 64,
        "verifiers": ["syft"],
    }
    rc, out = _run(req)
    assert rc == 2
    _validate(response_schema, out)
