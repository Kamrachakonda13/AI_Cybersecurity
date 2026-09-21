"""Governed security-tool execution/evidence control plane.

This POC deliberately does not execute arbitrary security-tool commands. It
creates a signed-by-provenance-style job contract, validates scope/approval,
and accepts normalized evidence from a separately isolated worker. A production
worker can consume the same contract after independent authorization.
"""
from __future__ import annotations
import hashlib, json, uuid, hmac, os
from datetime import datetime, timezone

ALLOWED_ENVIRONMENTS = {"lab", "approved_worker"}
MAX_SCOPE_ITEMS = 100
MAX_EVIDENCE_BYTES = 5 * 1024 * 1024


def _utc():
    return datetime.now(timezone.utc)


def make_job_contract(tool: dict, target: str, scope: list[str], approval_ticket: str,
                       environment: str, purpose: str, actor: str = "admin") -> dict:
    if environment not in ALLOWED_ENVIRONMENTS:
        raise ValueError("environment must be lab or approved_worker")
    if not target.strip():
        raise ValueError("target is required")
    if not scope or len(scope) > MAX_SCOPE_ITEMS:
        raise ValueError(f"scope must contain 1..{MAX_SCOPE_ITEMS} entries")
    if not approval_ticket.strip():
        raise ValueError("approval_ticket is required")
    if not purpose.strip():
        raise ValueError("purpose is required")
    if tool["execution_profile"] == "isolated_lab_only" and environment != "lab":
        raise ValueError("this tool is restricted to the isolated lab")
    contract = {
        "job_id": str(uuid.uuid4()),
        "tool": tool["name"],
        "tool_id": tool["id"],
        "execution_profile": tool["execution_profile"],
        "target": target.strip(),
        "scope": [x.strip() for x in scope if x.strip()],
        "approval_ticket": approval_ticket.strip(),
        "environment": environment,
        "purpose": purpose.strip(),
        "actor": actor,
        "created_at": _utc().isoformat(),
        "execution": "not_started",
        "browser_shell": False,
    }
    contract["contract_sha256"] = hashlib.sha256(
        json.dumps(contract, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    secret = os.getenv("VEYRA_WORKER_SIGNING_SECRET", "")
    if secret:
        contract["contract_signature"] = hmac.new(secret.encode(), contract["contract_sha256"].encode(), hashlib.sha256).hexdigest()
    else:
        contract["contract_signature"] = ""
    return contract

def verify_contract_signature(contract_sha256: str, signature: str) -> bool:
    secret = os.getenv("VEYRA_WORKER_SIGNING_SECRET", "")
    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode(), contract_sha256.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def normalize_evidence(job_id: str, payload: dict, raw_size: int | None = None) -> dict:
    if raw_size is not None and raw_size > MAX_EVIDENCE_BYTES:
        raise ValueError("evidence payload exceeds 5 MB limit")
    if not isinstance(payload, dict):
        raise ValueError("evidence must be a JSON object")
    artifact = {
        "artifact_id": str(uuid.uuid4()),
        "job_id": job_id,
        "sha256": hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest(),
        "source": str(payload.get("source", "isolated-worker"))[:255],
        "collector": str(payload.get("collector", "worker"))[:255],
        "collected_at": str(payload.get("collected_at", _utc().isoformat()))[:64],
        "classification": str(payload.get("classification", "internal"))[:32],
        "result_type": str(payload.get("result_type", "normalized"))[:64],
        "summary": str(payload.get("summary", ""))[:2000],
        "data": payload.get("data", {}),
    }
    return artifact
