"""AegisX v3.3 Security Readiness and Continuous Validation.

Read-only control-plane metadata plus documentation/readiness validation.
No security tool execution occurs in this service.
"""
from __future__ import annotations
from pathlib import Path
from .sudo_arsenal import _all_tools

ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / "docs" / "tools"

CONTROL_DOMAINS = [
    ("identity", "Identity & Privilege", "Least privilege, Sudo, MFA/PAM, session controls and time-boxed grants."),
    ("scope", "Scope & Authorization", "Explicit target scope, environment, purpose and approval before governed execution."),
    ("worker", "Managed Worker", "Isolated execution, version pinning, health checks and capability boundaries."),
    ("evidence", "Evidence & Provenance", "Normalized evidence, hashes, timestamps, provenance and retention."),
    ("ai-runtime", "AI Runtime Control", "Agent identity, tool allowlists, policy hooks, traceability and runtime controls."),
    ("ai-data", "AI Data Security", "Prompt, context, memory, RAG, vector-store and sensitive-data controls."),
    ("supply-chain", "Software & AI Supply Chain", "SBOM/AIBOM, signing, provenance, dependency and model-artifact controls."),
    ("detection", "Detection & Response", "Detections, triage, investigation, containment and recovery verification."),
    ("resilience", "Recovery & Exercises", "Tabletops, purple-team validation, backups, recovery tests and lessons learned."),
    ("documentation", "Team Documentation", "Per-tool explanations, UI workflow, terminal starting point and remediation guidance."),
]

EXERCISES = [
    {"id":"ai-agent-abuse", "name":"AI Agent Abuse Drill", "track":"ai-security", "goal":"Detect and contain an agent attempting an unauthorized high-impact tool action.", "evidence":["agent trace","policy decision","tool request","approval record","containment receipt"]},
    {"id":"prompt-rag-poisoning", "name":"Prompt + RAG Integrity Drill", "track":"ai-security", "goal":"Identify malicious or untrusted context and verify that retrieval and output controls hold.", "evidence":["prompt trace","retrieval trace","source provenance","policy result","verification report"]},
    {"id":"wifi-intrusion", "name":"Wireless Intrusion Response", "track":"soc-defender", "goal":"Detect an unauthorized wireless device/AP, correlate it to LAN observations and contain safely.", "evidence":["Wi-Fi observations","BSSID/device identity","DHCP/DNS events","timeline","containment plan"]},
    {"id":"identity-compromise", "name":"Identity Compromise Drill", "track":"soc-defender", "goal":"Correlate suspicious authentication, privilege changes and endpoint activity.", "evidence":["auth events","identity graph","endpoint telemetry","timeline","recovery verification"]},
    {"id":"cloud-exposure", "name":"Cloud Exposure Validation", "track":"cloud-k8s", "goal":"Find excessive exposure or IAM privilege and verify remediation without disruptive testing.", "evidence":["cloud findings","IAM graph","configuration snapshot","remediation receipt","verification"]},
    {"id":"malware-triage", "name":"Malware Triage Drill", "track":"dfir", "goal":"Preserve evidence, triage a sample and produce a defensible investigation record.", "evidence":["hashes","static analysis","YARA/capa results","timeline","analyst notes"]},
]

def documentation_readiness():
    tools = _all_tools()
    missing=[]; present=0
    for t in tools:
        p=DOCS / f"{t['id']}.md"
        if p.exists(): present += 1
        else: missing.append(t['id'])
    return {"registered_tools":len(tools),"documented_tools":present,"missing_tools":missing,"coverage_percent":round((present/len(tools)*100) if tools else 100,2)}

def readiness_overview():
    return {
        "release":"3.3",
        "domains":[{"id":a,"name":b,"description":c} for a,b,c in CONTROL_DOMAINS],
        "documentation":documentation_readiness(),
        "exercise_count":len(EXERCISES),
        "execution_boundary":"Readiness checks and exercises describe or validate governed workflows; arbitrary commands and hack-back are not exposed by this API.",
    }

def exercise_library(track: str|None=None):
    rows=[x for x in EXERCISES if not track or x["track"]==track]
    return {"track":track or "all","exercises":rows}
