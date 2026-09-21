"""VEYRA v3.5 Security Lifecycle orchestration.

This service turns the product philosophy into a deterministic lifecycle model.
It creates plans, readiness scores and evidence requirements only. It never
executes offensive commands, performs hack-back, or bypasses approval gates.
"""
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Asset, Finding, Incident, Identity, CloudResource, AIAsset, SecurityToolJob, SecurityEvidence

STAGES = [
    ("discover", "Discover", "Inventory assets, identities, services, AI systems, cloud resources and exposed surfaces.", ["asset inventory", "service inventory", "AI asset inventory"]),
    ("understand", "Understand", "Explain ownership, criticality, trust relationships, dependencies and expected baselines.", ["ownership", "criticality", "dependency map"]),
    ("validate", "Validate", "Run authorized control and exposure checks through governed managed workers.", ["scope record", "approval", "test result"]),
    ("investigate", "Investigate", "Preserve and examine suspicious findings, alerts, sessions, endpoints and AI traces.", ["timeline", "endpoint evidence", "AI trace"]),
    ("correlate", "Correlate", "Join network, identity, cloud, endpoint, AI and threat-intelligence evidence.", ["correlation links", "threat intel", "security graph"]),
    ("contain", "Contain", "Stage bounded containment actions for authorized approval and execution.", ["containment plan", "approval receipt", "action receipt"]),
    ("recover", "Recover", "Restore trusted state and verify credentials, configurations, workloads and services.", ["recovery checklist", "verification result"]),
    ("prove", "Prove", "Produce tamper-evident evidence, hashes, provenance and control attestations.", ["evidence hashes", "provenance", "control attestation"]),
    ("learn", "Learn", "Turn incidents and exercises into remediation, detections, playbooks and training.", ["lesson learned", "detection update", "training item"]),
    ("revalidate", "Continuously revalidate", "Schedule repeat checks and detect security drift over time.", ["schedule", "baseline comparison", "validation history"]),
]

def _counts(db: Session):
    return {"assets": db.query(func.count(Asset.id)).scalar() or 0,
            "findings": db.query(func.count(Finding.id)).scalar() or 0,
            "incidents": db.query(func.count(Incident.id)).scalar() or 0,
            "identities": db.query(func.count(Identity.id)).scalar() or 0,
            "cloud_resources": db.query(func.count(CloudResource.id)).scalar() or 0,
            "ai_assets": db.query(func.count(AIAsset.id)).scalar() or 0,
            "jobs": db.query(func.count(SecurityToolJob.id)).scalar() or 0,
            "evidence": db.query(func.count(SecurityEvidence.id)).scalar() or 0}

def lifecycle_overview(db: Session):
    counts=_counts(db)
    blocked=[]
    if not counts["assets"]: blocked.append("discover")
    if counts["incidents"] and not counts["evidence"]: blocked.append("prove")
    if counts["findings"] and not counts["jobs"]: blocked.append("validate")
    return {"release":"3.5", "generated_at":datetime.now(timezone.utc).isoformat(),
            "principle":"Discover → Understand → Validate → Investigate → Correlate → Contain → Recover → Prove → Learn → Continuously revalidate",
            "inventory":counts,
            "stages":[{"id":i,"name":n,"description":d,"evidence":e,"status":"attention" if i in blocked else "ready"} for i,n,d,e in STAGES],
            "guardrails":["explicit authorization scope","Sudo/RBAC","human approval for high-impact actions","isolated managed workers","signed job contracts","evidence hashing","audit logging","hack-back disabled"]}

def lifecycle_plan(db: Session, focus: str | None = None):
    o=lifecycle_overview(db)
    stages=o["stages"]
    if focus:
        stages=[s for s in stages if s["id"]==focus]
    return {"plan_id":"lifecycle-"+datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S'),
            "generated_at":o["generated_at"], "focus":focus or "all", "stages":stages,
            "next_action":"Use the earliest attention stage first; execution requires authorized scope, approval and an isolated worker.",
            "execution":"plan_only"}
