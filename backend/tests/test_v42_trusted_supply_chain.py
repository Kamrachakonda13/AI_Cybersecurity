from pathlib import Path as _Path
import sys as _sys
import subprocess as _subprocess
import os as _os
import json as _json
import hashlib as _hashlib
from app.services.v42_trusted_supply_chain import verification_plan, ingest_attestation, canary_plan, trusted_overview
from app.services.v41_supply_chain_runtime import accept_verification_report
from app.services.v40_tool_supply_chain import register_release
from app.models import ToolDefinition, ToolRelease, SupplyChainAttestation
from app.db import SessionLocal, Base, engine
import app.models
Base.metadata.create_all(bind=engine)


def _db(): return SessionLocal()


def _report(sha):
    checks = {k: {"passed": True, "evidence": "fixture"} for k in (
        "artifact_digest", "signature", "provenance", "sbom", "vulnerability_scan", "smoke_test", "parser_regression", "security_regression")}
    return {"worker_id": "v42-worker", "artifact_sha256": sha, "checks": checks, "signature_status": "verified", "provenance_status": "verified", "sbom_status": "verified"}


def test_v42_trusted_attestation_and_plan():
    db = _db()
    try:
        import uuid
        tool = "v42-tool-"+uuid.uuid4().hex[:8]
        sha = "c"*64
        db.add(ToolDefinition(tool_id=tool, name="V42 Tool", category="Test",
               purpose="test", upstream_source="test", resolver_kind="package"))
        db.commit()
        r = register_release(db, {"tool_id": tool, "version": "3.0.0", "artifact_uri": "vault://v42/test",
                             "artifact_sha256": sha, "signature_required": False, "provenance_required": False, "sbom_required": False})
        rel = db.query(ToolRelease).filter(
            ToolRelease.release_id == r["release_id"]).first()
        assert verification_plan(rel)["contract_version"] == "4.2"
        vr = accept_verification_report(
            db, rel.release_id, "v42-worker", _report(sha))
        assert vr["health_status"] == "healthy"
        for kind in ("identity", "artifact_digest", "signature", "provenance", "sbom", "vulnerability_scan", "smoke_test", "parser_regression", "security_regression", "policy_compliance", "runtime_observability"):
            ingest_attestation(db, rel.release_id, {
                               "worker_id": "v42-worker", "kind": kind, "subject_digest": "sha256:"+sha})
        cohort = canary_plan(db, tool, rel.release_id, ["w1", "w2", "w3"], 50)
        assert len(cohort["selected_workers"]) == 2
    finally:
        db.close()


def test_v42_overview_exposes_invariant():
    db = _db()
    try:
        o = trusted_overview(db)
        assert "No tool, model, agent" in o["trust_invariant"]
        assert "slsa" in o["integrations"]
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Regression tests: fail-closed behavior for worker/v42/veyra_trusted_verifier.py
# ---------------------------------------------------------------------------


_WORKER = _Path(__file__).resolve(
).parents[2] / "worker" / "v42" / "veyra_trusted_verifier.py"


def _run_worker(artifact, expected, verifier, empty_path=False):
    env = dict(_os.environ)
    if empty_path:
        env["PATH"] = ""
    p = _subprocess.run(
        [
            _sys.executable, str(_WORKER),
            "--artifact", str(artifact),
            "--expected-sha256", expected,
            "--verifier", verifier,
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    try:
        out = _json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        out = {"raw_stdout": p.stdout, "raw_stderr": p.stderr}
    return p.returncode, out


def test_v42_fails_closed_when_verifier_missing(tmp_path):
    """Regression: if the verifier binary isn't installed, result MUST be
    failed — even when the artifact digest matches. This locks in the
    fail-closed behavior of commit fce4ddb."""
    art = tmp_path / "artifact.bin"
    art.write_bytes(b"hello")
    expected = _hashlib.sha256(b"hello").hexdigest()

    rc, out = _run_worker(art, expected, "cosign", empty_path=True)

    assert rc == 2, out
    assert out["status"] == "failed", out
    assert out["digest_match"] is True
    assert out["verification"]["status"] == "not_installed"


def test_v42_digest_mismatch_fails(tmp_path):
    """Digest mismatch must always fail, regardless of verifier state."""
    art = tmp_path / "artifact.bin"
    art.write_bytes(b"hello")
    wrong = _hashlib.sha256(b"goodbye").hexdigest()

    rc, out = _run_worker(art, wrong, "cosign", empty_path=True)

    assert rc == 2, out
    assert out["status"] == "failed", out
    assert out["digest_match"] is False


def test_v42_missing_artifact_reports_failure(tmp_path):
    """Missing artifact must exit non-zero with a structured failure."""
    rc, out = _run_worker(tmp_path / "nope.bin", "0" *
                          64, "cosign", empty_path=True)
    assert rc == 2, out
    assert out["status"] == "failed", out
