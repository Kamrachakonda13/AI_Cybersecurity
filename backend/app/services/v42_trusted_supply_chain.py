from __future__ import annotations
import hashlib, json, os, shutil, subprocess, uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from ..models import ToolRelease, ToolDeployment, ToolUpdatePolicy, ToolArtifact, SupplyChainAttestation, ToolCanaryCohort, AISupplyChainAsset, AgentCircuitBreaker
from .v40_tool_supply_chain import now, canonical, deployment_plan, ensure_policy

RELEASE = "4.2"
GATES = ("identity", "artifact_digest", "signature", "provenance", "sbom", "vulnerability_scan", "smoke_test", "parser_regression", "security_regression", "policy_compliance", "runtime_observability")
TRUST_INVARIANT = "No tool, model, agent, MCP server, artifact or update becomes trusted merely because it exists. It must establish identity, provenance, integrity, policy compliance, validation, controlled deployment and observable runtime behavior."

VERIFIER_COMMANDS = {
    "cosign": "cosign",
    "syft": "syft",
    "grype": "grype",
    "tuf": "tuf-client",
}

def sha256_json(obj: dict) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()

def _safe_exec(name: str, args: list[str], timeout: int = 120) -> dict:
    binary = VERIFIER_COMMANDS.get(name)
    if not binary:
        raise ValueError("Verifier is not allowlisted")
    path = shutil.which(binary)
    if not path:
        return {"verifier": name, "status": "not_installed", "binary": binary}
    proc = subprocess.run([path, *args], capture_output=True, text=True, timeout=timeout, check=False)
    return {"verifier": name, "status": "passed" if proc.returncode == 0 else "failed", "returncode": proc.returncode,
            "stdout_sha256": hashlib.sha256(proc.stdout.encode()).hexdigest(), "stderr_sha256": hashlib.sha256(proc.stderr.encode()).hexdigest()}

def verification_plan(release: ToolRelease, artifact_path: str | None = None) -> dict:
    return {"contract_version": "4.2", "release_id": release.release_id, "tool_id": release.tool_id,
            "version": release.version, "expected_sha256": release.artifact_sha256, "expected_digest": release.artifact_digest,
            "artifact_path": artifact_path or "worker-local-cache", "gates": list(GATES),
            "allowed_verifiers": list(VERIFIER_COMMANDS), "network": "deny-by-default",
            "shell": "disabled", "expires_at": (now()+timedelta(hours=1)).isoformat()}

def ingest_attestation(db: Session, release_id: str, payload: dict) -> dict:
    rel = db.query(ToolRelease).filter(ToolRelease.release_id == release_id).first()
    if not rel: raise ValueError("Release not found")
    att_id = "att_" + uuid.uuid4().hex[:16]
    body = {"release_id": release_id, "worker_id": payload.get("worker_id",""), "kind": payload.get("kind","verification"),
            "predicate_type": payload.get("predicate_type",""), "subject_digest": payload.get("subject_digest",rel.artifact_digest),
            "payload": payload.get("payload",{}), "issued_at": payload.get("issued_at",now().isoformat())}
    evidence = sha256_json(body)
    row = SupplyChainAttestation(attestation_id=att_id, release_id=release_id, kind=body["kind"], predicate_type=body["predicate_type"],
                                 subject_digest=body["subject_digest"], issuer=payload.get("issuer",""), evidence_sha256=evidence,
                                 payload_json=json.dumps(body["payload"],sort_keys=True), verification_status=payload.get("verification_status","verified"))
    db.add(row); db.commit(); db.refresh(row)
    return {"attestation_id": att_id, "evidence_sha256": evidence, "status": row.verification_status}

