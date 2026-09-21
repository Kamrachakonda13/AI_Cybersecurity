"""Admin-only ethical hacking / security assessment tool registry.

This registry catalogs tools and their governance requirements. It intentionally
separates cataloging from execution: high-impact tooling is lab/approved-worker
only and is never exposed as arbitrary shell execution through the API.
"""

from app.services.slug import slugify


TOOL_REGISTRY = [
    # Network / discovery
    ("Nmap", "Network Discovery", "Asset/service discovery", "lab_or_approved_worker"),
    ("Masscan", "Network Discovery",
     "High-speed exposure inventory", "lab_or_approved_worker"),
    ("RustScan", "Network Discovery", "Fast port inventory", "lab_or_approved_worker"),
    ("Naabu", "Network Discovery", "Port discovery", "lab_or_approved_worker"),
    ("arp-scan", "Network Discovery", "Local network discovery", "own_network"),
    ("Netdiscover", "Network Discovery", "LAN discovery", "own_network"),
    ("Amass", "Attack Surface", "Asset/domain discovery", "approved_scope"),
    ("Assetfinder", "Attack Surface", "Passive asset discovery", "approved_scope"),
    ("dnsx", "Attack Surface", "DNS validation", "approved_scope"),
    ("httpx", "Attack Surface", "HTTP service inventory", "approved_scope"),
    # Web/API
    ("Burp Suite", "Web/API", "Web application security assessment",
     "lab_or_approved_worker"),
    ("OWASP ZAP", "Web/API", "Web application security assessment",
     "lab_or_approved_worker"),
    ("Nuclei", "Web/API", "Template-based vulnerability assessment",
     "lab_or_approved_worker"),
    ("Nikto", "Web/API", "Web server posture assessment", "lab_or_approved_worker"),
    ("Gobuster", "Web/API", "Content discovery", "lab_or_approved_worker"),
    ("Feroxbuster", "Web/API", "Content discovery", "lab_or_approved_worker"),
    ("FFUF", "Web/API", "Web content/fuzzing assessment", "lab_or_approved_worker"),
    ("Dirsearch", "Web/API", "Content discovery", "lab_or_approved_worker"),
    ("Wapiti", "Web/API", "Web vulnerability assessment", "lab_or_approved_worker"),
    ("WhatWeb", "Web/API", "Technology fingerprinting", "approved_scope"),
    ("SQLMap", "Web/API", "Authorized SQL injection assessment", "lab_or_approved_worker"),
    # Exploit validation / offensive frameworks
    ("Metasploit Framework", "Exploit Validation",
     "Authorized vulnerability validation", "isolated_lab_only"),
    ("Core Impact", "Exploit Validation",
     "Authorized penetration testing", "isolated_lab_only"),
    ("Impacket", "Identity/Network",
     "Authorized protocol/security assessment", "isolated_lab_only"),
    ("NetExec", "Identity/Network",
     "Authorized Windows/network assessment", "isolated_lab_only"),
    ("BloodHound", "Identity", "Identity attack-path analysis", "approved_scope"),
    ("Certipy", "Identity", "AD CS security assessment", "isolated_lab_only"),
    ("Kerbrute", "Identity", "Kerberos identity assessment", "isolated_lab_only"),
    # Credential audit - catalog/import, never browser execution
    ("Hashcat", "Credential Audit",
     "Authorized password-strength auditing", "offline_audit_only"),
    ("John the Ripper", "Credential Audit",
     "Authorized password-strength auditing", "offline_audit_only"),
    ("Hydra", "Credential Audit",
     "Authorized authentication testing", "isolated_lab_only"),
    ("Medusa", "Credential Audit",
     "Authorized authentication testing", "isolated_lab_only"),
    # Network security / packet
    ("Wireshark", "Network Defense", "Packet analysis", "analyst_workstation"),
    ("tshark", "Network Defense", "Packet analysis", "analyst_workstation"),
    ("tcpdump", "Network Defense", "Packet capture", "own_network"),
    ("Zeek", "Network Defense", "Network security monitoring", "sensor"),
    ("Suricata", "Network Defense", "IDS/NSM", "sensor"),
    ("Snort", "Network Defense", "IDS/NSM", "sensor"),
    # Vulnerability / supply chain
    ("OpenVAS/Greenbone", "Vulnerability",
     "Vulnerability assessment", "approved_worker"),
    ("Nessus", "Vulnerability", "Vulnerability assessment/import", "approved_worker"),
    ("Trivy", "Cloud/Container",
     "Container/Kubernetes/package security", "approved_worker"),
    ("Grype", "Cloud/Container", "SBOM/image vulnerability scanning", "approved_worker"),
    ("Syft", "Cloud/Container", "SBOM generation", "approved_worker"),
    ("Semgrep", "AppSec", "SAST/security rules", "approved_worker"),
    ("Bandit", "AppSec", "Python security analysis", "approved_worker"),
    ("CodeQL", "AppSec", "Code security analysis", "approved_worker"),
    ("Checkov", "IaC", "Infrastructure-as-code security", "approved_worker"),
    ("Terrascan", "IaC", "Infrastructure-as-code security", "approved_worker"),
    ("tfsec", "IaC", "Terraform security analysis", "approved_worker"),
    # Cloud/K8s
    ("Prowler", "Cloud", "CSPM/security auditing", "read_only_cloud"),
    ("Scout Suite", "Cloud", "Multi-cloud security auditing", "read_only_cloud"),
    ("CloudSploit", "Cloud", "Cloud configuration assessment", "read_only_cloud"),
    ("Kubescape", "Kubernetes", "Kubernetes posture/security", "approved_worker"),
    ("kube-bench", "Kubernetes", "CIS benchmark checks", "approved_worker"),
    ("kube-hunter", "Kubernetes", "Kubernetes security assessment", "isolated_lab_only"),
    ("Falco", "Kubernetes", "Runtime detection", "sensor"),
    # Endpoint / DFIR / malware
    ("osquery", "Endpoint", "Endpoint telemetry/query", "endpoint_agent"),
    ("Sysmon", "Endpoint", "Windows endpoint telemetry", "endpoint_agent"),
    ("Velociraptor", "DFIR", "Endpoint investigation", "approved_worker"),
    ("Volatility 3", "DFIR", "Memory forensics", "isolated_analysis_worker"),
    ("Autopsy", "DFIR", "Disk forensics", "analyst_workstation"),
    ("Sleuth Kit", "DFIR", "Filesystem forensics", "isolated_analysis_worker"),
    ("YARA", "Malware", "Static malware classification", "isolated_analysis_worker"),
    ("ClamAV", "Malware", "Malware scanning", "isolated_analysis_worker"),
    ("capa", "Malware", "Capability identification", "isolated_analysis_worker"),
    ("Ghidra", "Reverse Engineering",
     "Static reverse engineering", "isolated_analysis_worker"),
    ("radare2", "Reverse Engineering",
     "Static reverse engineering", "isolated_analysis_worker"),
    ("Rizin", "Reverse Engineering",
     "Static reverse engineering", "isolated_analysis_worker"),
    ("binwalk", "Firmware", "Firmware/file analysis", "isolated_analysis_worker"),
    ("foremost", "Forensics", "File carving", "isolated_analysis_worker"),
    ("ExifTool", "Forensics", "Metadata extraction", "isolated_analysis_worker"),
    # Threat intel / detection
    ("MISP", "Threat Intelligence", "IOC exchange", "approved_connector"),
    ("STIX/TAXII", "Threat Intelligence",
     "Threat-intel transport", "approved_connector"),
    ("Sigma", "Detection Engineering", "Portable detection rules", "approved_worker"),
    # AI security
    ("NeuralTrust", "AI Security",
     "Agent runtime security, posture and AI red teaming integration", "approved_connector"),
    ("Lakera Guard / Check Point AI Guardrails", "AI Security",
     "Prompt injection, jailbreak and data-leakage runtime defense", "approved_connector"),
    ("TrojAI", "AI Security",
     "Model vulnerability and adversarial stress-testing integration", "approved_connector"),
    ("CalypsoAI / F5 AI Security", "AI Security",
     "Inference-layer AI security and guardrails integration", "approved_connector"),
    ("Garak", "AI Security", "LLM security evaluation", "lab_or_approved_worker"),
    ("Promptfoo", "AI Security", "LLM/agent evaluation", "lab_or_approved_worker"),
    ("Adversarial Robustness Toolbox", "AI Security",
     "ML adversarial robustness testing", "isolated_ai_worker"),
    ("NeMo Guardrails", "AI Security",
     "LLM guardrails/policy enforcement", "approved_worker"),
    ("Robust Intelligence", "AI Security",
     "AI security/validation platform integration", "approved_connector"),
    ("HiddenLayer", "AI Security",
     "AI model security platform integration", "approved_connector"),
]


PRIVILEGED_ADMIN_TOOLS = {
    "Metasploit Framework", "Core Impact", "Impacket", "NetExec", "Certipy",
    "Kerbrute", "Hashcat", "John the Ripper", "Hydra", "Medusa",
    "SQLMap", "Masscan", "RustScan", "Naabu", "FFUF", "Gobuster",
    "Feroxbuster", "Dirsearch", "Wapiti", "kube-hunter"
}


def registry():
    return [
        {"id": slugify(name),
         "name": name, "category": category, "purpose": purpose,
         "execution_profile": profile, "admin_only": True,
         "access_tier": "privileged_admin" if name in PRIVILEGED_ADMIN_TOOLS else "admin",
         "privileged_usage": name in PRIVILEGED_ADMIN_TOOLS,
         "browser_shell": False,
         "status": "cataloged"}
        for name, category, purpose, profile in TOOL_REGISTRY
    ]
