# VEYRA v2.7 — Complete Security Tool Education Guide

This guide covers the **477 registered security-tool catalog entries** in the current VEYRA registry. The goal is to teach you what each tool does, when to use it, what evidence to expect, and how it fits into VEYRA. It intentionally does **not** provide attack commands, credential-attack recipes, payloads, persistence, C2 or hack-back instructions.

## The VEYRA way to use a tool

1. **Define ownership and scope** — identify the exact assets, domains, accounts or evidence you are authorized to assess.
2. **Select the tool in VEYRA** — use the Tool Academy to understand its purpose and governance tier.
3. **Choose the right execution boundary** — analyst workstation, read-only connector, sensor, approved worker, or isolated worker.
4. **Stage a governed job** — target + scope + purpose + approval ticket.
5. **Review evidence** — results should have provenance and hashes where applicable.
6. **Correlate** — map findings into risk, ATT&CK/ATLAS, Security Graph and incidents.
7. **Remediate and verify** — close the loop with evidence rather than assuming the scan result is enough.

## Permission levels

- **No access** — user cannot use the tool.
- **View** — catalog/help/evidence only.
- **Plan** — can prepare a governed assessment plan.
- **Request execution** — can submit a governed request; it still requires policy/approval and an isolated worker.

## Privileged tools

The following tools are marked **Privileged Admin** in VEYRA: Certipy, Core Impact, Dirsearch, FFUF, Feroxbuster, Gobuster, Hashcat, Hydra, Impacket, John the Ripper, Kerbrute, Masscan, Medusa, Metasploit Framework, Naabu, NetExec, RustScan, SQLMap, Wapiti, kube-hunter. These should be assigned sparingly. The backend also enforces role and governance checks; UI selection is not the only security boundary.

## Complete tool-by-tool guide

### 1. Nmap
- **Category:** Network Discovery
- **Purpose:** Asset/service discovery
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Start with a tightly scoped owned network/domain list. Compare discovered hosts and services against VEYRA inventory, investigate unexpected exposure, and preserve the scan result as evidence.

### 2. Masscan
- **Category:** Network Discovery
- **Purpose:** High-speed exposure inventory
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Start with a tightly scoped owned network/domain list. Compare discovered hosts and services against VEYRA inventory, investigate unexpected exposure, and preserve the scan result as evidence.

### 3. RustScan
- **Category:** Network Discovery
- **Purpose:** Fast port inventory
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Start with a tightly scoped owned network/domain list. Compare discovered hosts and services against VEYRA inventory, investigate unexpected exposure, and preserve the scan result as evidence.

### 4. Naabu
- **Category:** Network Discovery
- **Purpose:** Port discovery
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Start with a tightly scoped owned network/domain list. Compare discovered hosts and services against VEYRA inventory, investigate unexpected exposure, and preserve the scan result as evidence.

### 5. arp-scan
- **Category:** Network Discovery
- **Purpose:** Local network discovery
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `own_network`
- **How to use it in VEYRA:** Start with a tightly scoped owned network/domain list. Compare discovered hosts and services against VEYRA inventory, investigate unexpected exposure, and preserve the scan result as evidence.

### 6. Netdiscover
- **Category:** Network Discovery
- **Purpose:** LAN discovery
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `own_network`
- **How to use it in VEYRA:** Start with a tightly scoped owned network/domain list. Compare discovered hosts and services against VEYRA inventory, investigate unexpected exposure, and preserve the scan result as evidence.

### 7. Amass
- **Category:** Attack Surface
- **Purpose:** Asset/domain discovery
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_scope`
- **How to use it in VEYRA:** Start with a tightly scoped owned network/domain list. Compare discovered hosts and services against VEYRA inventory, investigate unexpected exposure, and preserve the scan result as evidence.

### 8. Subfinder
- **Category:** Attack Surface
- **Purpose:** Passive subdomain discovery
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_scope`
- **How to use it in VEYRA:** Start with a tightly scoped owned network/domain list. Compare discovered hosts and services against VEYRA inventory, investigate unexpected exposure, and preserve the scan result as evidence.

