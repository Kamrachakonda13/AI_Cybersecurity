from __future__ import annotations

import hashlib, json, os, uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
from sqlalchemy.orm import Session

from ..models import ToolDefinition, ToolRelease, ToolUpdatePolicy, ToolDeployment, ToolHealthCheck, ToolArtifact
from .extended_catalog import extended_registry
from .ai_ecosystem import registry as ai_ecosystem_registry

RELEASE = "4.0"
CHANNELS = {"candidate", "canary", "stable", "extended_stable"}
PIN_MODES = {"floating", "pinned", "immutable"}
STATES = {"discovered", "verified", "healthy", "outdated", "failed", "quarantined", "frozen"}

SOURCE_CATALOG = [
    {"source_id":"cisa-kev", "name":"CISA KEV", "kind":"advisory", "cadence":"continuous", "purpose":"Prioritize actively exploited vulnerabilities affecting installed toolchains."},
    {"source_id":"nvd", "name":"NVD", "kind":"advisory", "cadence":"daily", "purpose":"CVE enrichment and severity metadata."},
    {"source_id":"osv", "name":"OSV", "kind":"advisory", "cadence":"daily", "purpose":"Open-source dependency vulnerability intelligence."},
    {"source_id":"github-advisories", "name":"GitHub Advisories", "kind":"advisory", "cadence":"daily", "purpose":"Repository and package security advisories."},
    {"source_id":"vendor-advisories", "name":"Vendor Advisories", "kind":"upstream", "cadence":"daily", "purpose":"Publisher release notes, security fixes and deprecations."},
    {"source_id":"github-releases", "name":"GitHub Releases", "kind":"release", "cadence":"daily", "purpose":"Release metadata for tools distributed from source repositories."},
    {"source_id":"package-registries", "name":"Approved Package Registries", "kind":"package", "cadence":"daily", "purpose":"Candidate package versions; never trusted without artifact verification."},
    {"source_id":"container-registries", "name":"Approved Container Registries", "kind":"container", "cadence":"daily", "purpose":"Container image candidates with digest pinning."},
    {"source_id":"linux-distro", "name":"Approved Linux Distribution Repositories", "kind":"os", "cadence":"daily", "purpose":"Distribution packages for managed workers."},
]


def now():
    return datetime.now(timezone.utc)


