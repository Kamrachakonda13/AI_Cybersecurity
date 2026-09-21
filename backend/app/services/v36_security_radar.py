"""AegisX v3.6 Security Radar and Tool Scout.

Separates verified catalog entries from emerging/experimental recommendations.
Radar items are advisory metadata; execution remains governed by AegisX workers.
"""
from __future__ import annotations
from datetime import datetime, timezone

RECOMMENDATIONS = [
    {"id":"owasp-acs-2026","name":"OWASP Agent Control Standard","kind":"standard","maturity":"recommended","reason":"Adds inspectable, traceable and instrumentable runtime control hooks for agents.","source":"OWASP GenAI Security Project","maps_to":["agent identity","tool authorization","runtime enforcement","audit"]},
    {"id":"owasp-genai-crosswalk-2026","name":"OWASP GenAI Security Industry Framework Crosswalk","kind":"standard","maturity":"recommended","reason":"Connects GenAI risks and controls to established governance and security frameworks.","source":"OWASP GenAI Security Project","maps_to":["NIST AI RMF","MITRE ATLAS","governance","control evidence"]},
    {"id":"kyverno-2026","name":"Kyverno 1.18+","kind":"tool","maturity":"recommended","reason":"Kubernetes-native policy-as-code with stronger HTTP execution safeguards and modern policy types.","source":"CNCF","maps_to":["Kubernetes governance","admission control","image verification","policy drift"]},
    {"id":"inspektor-gadget-2026","name":"Inspektor Gadget","kind":"tool","maturity":"recommended","reason":"eBPF-based Kubernetes/Linux inspection with a published 2026 security audit and patched findings.","source":"CNCF","maps_to":["runtime visibility","Kubernetes","Linux","DFIR"]},
    {"id":"prempti-2026","name":"Prempti","kind":"tool","maturity":"experimental","reason":"Emerging Falco ecosystem work focused on AI coding-agent tool-call lifecycle visibility and policy.","source":"CNCF/Falco ecosystem","maps_to":["agent runtime","tool calls","policy","host telemetry"]},
    {"id":"mcp-shield-runtime","name":"MCP Shield Runtime","kind":"tool","maturity":"experimental","reason":"Emerging MCP runtime gateway pattern for parameter policies, approval gates, secret redaction, drift detection and tamper-evident audit.","source":"community","maps_to":["MCP","tool contract","approval","egress","audit"]},
    {"id":"pipelock","name":"Pipelock","kind":"tool","maturity":"experimental","reason":"Emerging agent firewall for MCP/A2A/WebSocket egress, SSRF, exfiltration and prompt-injection signals with signed action receipts.","source":"community","maps_to":["egress","MCP","A2A","evidence"]},
    {"id":"adrian","name":"Adrian Agent Security","kind":"tool","maturity":"experimental","reason":"Emerging runtime monitoring/intervention layer for agent actions and tool calls.","source":"community","maps_to":["agent runtime","tool-call policy","intervention"]},
    {"id":"sint-protocol","name":"SINT Protocol","kind":"tool","maturity":"experimental","reason":"Emerging authority/evidence protocol for consequential autonomous actions, with capability tokens and signed receipts.","source":"community","maps_to":["capability tokens","approval","revocation","evidence"]},
    {"id":"openssf-scorecard","name":"OpenSSF Scorecard","kind":"tool","maturity":"recommended","reason":"Adds repository security-health signals to software and AI supply-chain risk decisions.","source":"OpenSSF","maps_to":["supply chain","repository risk","AIBOM/SBOM"]},
    {"id":"tuf","name":"The Update Framework (TUF)","kind":"tool","maturity":"recommended","reason":"Adds resilient update trust and rollback protections to worker/tool distribution.","source":"CNCF / OpenSSF ecosystem","maps_to":["worker supply chain","updates","artifact trust"]},
    {"id":"guac","name":"GUAC","kind":"tool","maturity":"recommended","reason":"Graph-based aggregation of SBOM, attestation and dependency evidence for supply-chain analysis.","source":"OpenSSF","maps_to":["SBOM","provenance","dependency graph","risk correlation"]},
]

def overview():
    return {"release":"3.6","generated_at":datetime.now(timezone.utc).isoformat(),"recommendations":RECOMMENDATIONS,"principle":"Scout continuously; promote only after evidence, provenance, licensing, security review and worker compatibility are verified."}

def recommendations(maturity: str|None=None, kind: str|None=None):
    rows=RECOMMENDATIONS
    if maturity: rows=[x for x in rows if x["maturity"]==maturity]
    if kind: rows=[x for x in rows if x["kind"]==kind]
    return rows