### 9. Assetfinder
- **Category:** Attack Surface
- **Purpose:** Passive asset discovery
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_scope`
- **How to use it in VEYRA:** Start with a tightly scoped owned network/domain list. Compare discovered hosts and services against VEYRA inventory, investigate unexpected exposure, and preserve the scan result as evidence.

### 10. dnsx
- **Category:** Attack Surface
- **Purpose:** DNS validation
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_scope`
- **How to use it in VEYRA:** Start with a tightly scoped owned network/domain list. Compare discovered hosts and services against VEYRA inventory, investigate unexpected exposure, and preserve the scan result as evidence.

### 11. httpx
- **Category:** Attack Surface
- **Purpose:** HTTP service inventory
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_scope`
- **How to use it in VEYRA:** Start with a tightly scoped owned network/domain list. Compare discovered hosts and services against VEYRA inventory, investigate unexpected exposure, and preserve the scan result as evidence.

### 12. Burp Suite
- **Category:** Web/API
- **Purpose:** Web application security assessment
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Point the tool only at an authorized application or lab. Begin with mapping/passive assessment, review findings, de-duplicate alerts, and escalate active checks through approval.

### 13. OWASP ZAP
- **Category:** Web/API
- **Purpose:** Web application security assessment
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Point the tool only at an authorized application or lab. Begin with mapping/passive assessment, review findings, de-duplicate alerts, and escalate active checks through approval.

### 14. Nuclei
- **Category:** Web/API
- **Purpose:** Template-based vulnerability assessment
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Point the tool only at an authorized application or lab. Begin with mapping/passive assessment, review findings, de-duplicate alerts, and escalate active checks through approval.

### 15. Nikto
- **Category:** Web/API
- **Purpose:** Web server posture assessment
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Point the tool only at an authorized application or lab. Begin with mapping/passive assessment, review findings, de-duplicate alerts, and escalate active checks through approval.

### 16. Gobuster
- **Category:** Web/API
- **Purpose:** Content discovery
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Point the tool only at an authorized application or lab. Begin with mapping/passive assessment, review findings, de-duplicate alerts, and escalate active checks through approval.

### 17. Feroxbuster
- **Category:** Web/API
- **Purpose:** Content discovery
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Point the tool only at an authorized application or lab. Begin with mapping/passive assessment, review findings, de-duplicate alerts, and escalate active checks through approval.

### 18. FFUF
- **Category:** Web/API
- **Purpose:** Web content/fuzzing assessment
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Point the tool only at an authorized application or lab. Begin with mapping/passive assessment, review findings, de-duplicate alerts, and escalate active checks through approval.

### 19. Dirsearch
- **Category:** Web/API
- **Purpose:** Content discovery
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Point the tool only at an authorized application or lab. Begin with mapping/passive assessment, review findings, de-duplicate alerts, and escalate active checks through approval.

### 20. Wapiti
- **Category:** Web/API
- **Purpose:** Web vulnerability assessment
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Point the tool only at an authorized application or lab. Begin with mapping/passive assessment, review findings, de-duplicate alerts, and escalate active checks through approval.

### 21. WhatWeb
- **Category:** Web/API
- **Purpose:** Technology fingerprinting
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_scope`
- **How to use it in VEYRA:** Point the tool only at an authorized application or lab. Begin with mapping/passive assessment, review findings, de-duplicate alerts, and escalate active checks through approval.

### 22. SQLMap
- **Category:** Web/API
- **Purpose:** Authorized SQL injection assessment
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Point the tool only at an authorized application or lab. Begin with mapping/passive assessment, review findings, de-duplicate alerts, and escalate active checks through approval.

### 23. Metasploit Framework
- **Category:** Exploit Validation
- **Purpose:** Authorized vulnerability validation
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `isolated_lab_only`
- **How to use it in VEYRA:** Use only in an isolated lab or explicitly approved worker. Treat results as validation evidence, not as permission to attack a real account or system.

### 24. Core Impact
- **Category:** Exploit Validation
- **Purpose:** Authorized penetration testing
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `isolated_lab_only`
- **How to use it in VEYRA:** Use only in an isolated lab or explicitly approved worker. Treat results as validation evidence, not as permission to attack a real account or system.