def canonical(obj: dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def sha256_json(obj: dict[str, Any]) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def sign_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Sign with configured Ed25519 private key when available; otherwise mark unsigned.

    Production must provide VEYRA_UPDATE_SIGNING_PRIVATE_KEY and rotate it through an
    external secret manager. We intentionally never generate or persist signing keys here.
    """
    unsigned = {k: v for k, v in manifest.items() if k != "signature"}
    payload = canonical(unsigned)
    key_pem = os.getenv("VEYRA_UPDATE_SIGNING_PRIVATE_KEY", "")
    if not key_pem:
        return {**manifest, "signature": None, "signature_status": "unsigned", "manifest_sha256": hashlib.sha256(payload).hexdigest()}
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        key = serialization.load_pem_private_key(key_pem.encode(), password=None)
        if not isinstance(key, Ed25519PrivateKey):
            raise ValueError("configured key is not Ed25519")
        sig = key.sign(payload).hex()
        return {**manifest, "signature": sig, "signature_status": "ed25519", "manifest_sha256": hashlib.sha256(payload).hexdigest()}
    except Exception as exc:
        return {**manifest, "signature": None, "signature_status": f"signing_error:{type(exc).__name__}", "manifest_sha256": hashlib.sha256(payload).hexdigest()}


def verify_release(release: ToolRelease) -> tuple[bool, list[str]]:
    errors=[]
    if not release.version or release.version == "DISCOVERY_REQUIRED": errors.append("version_missing")
    if not release.artifact_sha256 or len(release.artifact_sha256) != 64: errors.append("sha256_missing")
    if not release.artifact_uri: errors.append("artifact_uri_missing")
    if release.signature_required and not release.signature: errors.append("signature_missing")
    if release.provenance_required and not release.provenance_uri: errors.append("provenance_missing")
    if release.sbom_required and not release.sbom_uri: errors.append("sbom_missing")
    if errors: return False, errors
    return True, []


def infer_source(tool: dict) -> tuple[str, str]:
    name=(tool.get("name") or "").lower()
    if "github" in (tool.get("purpose") or "").lower() or any(x in name for x in ("nuclei","semgrep","trivy","gitleaks","osv-scanner")):
        return "github-releases", "github"
    if any(x in name for x in ("docker","kubectl","kube-bench","kube-hunter")):
        return "container-registries", "container"
    return "approved-package-source", "package"


def sync_catalog(db: Session) -> int:
    """Create durable tool definitions from the existing 588+ tool catalog without
    inventing release versions. This is idempotent and preserves operator state."""
    catalog = extended_registry() + ai_ecosystem_registry()
    seen=set(); created=0
    for tool in catalog:
        tid=str(tool.get("id") or tool.get("name","")).strip()
        if not tid or tid in seen: continue
        seen.add(tid)
        row=db.query(ToolDefinition).filter(ToolDefinition.tool_id==tid).first()
        source, resolver=infer_source(tool)
        if not row:
            row=ToolDefinition(tool_id=tid, name=tool.get("name",tid), category=tool.get("category","Security"),
                purpose=tool.get("purpose","Managed security tool"), upstream_source=source, resolver_kind=resolver,
                maturity="stable", update_channel="stable", pin_mode="floating", status="active")
            db.add(row); created+=1
        else:
            row.name=tool.get("name",row.name); row.category=tool.get("category",row.category); row.purpose=tool.get("purpose",row.purpose)
    db.commit()
    return created


def ensure_policy(db: Session, tool_id: str) -> ToolUpdatePolicy:
    p=db.query(ToolUpdatePolicy).filter(ToolUpdatePolicy.tool_id==tool_id).first()
    if p: return p
    p=ToolUpdatePolicy(tool_id=tool_id, channel="stable", pin_mode="floating", auto_update=False,
                       critical_override=True, require_canary=True, canary_percent=10, maintenance_window="weekly")
    db.add(p); db.commit(); db.refresh(p); return p


def overview(db: Session) -> dict[str, Any]:
    sync_catalog(db)
    defs=db.query(ToolDefinition).count(); releases=db.query(ToolRelease).count(); deployments=db.query(ToolDeployment).count()
    pending=db.query(ToolRelease).filter(ToolRelease.verification_status.in_(["pending","candidate"])).count()
    healthy=db.query(ToolRelease).filter(ToolRelease.health_status=="healthy").count()
    failed=db.query(ToolRelease).filter(ToolRelease.health_status.in_(["failed","quarantined"])).count()
    return {"release":RELEASE,"catalog_tools":defs,"releases":releases,"deployments":deployments,"pending_verification":pending,"healthy_releases":healthy,"failed_or_quarantined":failed,
            "channels":["candidate","canary","stable","extended_stable"],"pin_modes":["floating","pinned","immutable"],"sources":SOURCE_CATALOG,
            "cadence":{"critical_exploited":"continuous/immediate","high_security":"daily discovery; deploy after validation","normal":"daily discovery; weekly deployment","major":"planned/monthly"}}


def scout(db: Session, tool_id: str|None=None) -> list[dict[str, Any]]:
    sync_catalog(db)
    q=db.query(ToolDefinition)
    if tool_id: q=q.filter(ToolDefinition.tool_id==tool_id)
    rows=q.order_by(ToolDefinition.name).limit(1000).all()
    out=[]
    for d in rows:
        releases=db.query(ToolRelease).filter(ToolRelease.tool_id==d.tool_id).order_by(ToolRelease.discovered_at.desc()).all()
        installed=db.query(ToolDeployment).filter(ToolDeployment.tool_id==d.tool_id, ToolDeployment.state=="active").order_by(ToolDeployment.created_at.desc()).first()
        out.append({"tool_id":d.tool_id,"name":d.name,"category":d.category,"upstream_source":d.upstream_source,"maturity":d.maturity,
                    "channel":d.update_channel,"pin_mode":d.pin_mode,"installed_version":installed.target_version if installed else None,
                    "candidate_count":len(releases),"verified_candidates":[r.version for r in releases if r.verification_status=="verified"],
                    "latest_discovered":releases[0].version if releases else None,"update_status":"update_available" if any(r.verification_status=="verified" for r in releases) else "discovery_required"})
    return out


def register_release(db: Session, data: dict[str, Any]) -> dict[str, Any]:
    required=["tool_id","version","artifact_uri","artifact_sha256"]
    missing=[x for x in required if not str(data.get(x,""))]
    if missing: raise ValueError("Missing: "+", ".join(missing))
    existing=db.query(ToolRelease).filter(ToolRelease.tool_id==data["tool_id"], ToolRelease.version==data["version"]).first()
    if existing: raise ValueError("Release already registered")
    r=ToolRelease(release_id="rel_"+uuid.uuid4().hex[:16], tool_id=data["tool_id"], version=data["version"], channel=data.get("channel","candidate"),
                  artifact_uri=data["artifact_uri"], artifact_sha256=data["artifact_sha256"], artifact_digest=data.get("artifact_digest", "sha256:"+data["artifact_sha256"]),
                  signature=data.get("signature",""), signature_required=bool(data.get("signature_required",True)), provenance_uri=data.get("provenance_uri",""), provenance_required=bool(data.get("provenance_required",True)),
                  sbom_uri=data.get("sbom_uri",""), sbom_required=bool(data.get("sbom_required",True)), license=data.get("license","unknown"), source_commit=data.get("source_commit",""),
                  verification_status="candidate", health_status="unknown", notes=data.get("notes",""))
    ok, errors=verify_release(r)
    r.verification_status="verified" if ok else "rejected"
    r.verification_errors=json.dumps(errors)
    db.add(r); db.commit(); db.refresh(r)
    return {"release_id":r.release_id,"verification_status":r.verification_status,"errors":errors,"version":r.version}


def deployment_plan(db: Session, tool_id: str, release_id: str, worker_id: str, operation: str="install_or_update", force: bool=False) -> dict[str, Any]:
    r=db.query(ToolRelease).filter(ToolRelease.release_id==release_id, ToolRelease.tool_id==tool_id).first()
    if not r: raise ValueError("Release not found")
    p=ensure_policy(db,tool_id)
    if p.frozen_until and p.frozen_until > now() and not force:
        raise ValueError("Tool is frozen until " + p.frozen_until.isoformat())
    if p.pin_mode == "pinned" and p.pinned_version and r.version != p.pinned_version and not force:
        raise ValueError("Pinned policy permits only version " + p.pinned_version)
    if p.pin_mode == "immutable" and p.pinned_digest and r.artifact_digest != p.pinned_digest and not force:
        raise ValueError("Immutable policy permits only digest " + p.pinned_digest)
    if p.channel in {"stable", "extended_stable"} and r.channel not in {p.channel, "stable", "extended_stable"} and not force:
        raise ValueError("Release is not promoted to the configured channel")
    if r.verification_status!="verified": raise ValueError("Release is not verified")
    if p.pin_mode=="immutable" and not r.artifact_digest: raise ValueError("Immutable policy requires artifact digest")
    manifest={"contract_version":"4.0","operation":operation,"tool_id":tool_id,"release_id":release_id,"version":r.version,"artifact_uri":r.artifact_uri,
              "artifact_digest":r.artifact_digest,"artifact_sha256":r.artifact_sha256,"signature":r.signature,"sbom_uri":r.sbom_uri,"provenance_uri":r.provenance_uri,
              "worker_id":worker_id,"channel":p.channel,"pin_mode":p.pin_mode,"force":force,"expires_at":(now()+timedelta(hours=2)).isoformat(),
              "approval_required":not force,"policy_id":p.policy_id}
    manifest=sign_manifest(manifest)
    d=ToolDeployment(deployment_id="dep_"+uuid.uuid4().hex[:16],tool_id=tool_id,release_id=release_id,worker_id=worker_id,operation=operation,
                     target_version=r.version,state="planned",force=force,manifest_json=json.dumps(manifest),manifest_sha256=manifest["manifest_sha256"])
    db.add(d); db.commit(); db.refresh(d)
    return {"deployment_id":d.deployment_id,"state":d.state,"manifest":manifest,"safety":"worker-side signed contract; SaaS does not execute binaries"}


def rollback_plan(db: Session, tool_id: str, worker_id: str, target_release_id: str) -> dict[str, Any]:
    return deployment_plan(db,tool_id,target_release_id,worker_id,operation="rollback",force=True)
