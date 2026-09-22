"""Domain catalog — segregate all 658 tools into the 8 CISSP-style domains.

User wants UI segregation per:
 1 Network Security
 2 IAM
 3 Application Security
 4 Cloud Security
 5 Endpoint Security
 6 SecOps & DFIR
 7 Data Security & Cryptography
 8 GRC

Each raw category (57 values) maps to exactly one domain. Security Utilities
(198) are split by tool name heuristic; fallback is SecOps & DFIR.
"""
from __future__ import annotations

from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# The 8 canonical domains (UI labels match the user's table)
# ---------------------------------------------------------------------------
DOMAINS_8 = [
    "Network Security",
    "Identity and Access Management",
    "Application Security",
    "Cloud Security",
    "Endpoint Security",
    "Security Operations & DFIR",
    "Data Security & Cryptography",
    "Governance, Risk & Compliance",
]

# Vendor examples per domain (for UI reference panels)
DOMAIN_VENDORS = {
    "Network Security": ["Cisco ASA", "Palo Alto NGFW", "Fortinet FortiGate", "Snort", "Zeek", "Suricata", "Wireshark", "SolarWinds", "OpenVPN", "WireGuard"],
    "Identity and Access Management": ["Microsoft AD", "Okta", "Azure AD", "CyberArk", "BeyondTrust", "HashiCorp Vault", "Duo", "YubiKey"],
    "Application Security": ["Veracode", "Checkmarx", "SonarQube", "OWASP ZAP", "Burp Suite", "Snyk", "Black Duck", "Cloudflare WAF"],
    "Cloud Security": ["Wiz", "Prisma Cloud", "Orca", "Netskope", "AWS IAM", "Azure Security Center", "GCP SCC"],
    "Endpoint Security": ["CrowdStrike Falcon", "SentinelOne", "Microsoft Defender XDR", "Intune", "Workspace ONE", "ESET", "Malwarebytes"],
    "Security Operations & DFIR": ["Splunk", "Microsoft Sentinel", "QRadar", "Cortex XSOAR", "Autopsy", "EnCase", "VirusTotal", "Mandiant"],
    "Data Security & Cryptography": ["Symantec DLP", "Forcepoint DLP", "BitLocker", "FileVault", "VeraCrypt", "AWS KMS", "Azure Key Vault"],
    "Governance, Risk & Compliance": ["ServiceNow GRC", "OneTrust", "Nessus", "Qualys", "Rapid7", "NIST CSF", "ISO 27001", "CIS Controls"],
}