### 25. Impacket
- **Category:** Identity/Network
- **Purpose:** Authorized protocol/security assessment
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `isolated_lab_only`
- **How to use it in VEYRA:** Define explicit scope, use the designated VEYRA worker/connector, review evidence and document provenance.

### 26. NetExec
- **Category:** Identity/Network
- **Purpose:** Authorized Windows/network assessment
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `isolated_lab_only`
- **How to use it in VEYRA:** Define explicit scope, use the designated VEYRA worker/connector, review evidence and document provenance.

### 27. BloodHound
- **Category:** Identity
- **Purpose:** Identity attack-path analysis
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_scope`
- **How to use it in VEYRA:** Define explicit scope, use the designated VEYRA worker/connector, review evidence and document provenance.

### 28. Certipy
- **Category:** Identity
- **Purpose:** AD CS security assessment
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `isolated_lab_only`
- **How to use it in VEYRA:** Define explicit scope, use the designated VEYRA worker/connector, review evidence and document provenance.

### 29. Kerbrute
- **Category:** Identity
- **Purpose:** Kerberos identity assessment
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `isolated_lab_only`
- **How to use it in VEYRA:** Define explicit scope, use the designated VEYRA worker/connector, review evidence and document provenance.

### 30. Hashcat
- **Category:** Credential Audit
- **Purpose:** Authorized password-strength auditing
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `offline_audit_only`
- **How to use it in VEYRA:** Use only in an isolated lab or explicitly approved worker. Treat results as validation evidence, not as permission to attack a real account or system.

### 31. John the Ripper
- **Category:** Credential Audit
- **Purpose:** Authorized password-strength auditing
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `offline_audit_only`
- **How to use it in VEYRA:** Use only in an isolated lab or explicitly approved worker. Treat results as validation evidence, not as permission to attack a real account or system.

### 32. Hydra
- **Category:** Credential Audit
- **Purpose:** Authorized authentication testing
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `isolated_lab_only`
- **How to use it in VEYRA:** Use only in an isolated lab or explicitly approved worker. Treat results as validation evidence, not as permission to attack a real account or system.

### 33. Medusa
- **Category:** Credential Audit
- **Purpose:** Authorized authentication testing
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `isolated_lab_only`
- **How to use it in VEYRA:** Use only in an isolated lab or explicitly approved worker. Treat results as validation evidence, not as permission to attack a real account or system.

### 34. Wireshark
- **Category:** Network Defense
- **Purpose:** Packet analysis
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `analyst_workstation`
- **How to use it in VEYRA:** Use on networks you own/manage. Inspect traffic, protocol behavior and anomalies; turn confirmed behavior into detections and incident evidence.

### 35. tshark
- **Category:** Network Defense
- **Purpose:** Packet analysis
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `analyst_workstation`
- **How to use it in VEYRA:** Use on networks you own/manage. Inspect traffic, protocol behavior and anomalies; turn confirmed behavior into detections and incident evidence.

### 36. tcpdump
- **Category:** Network Defense
- **Purpose:** Packet capture
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `own_network`
- **How to use it in VEYRA:** Use on networks you own/manage. Inspect traffic, protocol behavior and anomalies; turn confirmed behavior into detections and incident evidence.

### 37. Zeek
- **Category:** Network Defense
- **Purpose:** Network security monitoring
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `sensor`
- **How to use it in VEYRA:** Use on networks you own/manage. Inspect traffic, protocol behavior and anomalies; turn confirmed behavior into detections and incident evidence.

### 38. Suricata
- **Category:** Network Defense
- **Purpose:** IDS/NSM
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `sensor`
- **How to use it in VEYRA:** Use on networks you own/manage. Inspect traffic, protocol behavior and anomalies; turn confirmed behavior into detections and incident evidence.

### 39. Snort
- **Category:** Network Defense
- **Purpose:** IDS/NSM
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `sensor`
- **How to use it in VEYRA:** Use on networks you own/manage. Inspect traffic, protocol behavior and anomalies; turn confirmed behavior into detections and incident evidence.

### 40. OpenVAS/Greenbone
- **Category:** Vulnerability
- **Purpose:** Vulnerability assessment
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 41. Nessus
- **Category:** Vulnerability
- **Purpose:** Vulnerability assessment/import
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 42. Trivy
- **Category:** Cloud/Container
- **Purpose:** Container/Kubernetes/package security
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 43. Grype
- **Category:** Cloud/Container
- **Purpose:** SBOM/image vulnerability scanning
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 44. Syft
- **Category:** Cloud/Container
- **Purpose:** SBOM generation
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 45. Semgrep
- **Category:** AppSec
- **Purpose:** SAST/security rules
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 46. Bandit
- **Category:** AppSec
- **Purpose:** Python security analysis
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 47. CodeQL
- **Category:** AppSec
- **Purpose:** Code security analysis
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 48. Checkov
- **Category:** IaC
- **Purpose:** Infrastructure-as-code security
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 49. Terrascan
- **Category:** IaC
- **Purpose:** Infrastructure-as-code security
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 50. tfsec
- **Category:** IaC
- **Purpose:** Terraform security analysis
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 51. Prowler
- **Category:** Cloud
- **Purpose:** CSPM/security auditing
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `read_only_cloud`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 52. Scout Suite
- **Category:** Cloud
- **Purpose:** Multi-cloud security auditing
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `read_only_cloud`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 53. CloudSploit
- **Category:** Cloud
- **Purpose:** Cloud configuration assessment
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `read_only_cloud`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 54. Kubescape
- **Category:** Kubernetes
- **Purpose:** Kubernetes posture/security
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 55. kube-bench
- **Category:** Kubernetes
- **Purpose:** CIS benchmark checks
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 56. kube-hunter
- **Category:** Kubernetes
- **Purpose:** Kubernetes security assessment
- **VEYRA tier:** PRIVILEGED ADMIN
- **Execution boundary:** `isolated_lab_only`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 57. Falco
- **Category:** Kubernetes
- **Purpose:** Runtime detection
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `sensor`
- **How to use it in VEYRA:** Run against approved assets/builds/configuration, prioritize internet exposure and identity risk, map results to severity/KEV, and track remediation.

### 58. osquery
- **Category:** Endpoint
- **Purpose:** Endpoint telemetry/query
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `endpoint_agent`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 59. Sysmon
- **Category:** Endpoint
- **Purpose:** Windows endpoint telemetry
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `endpoint_agent`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 60. Velociraptor
- **Category:** DFIR
- **Purpose:** Endpoint investigation
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 61. Volatility 3
- **Category:** DFIR
- **Purpose:** Memory forensics
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `isolated_analysis_worker`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 62. Autopsy
- **Category:** DFIR
- **Purpose:** Disk forensics
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `analyst_workstation`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 63. Sleuth Kit
- **Category:** DFIR
- **Purpose:** Filesystem forensics
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `isolated_analysis_worker`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 64. YARA
- **Category:** Malware
- **Purpose:** Static malware classification
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `isolated_analysis_worker`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 65. ClamAV
- **Category:** Malware
- **Purpose:** Malware scanning
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `isolated_analysis_worker`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 66. capa
- **Category:** Malware
- **Purpose:** Capability identification
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `isolated_analysis_worker`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 67. Ghidra
- **Category:** Reverse Engineering
- **Purpose:** Static reverse engineering
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `isolated_analysis_worker`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 68. radare2
- **Category:** Reverse Engineering
- **Purpose:** Static reverse engineering
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `isolated_analysis_worker`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 69. Rizin
- **Category:** Reverse Engineering
- **Purpose:** Static reverse engineering
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `isolated_analysis_worker`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 70. binwalk
- **Category:** Firmware
- **Purpose:** Firmware/file analysis
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `isolated_analysis_worker`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 71. foremost
- **Category:** Forensics
- **Purpose:** File carving
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `isolated_analysis_worker`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 72. ExifTool
- **Category:** Forensics
- **Purpose:** Metadata extraction
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `isolated_analysis_worker`
- **How to use it in VEYRA:** Work from authorized evidence copies in the correct isolated or analyst environment. Preserve hashes and chain-of-custody metadata before analysis.

### 73. MISP
- **Category:** Threat Intelligence
- **Purpose:** IOC exchange
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_connector`
- **How to use it in VEYRA:** Ingest or author normalized intelligence/detections, attach source and confidence, test against internal telemetry, and measure coverage and false positives.