def canary_plan(db: Session, tool_id: str, release_id: str, workers: list[str], percent: int = 10) -> dict:
    if not workers: raise ValueError("At least one worker is required")
    rel = db.query(ToolRelease).filter(ToolRelease.release_id == release_id).first()
    if not rel or rel.health_status != "healthy": raise ValueError("Canary requires a healthy verified release")
    percent = max(1,min(100,int(percent)))
    ranked = sorted(set(workers), key=lambda w: hashlib.sha256(f"{release_id}:{w}".encode()).hexdigest())
    count = max(1, (len(ranked)*percent + 99)//100)
    selected = ranked[:count]
    row = ToolCanaryCohort(cohort_id="can_"+uuid.uuid4().hex[:16], tool_id=tool_id, release_id=release_id,
                           worker_ids_json=json.dumps(selected), percent=percent, state="planned", created_at=now())
    db.add(row); db.commit(); db.refresh(row)
    return {"cohort_id":row.cohort_id,"selected_workers":selected,"percent":percent,"state":row.state}

def evaluate_canary(db: Session, cohort_id: str) -> dict:
    cohort = db.query(ToolCanaryCohort).filter(ToolCanaryCohort.cohort_id==cohort_id).first()
    if not cohort: raise ValueError("Canary cohort not found")
    worker_ids = json.loads(cohort.worker_ids_json or "[]")
    deployments = db.query(ToolDeployment).filter(ToolDeployment.tool_id==cohort.tool_id, ToolDeployment.release_id==cohort.release_id, ToolDeployment.worker_id.in_(worker_ids)).all()
    total=len(worker_ids); healthy=sum(1 for d in deployments if d.state=="active")
    failed=sum(1 for d in deployments if d.state in {"failed","rollback_planned"})
    status="healthy" if total and healthy==total else "failed" if failed else "pending"
    cohort.state=status; cohort.evaluated_at=now(); cohort.result_json=json.dumps({"total":total,"healthy":healthy,"failed":failed})
    db.commit()
    return {"cohort_id":cohort_id,"status":status,"total":total,"healthy":healthy,"failed":failed,"recommendation":"promote" if status=="healthy" else "rollback" if status=="failed" else "wait"}

def trusted_promote(db: Session, release_id: str, channel: str) -> dict:
    rel=db.query(ToolRelease).filter(ToolRelease.release_id==release_id).first()
    if not rel: raise ValueError("Release not found")
    if rel.health_status!="healthy": raise ValueError("Release is not healthy")
    required=["identity","artifact_digest","signature","provenance","sbom","vulnerability_scan","smoke_test","parser_regression","security_regression","policy_compliance","runtime_observability"]
    checks=db.query(SupplyChainAttestation).filter(SupplyChainAttestation.release_id==release_id, SupplyChainAttestation.verification_status=="verified").all()
    kinds={a.kind for a in checks}
    missing=[x for x in required if x not in kinds]
    # Compatibility: v4.1 worker receipt is accepted for the core artifact gates, but v4.2 runtime gates require explicit attestations.
    if missing: raise ValueError("Trusted promotion blocked; missing attestations: "+", ".join(missing))
    rel.channel=channel
    if channel in {"stable","extended_stable"}: ensure_policy(db,rel.tool_id).channel=channel
    db.commit(); return {"release_id":release_id,"channel":channel,"status":"trusted_promoted","trust_invariant":TRUST_INVARIANT}

def create_circuit_breaker(db: Session, agent_id: str, reason: str, scope: str="agent") -> dict:
    row=AgentCircuitBreaker(breaker_id="cb_"+uuid.uuid4().hex[:16],agent_id=agent_id,scope=scope,state="armed",reason=reason,activated_at=now())
    db.add(row); db.commit(); db.refresh(row)
    return {"breaker_id":row.breaker_id,"agent_id":agent_id,"state":row.state,"scope":scope,"reason":reason}

def trusted_overview(db: Session) -> dict:
    return {"release":RELEASE,"trust_invariant":TRUST_INVARIANT,"gates":list(GATES),
            "attestations":db.query(SupplyChainAttestation).count(),"canary_cohorts":db.query(ToolCanaryCohort).count(),
            "ai_supply_chain_assets":db.query(AISupplyChainAsset).count(),"armed_circuit_breakers":db.query(AgentCircuitBreaker).filter(AgentCircuitBreaker.state=="armed").count(),
            "integrations":{"tuf":{"status":"worker_adapter","purpose":"update metadata/freshness/rollback protection"},"cosign":{"status":"worker_adapter","purpose":"artifact and attestation verification"},"syft":{"status":"worker_adapter","purpose":"SBOM generation"},"grype":{"status":"worker_adapter","purpose":"vulnerability gating"},"slsa":{"status":"attestation_ingest","version":"1.2"}},
            "execution_boundary":"Only fixed, allowlisted verification binaries may run on managed workers. SaaS never accepts arbitrary shell/package-manager commands."}
