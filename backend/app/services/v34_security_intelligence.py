"""AegisX v3.4 Security Intelligence & Continuous Control Validation.

Read-only orchestration metadata. It does not execute security tools or perform
intrusion/hack-back. It turns existing telemetry/control-plane data into a
repeatable validation plan and prioritised defensive backlog.
"""
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Asset, Finding, Incident, Identity, CloudResource, AIAsset, SecurityToolJob, SecurityEvidence
from .security_readiness import documentation_readiness, CONTROL_DOMAINS

CONTROL_TESTS = [
    {"id":"identity-least-privilege","domain":"identity","name":"Identity & least-privilege validation","frequency":"daily","evidence":["identity inventory","privilege review","session anomalies"]},
    {"id":"external-attack-surface","domain":"scope","name":"External attack-surface validation","frequency":"daily","evidence":["asset inventory","service exposure","scope record"]},
    {"id":"worker-integrity","domain":"worker","name":"Managed-worker integrity validation","frequency":"daily","evidence":["worker health","tool versions","provenance"]},
    {"id":"evidence-chain","domain":"evidence","name":"Evidence-chain validation","frequency":"daily","evidence":["hashes","timestamps","receipts"]},
    {"id":"ai-agent-controls","domain":"ai-runtime","name":"AI agent runtime-control validation","frequency":"continuous","evidence":["agent traces","policy decisions","tool calls"]},
    {"id":"ai-data-boundaries","domain":"ai-data","name":"AI/RAG data-boundary validation","frequency":"continuous","evidence":["retrieval traces","source provenance","data-policy results"]},
    {"id":"supply-chain","domain":"supply-chain","name":"Software/model supply-chain validation","frequency":"daily","evidence":["SBOM/AIBOM","signatures","dependency findings"]},
    {"id":"detection-coverage","domain":"detection","name":"Detection coverage validation","frequency":"hourly","evidence":["alerts","rule coverage","telemetry health"]},
    {"id":"recovery-exercise","domain":"resilience","name":"Recovery and containment exercise","frequency":"weekly","evidence":["exercise record","containment receipt","recovery verification"]},
    {"id":"documentation","domain":"documentation","name":"Tool documentation contract validation","frequency":"on-change","evidence":["tool registry","Markdown pages","validation report"]},
]

def _counts(db: Session):
    return {
        "assets": db.query(func.count(Asset.id)).scalar() or 0,
        "findings": db.query(func.count(Finding.id)).scalar() or 0,
        "incidents": db.query(func.count(Incident.id)).scalar() or 0,
        "identities": db.query(func.count(Identity.id)).scalar() or 0,
        "cloud_resources": db.query(func.count(CloudResource.id)).scalar() or 0,
        "ai_assets": db.query(func.count(AIAsset.id)).scalar() or 0,
        "jobs": db.query(func.count(SecurityToolJob.id)).scalar() or 0,
        "evidence": db.query(func.count(SecurityEvidence.id)).scalar() or 0,
    }

def intelligence_overview(db: Session):
    counts = _counts(db)
    doc = documentation_readiness()
    signals = []
    if doc["missing_tools"]: signals.append({"priority":"high","id":"documentation","message":f"{len(doc['missing_tools'])} tool pages need documentation."})
    if counts["findings"]: signals.append({"priority":"medium","id":"findings","message":f"{counts['findings']} findings are present; run triage and remediation verification."})
    if counts["incidents"]: signals.append({"priority":"high","id":"incidents","message":f"{counts['incidents']} incidents exist; confirm containment and recovery evidence."})
    if counts["ai_assets"]: signals.append({"priority":"high","id":"ai-runtime","message":f"{counts['ai_assets']} AI assets are inventoried; verify agent identity, tool policy and traceability."})
    if counts["cloud_resources"]: signals.append({"priority":"medium","id":"cloud","message":f"{counts['cloud_resources']} cloud resources are inventoried; validate IAM and external exposure."})
    return {"release":"3.4","generated_at":datetime.now(timezone.utc).isoformat(),"inventory":counts,"documentation":doc,"control_tests":CONTROL_TESTS,"signals":signals,"principle":"continuous validation produces plans and evidence requirements; governed workers execute only explicitly authorised tests."}

def validation_plan(db: Session):
    overview=intelligence_overview(db)
    return {"plan_id":"cv-"+datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S'),"generated_at":overview["generated_at"],"tests":[{**t,"status":"ready_for_governed_execution","scope_required":True,"approval_required":True} for t in CONTROL_TESTS],"priority_signals":overview["signals"]}