### 74. STIX/TAXII
- **Category:** Threat Intelligence
- **Purpose:** Threat-intel transport
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_connector`
- **How to use it in VEYRA:** Ingest or author normalized intelligence/detections, attach source and confidence, test against internal telemetry, and measure coverage and false positives.

### 75. Sigma
- **Category:** Detection Engineering
- **Purpose:** Portable detection rules
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Ingest or author normalized intelligence/detections, attach source and confidence, test against internal telemetry, and measure coverage and false positives.

### 76. NeuralTrust
- **Category:** AI Security
- **Purpose:** Agent runtime security, posture and AI red teaming integration
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_connector`
- **How to use it in VEYRA:** Assess AI applications/agents in lab or approved environments. Check prompt/context integrity, tool permissions, RAG authorization, memory provenance, model supply chain and runtime policy.

### 77. Lakera Guard / Check Point AI Guardrails
- **Category:** AI Security
- **Purpose:** Prompt injection, jailbreak and data-leakage runtime defense
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_connector`
- **How to use it in VEYRA:** Assess AI applications/agents in lab or approved environments. Check prompt/context integrity, tool permissions, RAG authorization, memory provenance, model supply chain and runtime policy.

### 78. TrojAI
- **Category:** AI Security
- **Purpose:** Model vulnerability and adversarial stress-testing integration
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_connector`
- **How to use it in VEYRA:** Assess AI applications/agents in lab or approved environments. Check prompt/context integrity, tool permissions, RAG authorization, memory provenance, model supply chain and runtime policy.

