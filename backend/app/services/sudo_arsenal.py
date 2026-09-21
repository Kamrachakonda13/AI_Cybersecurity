"""VEYRA v3.1 Sudo Security Arsenal and Adversary Trace metadata.

This module is a policy/read-model layer. It never executes third-party security
commands. Actual tooling remains on authenticated, isolated managed workers.
"""
from __future__ import annotations
from datetime import datetime, timezone
from .extended_catalog import extended_registry
from .ai_ecosystem import registry as ai_registry
from .ai_cutting_edge_2026 import registry as ai_cutting_edge_registry


def _all_tools():
    rows = extended_registry()
    seen = {x["id"] for x in rows}
    for source in (ai_registry, ai_cutting_edge_registry):
        for x in source():
            if x["id"] not in seen:
                rows.append(x)
                seen.add(x["id"])
    return rows


def arsenal_overview():
    tools = _all_tools()
    categories = {}
    for t in tools:
        categories[t["category"]] = categories.get(t["category"], 0) + 1
    return {
        "release": "3.1",
        "name": "Sudo Security Arsenal & Adversary Trace Fabric",
        "tool_count": len(tools),
        "privileged_count": sum(1 for t in tools if t.get("access_tier") == "privileged_admin" or t.get("privileged_usage")),
        "categories": dict(sorted(categories.items())),
        "execution_model": ["scope", "authorization", "approval", "managed worker", "evidence", "audit"],
        "terminal_policy": "Terminal access is worker-local and policy-bound; VEYRA SaaS does not expose an arbitrary browser shell.",
        "hack_back": "disabled",
        "attribution": "hypothesis_and_evidence_based",
    }


def list_tools(category: str | None = None, privileged_only: bool = False):
    rows = _all_tools()
    if category:
        rows = [x for x in rows if x.get(
            "category", "").lower() == category.lower()]
    if privileged_only:
        rows = [x for x in rows if x.get(
            "access_tier") == "privileged_admin" or x.get("privileged_usage")]
    return rows


def tool_detail(tool_id: str):
    for t in _all_tools():
        if t["id"] == tool_id:
            help_meta = t.get("help", {})
            return {
                **t,
                "ui_usage": {
                    "step_1": "Open Sudo Security Arsenal and select the tool.",
                    "step_2": "Choose an approved asset/scope and assessment profile.",
                    "step_3": "Provide purpose and approval context; privileged tools require the Sudo gate.",
                    "step_4": "Review the generated job contract before queueing the managed worker.",
                    "step_5": "Review normalized evidence, hashes, provenance and remediation guidance.",
                },
                "terminal_usage": {
                    "first_check": f"sudo -n {tool_id} --help",
                    "policy": "Run only from an enrolled VEYRA managed worker against an explicitly authorized scope.",
                    "safe_start": "Prefer the tool's help/version command first; use only the worker-generated command profile for active assessment.",
                    "evidence": "Capture stdout/stderr, exit code, timestamps, target scope, tool version and artifact hashes into the VEYRA evidence bundle.",
                },
                "help_boundary": help_meta.get("help_boundary", "Governed security operations. VEYRA enables authorized security testing, red-team, blue-team, and defensive work on owned or explicitly permitted targets. Tools are tiered by risk: Standard (discovery, analysis, defensive verification), Privileged (high-impact testing requires privileged_admin and an approved engagement), and Isolated Lab Only (attack-capable tools may only run against lab/sandbox targets). All executions are scope-bound, evidence-captured, and audited. Out-of-scope activity, unowned targets, and unauthorized use are prohibited."),
            }
    return None


def build_trace_plan(source_ip: str = "", destination: str = "", observed_at: str = "", indicators: list[str] | None = None):
    indicators = [x.strip() for x in (indicators or []) if x.strip()]
    now = datetime.now(timezone.utc).isoformat()
    return {
        "plan_id": f"TRACE-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "created_at": now,
        "source": source_ip,
        "destination": destination,
        "observed_at": observed_at,
        "indicators": indicators,
        "steps": [
            "Preserve original logs/PCAP/endpoint/cloud evidence and hash the evidence copies.",
            "Correlate source IP, port, protocol, timestamp, NAT/VPN/proxy/Tor indicators and DNS context.",
            "Enrich IP/domain/certificate/ASN/hosting indicators against approved threat-intelligence sources.",
            "Build a timeline covering initial access, persistence, privilege escalation, lateral movement and data access when evidence supports it.",
            "Map observed behavior to MITRE ATT&CK/ATLAS techniques without treating a mapping as proof of attribution.",
            "Generate containment options: isolate affected host, revoke sessions/tokens, disable compromised credentials, block confirmed indicators and segment affected networks.",
            "Preserve an auditable evidence bundle and record confidence plus alternative hypotheses.",
        ],
        "prohibited": ["hack-back", "unauthorized access", "counter-intrusion", "payload delivery to attacker", "destructive disruption"],
        "outputs": ["evidence_bundle", "timeline", "security_graph_updates", "ioc_enrichment", "containment_plan", "attribution_hypotheses"],
    }
