from __future__ import annotations
import hashlib, json, os, uuid
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session
from ..models import ToolRelease, ToolArtifact, ToolDeployment, ToolHealthCheck, ToolUpdatePolicy
from .v40_tool_supply_chain import deployment_plan, ensure_policy, now, canonical

RELEASE = "4.1"
CHECKS = ("artifact_digest", "signature", "provenance", "sbom", "vulnerability_scan", "smoke_test", "parser_regression", "security_regression")


def evidence_hash(payload: dict) -> str:
    return hashlib.sha256(canonical(payload)).hexdigest()


def _hex64(value: str) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


def accept_verification_report(db: Session, release_id: str, worker_id: str, report: dict) -> dict:
    """Accept a structured report from an isolated verification/managed worker.

    The control plane never executes the artifact. The worker proves what it verified,
    with immutable digest/evidence references and a signed receipt when available.
    """
    rel = db.query(ToolRelease).filter(ToolRelease.release_id == release_id).first()
    if not rel:
        raise ValueError("Release not found")
    if not worker_id:
        raise ValueError("worker_id is required")
    checks = report.get("checks") or {}
    missing = [c for c in CHECKS if c not in checks]
    if missing:
        raise ValueError("Verification report missing checks: " + ", ".join(missing))
    observed_sha = report.get("artifact_sha256", "")
    if not _hex64(observed_sha):
        raise ValueError("artifact_sha256 must be a 64-character hexadecimal digest")
    if observed_sha.lower() != rel.artifact_sha256.lower():
        raise ValueError("artifact digest mismatch; release remains rejected")

    failed = [k for k, v in checks.items() if not bool(v.get("passed", False))]
    status = "healthy" if not failed else "failed"
    receipt = {
        "receipt_version": "4.1",
        "release_id": release_id,
        "worker_id": worker_id,
        "artifact_sha256": observed_sha,
        "checks": checks,
        "tool_version": rel.version,
        "verified_at": now().isoformat(),
        "worker_identity": report.get("worker_identity", worker_id),
        "policy_hash": report.get("policy_hash", ""),
        "signature_status": report.get("signature_status", "unknown"),
        "provenance_status": report.get("provenance_status", "unknown"),
        "sbom_status": report.get("sbom_status", "unknown"),
    }
    ev = evidence_hash(receipt)
    receipt["receipt_sha256"] = ev

    hc = ToolHealthCheck(check_id="hc_" + uuid.uuid4().hex[:16], release_id=release_id, worker_id=worker_id,
                         status=status, checks_json=json.dumps(receipt, sort_keys=True), evidence_sha256=ev,
                         notes="; ".join(failed) if failed else "All required release validation gates passed.",
                         completed_at=now())
    db.add(hc)
    rel.health_status = status
    rel.verification_status = "verified" if status == "healthy" else "rejected"

    art = db.query(ToolArtifact).filter(ToolArtifact.release_id == release_id).first()
    if not art:
        art = ToolArtifact(artifact_id="art_" + uuid.uuid4().hex[:16], release_id=release_id,
                           storage_uri=rel.artifact_uri, digest=rel.artifact_digest, sha256=rel.artifact_sha256,
                           signature_status="verified" if checks["signature"].get("passed") else "failed",
                           provenance_status="verified" if checks["provenance"].get("passed") else "failed",
                           sbom_status="verified" if checks["sbom"].get("passed") else "failed", immutable=True)
        db.add(art)
    else:
        art.signature_status = "verified" if checks["signature"].get("passed") else "failed"
        art.provenance_status = "verified" if checks["provenance"].get("passed") else "failed"
        art.sbom_status = "verified" if checks["sbom"].get("passed") else "failed"

    deployment_id = report.get("deployment_id")
    rollback = None
    if deployment_id:
        dep = db.query(ToolDeployment).filter(ToolDeployment.deployment_id == deployment_id).first()
        if dep:
            dep.worker_receipt_json = json.dumps(receipt, sort_keys=True)
            dep.state = "active" if status == "healthy" else "failed"
            dep.completed_at = now()
            if status == "failed" and bool(report.get("auto_rollback", True)):
                prior = (db.query(ToolDeployment)
                         .filter(ToolDeployment.tool_id == dep.tool_id, ToolDeployment.worker_id == dep.worker_id,
                                 ToolDeployment.state == "active", ToolDeployment.target_version != dep.target_version)
                         .order_by(ToolDeployment.completed_at.desc()).first())
                if prior:
                    rollback = deployment_plan(db, dep.tool_id, prior.release_id, dep.worker_id, operation="rollback", force=True)
                    dep.state = "rollback_planned"
    db.commit()
    return {"release_id": release_id, "health_status": status, "failed_checks": failed,
            "health_check_id": hc.check_id, "evidence_sha256": ev, "rollback": rollback,
            "message": "Verification receipt accepted; no artifact execution occurred in the control plane."}


def promote_release(db: Session, release_id: str, target_channel: str) -> dict:
    allowed = {"candidate", "canary", "stable", "extended_stable"}
    if target_channel not in allowed:
        raise ValueError("Invalid channel")
    rel = db.query(ToolRelease).filter(ToolRelease.release_id == release_id).first()
    if not rel:
        raise ValueError("Release not found")
    if rel.health_status != "healthy":
        raise ValueError("Only healthy releases can be promoted")
    policy = ensure_policy(db, rel.tool_id)
    if policy.frozen_until and policy.frozen_until > now():
        raise ValueError("Tool is frozen until " + policy.frozen_until.isoformat())
    rel.channel = target_channel
    if target_channel in {"stable", "extended_stable"}:
        policy.channel = target_channel
    db.commit()
    return {"release_id": release_id, "channel": target_channel, "status": "promoted"}


def rollback_on_failure(db: Session, deployment_id: str, reason: str = "health regression") -> dict:
    dep = db.query(ToolDeployment).filter(ToolDeployment.deployment_id == deployment_id).first()
    if not dep:
        raise ValueError("Deployment not found")
    prior = (db.query(ToolDeployment)
             .filter(ToolDeployment.tool_id == dep.tool_id, ToolDeployment.worker_id == dep.worker_id,
                     ToolDeployment.state == "active", ToolDeployment.target_version != dep.target_version)
             .order_by(ToolDeployment.completed_at.desc()).first())
    if not prior:
        raise ValueError("No verified active prior release available for rollback")
    result = deployment_plan(db, dep.tool_id, prior.release_id, dep.worker_id, operation="rollback", force=True)
    dep.state = "rollback_planned"
    db.commit()
    return {"reason": reason, "source_deployment": deployment_id, "rollback": result}


def runtime_overview(db: Session) -> dict:
    return {
        "release": RELEASE,
        "verification_checks": list(CHECKS),
        "artifact_policy": "immutable digest + worker receipt",
        "promotion": "healthy-only",
        "rollback": "automatic plan on failed canary/health report when prior active release exists",
        "execution_boundary": "verification and binary operations occur only on managed workers; control plane never runs arbitrary shell/package-manager commands",
        "production_integrations": ["TUF", "Cosign/Sigstore", "Syft", "Grype", "SLSA v1.2/in-toto"],
    }