### 79. CalypsoAI / F5 AI Security
- **Category:** AI Security
- **Purpose:** Inference-layer AI security and guardrails integration
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_connector`
- **How to use it in VEYRA:** Assess AI applications/agents in lab or approved environments. Check prompt/context integrity, tool permissions, RAG authorization, memory provenance, model supply chain and runtime policy.

### 80. Garak
- **Category:** AI Security
- **Purpose:** LLM security evaluation
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Assess AI applications/agents in lab or approved environments. Check prompt/context integrity, tool permissions, RAG authorization, memory provenance, model supply chain and runtime policy.

### 81. Promptfoo
- **Category:** AI Security
- **Purpose:** LLM/agent evaluation
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `lab_or_approved_worker`
- **How to use it in VEYRA:** Assess AI applications/agents in lab or approved environments. Check prompt/context integrity, tool permissions, RAG authorization, memory provenance, model supply chain and runtime policy.

### 82. Adversarial Robustness Toolbox
- **Category:** AI Security
- **Purpose:** ML adversarial robustness testing
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `isolated_ai_worker`
- **How to use it in VEYRA:** Assess AI applications/agents in lab or approved environments. Check prompt/context integrity, tool permissions, RAG authorization, memory provenance, model supply chain and runtime policy.

### 83. NeMo Guardrails
- **Category:** AI Security
- **Purpose:** LLM guardrails/policy enforcement
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_worker`
- **How to use it in VEYRA:** Assess AI applications/agents in lab or approved environments. Check prompt/context integrity, tool permissions, RAG authorization, memory provenance, model supply chain and runtime policy.

### 84. Robust Intelligence
- **Category:** AI Security
- **Purpose:** AI security/validation platform integration
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_connector`
- **How to use it in VEYRA:** Assess AI applications/agents in lab or approved environments. Check prompt/context integrity, tool permissions, RAG authorization, memory provenance, model supply chain and runtime policy.

### 85. HiddenLayer
- **Category:** AI Security
- **Purpose:** AI model security platform integration
- **VEYRA tier:** ADMIN GOVERNED
- **Execution boundary:** `approved_connector`
- **How to use it in VEYRA:** Assess AI applications/agents in lab or approved environments. Check prompt/context integrity, tool permissions, RAG authorization, memory provenance, model supply chain and runtime policy.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
