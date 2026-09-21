"""AegisX v3.2 Team Academy and documentation index.

Read-only metadata. This service does not execute security tools.
"""
from __future__ import annotations
from .sudo_arsenal import _all_tools

LEVELS = [
    {"id":"beginner","name":"Beginner","goal":"Understand the purpose, evidence and defensive value of a security tool before running it."},
    {"id":"intermediate","name":"Intermediate","goal":"Run repeatable authorized assessments and interpret findings."},
    {"id":"advanced","name":"Advanced","goal":"Correlate multiple tools, telemetry and attack paths."},
    {"id":"expert","name":"Expert","goal":"Design governed red/blue/purple exercises, detection logic and remediation verification."},
]

TRACKS = [
    ("soc-defender","SOC / Blue Team","Network, endpoint, identity, cloud, DFIR, threat intelligence and response."),
    ("red-team","Red / Purple Team","Authorized attack-surface validation, safe exploit validation, evidence and detection testing."),
    ("ai-security","AI Security Engineer","LLM, agent, MCP/A2A, RAG, model, data, supply-chain and runtime security."),
    ("cloud-k8s","Cloud & Kubernetes","Cloud posture, IAM, containers, Kubernetes, runtime and supply-chain security."),
    ("dfir","DFIR / Malware","Evidence preservation, memory, disk, network, malware triage and reverse engineering."),
    ("security-engineering","Security Engineering","Detection engineering, automation, governance, workers and security architecture."),
]

def academy_overview():
    tools = _all_tools()
    return {
        "release":"3.2",
        "tool_count":len(tools),
        "levels":LEVELS,
        "tracks":[{"id":a,"name":b,"description":c} for a,b,c in TRACKS],
        "documentation_contract":[
            "purpose", "when_to_use", "ui_workflow", "terminal_start", "permissions", "scope", "evidence", "interpretation", "remediation", "verification", "common_mistakes"
        ],
        "execution_rule":"Documentation may teach and explain; execution remains governed by scope, authorization, approval and managed workers.",
    }

def recommended_curriculum(track: str):
    tools = _all_tools()
    if track == "ai-security":
        cats={"LLM Red Team","LLM Evaluation","Agent Evaluation","Agent Security","MCP Security","A2A Security","AI Gateway","AI Observability","RAG Security","Vector DB Security","Model Security","Adversarial ML","AI Supply Chain","AI Governance","AI Threat Intelligence","Agent Memory Security","Agent Identity","Agent Supply Chain"}
    elif track == "soc-defender":
        cats={"Network Defense","DFIR","Forensics","Endpoint","Threat Intelligence","Detection Engineering","Identity","Cloud","Kubernetes","AI SOC","AI Incident Response"}
    elif track == "red-team":
        cats={"Network Discovery","Web/API","AppSec","Wireless","Vulnerability","Exploit Validation","Identity/Network","Cloud","Kubernetes","AI Red Team","LLM Red Team","Agent Evaluation"}
    elif track == "cloud-k8s":
        cats={"Cloud","Cloud/Container","Kubernetes","IaC","AI Supply Chain","Vector DB Security"}
    elif track == "dfir":
        cats={"DFIR","Forensics","Malware","Reverse Engineering","Network Defense","Threat Intelligence"}
    else:
        cats={"Detection Engineering","Security Utilities","AI Security","AI Gateway","AI Observability","AI Governance","AI Supply Chain"}
    selected=[t for t in tools if t.get("category") in cats]
    return {"track":track,"tool_count":len(selected),"tools":[{"id":t["id"],"name":t["name"],"category":t.get("category"),"purpose":t.get("purpose"),"access_tier":t.get("access_tier"),"execution_profile":t.get("execution_profile")} for t in selected]}