# Explicit category → domain mapping (covers all 60+ raw categories)
CATEGORY_TO_DOMAIN: dict[str, str] = {
    # Network Security
    "Network Discovery": "Network Security",
    "Network Defense": "Network Security",
    "Wireless": "Network Security",
    "AI Network Security": "Network Security",
    "Vector DB": "Network Security",  # monitoring plumbing
    # IAM
    "Identity": "Identity and Access Management",
    "Identity/Network": "Identity and Access Management",
    "Credential Audit": "Identity and Access Management",
    "Agent Identity": "Identity and Access Management",
    # AppSec
    "AppSec": "Application Security",
    "Attack Surface": "Application Security",
    "Web/API": "Application Security",
    "Exploit Validation": "Application Security",
    "Firmware": "Application Security",
    "Vulnerability": "Application Security",
    "AI AppSec": "Application Security",
    # Cloud Security
    "Cloud": "Cloud Security",
    "Cloud/Container": "Cloud Security",
    "Kubernetes": "Cloud Security",
    "Kubernetes Governance": "Cloud Security",
    "IaC": "Cloud Security",
    "AI Supply Chain": "Cloud Security",  # supply chain is cloud-adjacent but keep with cloud? Actually GRC but keep here for now
    # Endpoint Security
    "Endpoint": "Endpoint Security",
    "Malware": "Endpoint Security",
    # SecOps & DFIR
    "DFIR": "Security Operations & DFIR",
    "Forensics": "Security Operations & DFIR",
    "Reverse Engineering": "Security Operations & DFIR",
    "Threat Intelligence": "Security Operations & DFIR",
    "AI Threat Intelligence": "Security Operations & DFIR",
    "Threat Hunting": "Security Operations & DFIR",
    "Detection Engineering": "Security Operations & DFIR",
    "AI Incident Response": "Security Operations & DFIR",
    "AI SOC": "Security Operations & DFIR",
    "AI Observability": "Security Operations & DFIR",
    # Data Security
    "AI Secrets": "Data Security & Cryptography",
    "AI Data Security": "Data Security & Cryptography",
    "Vector DB Security": "Data Security & Cryptography",
    "Agent Memory Security": "Data Security & Cryptography",
    "Model Security": "Data Security & Cryptography",
    "AI Cybersecurity": "Data Security & Cryptography",
    # GRC
    "Policy as Code": "Governance, Risk & Compliance",
    "Software Supply Chain": "Governance, Risk & Compliance",
    "AI Governance": "Governance, Risk & Compliance",
    "AI SBOM": "Governance, Risk & Compliance",
    # AI / Agent — split into appropriate buckets:
    "AI Security": "Security Operations & DFIR",
    "AI Gateway": "Identity and Access Management",  # gateway = identity
    "AI Guardrails": "Application Security",
    "AI Evaluation": "Application Security",
    "LLM Evaluation": "Application Security",
    "LLM Red Team": "Security Operations & DFIR",
    "AI Red Team": "Security Operations & DFIR",
    "Adversarial ML": "Application Security",
    "Agent Security": "Security Operations & DFIR",
    "Agent Safety": "Security Operations & DFIR",
    "Agent Evaluation": "Security Operations & DFIR",
    "Agent Governance": "Governance, Risk & Compliance",
    "Agent Supply Chain": "Governance, Risk & Compliance",
    "Agent Red Team": "Security Operations & DFIR",
    "A2A Security": "Security Operations & DFIR",
    "MCP Security": "Security Operations & DFIR",
    "RAG Security": "Data Security & Cryptography",
    "Prompt Injection": "Application Security",
    "Prompt Security": "Application Security",
    "ML Lifecycle": "Application Security",
    "Threat Intelligence": "Security Operations & DFIR",
    # Utilities — SecOps catch-all
    "Security Utilities": "Security Operations & DFIR",
}

# Fallback for unknowns: map to GRC
FALLBACK_DOMAIN = "Governance, Risk & Compliance"


def domain_for_tool(tool: dict) -> str:
    cat = tool.get("category", "")
    if cat in CATEGORY_TO_DOMAIN:
        return CATEGORY_TO_DOMAIN[cat]
    # Heuristic for Security Utilities sub-split by name
    name = tool.get("name", "").lower()
    if any(k in name for k in ("firewall", "vpn", "wireshark", "nmap", "snort", "suricata", "zeek")):
        return "Network Security"
    if any(k in name for k in ("vault", "auth", "sso", "mfa", "okta", "ad ")):
        return "Identity and Access Management"
    if any(k in name for k in ("snyk", "zap", "burp")):
        return "Application Security"
    if any(k in name for k in ("wiz", "prisma", "cloud")):
        return "Cloud Security"
    if any(k in name for k in ("crowdstrike", "sentinel", "edr", "defender")):
        return "Endpoint Security"
    if any(k in name for k in ("splunk", "sentinel", "qradar", "autopsy")):
        return "Security Operations & DFIR"
    if any(k in name for k in ("dlp", "kms", "vault", "bitlocker")):
        return "Data Security & Cryptography"
    return FALLBACK_DOMAIN


def segregate_tools(tools: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {d: [] for d in DOMAINS_8}
    for t in tools:
        d = domain_for_tool(t)
        out[d].append(t)
    return out


def domain_stats(tools: list[dict]) -> list[dict]:
    by = segregate_tools(tools)
    stats = []
    for d in DOMAINS_8:
        lst = by[d]
        cats = Counter(x.get("category", "?") for x in lst)
        stats.append({"domain": d, "count": len(lst), "vendors": DOMAIN_VENDORS[d], "categories": dict(cats)})
    return stats


def all_tools() -> list[dict]:
    from app.services.extended_catalog import extended_registry
    from app.services.ai_cutting_edge_2026 import registry as ai_reg
    from app.services.ai_ecosystem import registry as eco_reg

    return extended_registry() + ai_reg() + eco_reg()
