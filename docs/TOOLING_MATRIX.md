# VEYRA Security Tooling Matrix

VEYRA should recognize a broad security-tool ecosystem without turning the
browser into an unrestricted attack terminal. Tools are connectors, not
permissions. Every connector needs target scope, authorization, isolation,
approval level, rate limits, credentials, evidence schema and audit events.

## 1. Network / asset discovery

| Tool | Role in VEYRA | Default |
|---|---|---|
| Nmap | Service/port inventory | Lab / approved |
| Masscan | Large-scale exposure inventory | Lab / approved |
| RustScan | Fast port discovery | Lab / approved |
| arp-scan | Local/LAN discovery | Own network |
| Netdiscover | LAN discovery | Own network |
| Amass | Asset/domain discovery | Approved scope |
| Subfinder | Passive subdomain inventory | Approved scope |
| Assetfinder | Passive asset inventory | Approved scope |
| DNSx | DNS resolution/validation | Approved scope |
| Naabu | Port inventory | Lab / approved |

## 2. Web / API security

Nuclei, OWASP ZAP, Burp Suite, Nikto, Gobuster, Feroxbuster, FFUF,
Dirsearch, Wapiti, WhatWeb, httpx and API-schema/security tooling belong here.

VEYRA should import findings and orchestrate **approved** assessments. Intrusive
payload execution must stay inside the isolated assessment worker.

## 3. Vulnerability / application / code security

Nuclei, OpenVAS/Greenbone, Nessus-compatible result imports, Semgrep, Bandit,
CodeQL-compatible SARIF imports, Trivy, Grype, Syft, Checkov, Terrascan,
tfsec-compatible results and dependency scanners.

Normalize results into one Finding schema with source, scanner version,
timestamp, asset, evidence, CVE/CWE, severity and remediation.

## 4. Identity / directory security

BloodHound, BloodHound-compatible graph imports, NetExec, Impacket,
Certipy, Kerbrute and directory-audit tooling should be treated as **authorized
assessment connectors**.

VEYRA should focus on identity relationships, privilege paths, MFA gaps,
delegation/configuration risk and evidence rather than exposing credential
attack workflows.

## 5. Credential / authentication security

Hashcat, John the Ripper, Hydra, Medusa and related tools can be catalogued for
authorized password-audit work, but the VEYRA browser should not expose
credential spraying/cracking against arbitrary targets.

Prefer imports of approved audit results plus controls for password policy,
MFA, breached-secret detection and privileged-session review.

## 6. Network detection / packet analysis

Wireshark, tshark, tcpdump, Zeek, Suricata and Snort.

VEYRA should ingest normalized alerts, PCAP-derived metadata, DNS, TLS and flow
records. Full packet capture should be performed by dedicated sensors, not the
web UI.

## 7. Endpoint / DFIR

Sysmon, osquery, Velociraptor, Wazuh-compatible events, Microsoft Defender/
EDR-compatible exports, Volatility, Volatility 3, Autopsy, Sleuth Kit,
KAPE-compatible evidence, Hayabusa, Chainsaw, YARA, ClamAV, capa, binwalk,
foremost and exiftool.

Use an isolated evidence worker for parsing/detonation-adjacent analysis.
Never execute an untrusted sample in the API process.

## 8. Reverse engineering / malware analysis

Ghidra, radare2, Rizin, objdump, strings, capa and IDA-compatible analysis
results should feed a **Malware/Reverse Engineering Workbench**.

Important design: store hashes, sample provenance, static findings, imported
function/symbol evidence, ATT&CK mappings and analyst notes. Keep dynamic
detonation in a separately isolated sandbox.

## 9. Cloud / Kubernetes / container

Prowler, Scout Suite, CloudSploit, Trivy, Grype, Checkov, Kubescape,
kube-bench, kube-hunter, Falco and cloud-provider security findings.

Use read-only cloud identities by default. Separate inventory permissions
from remediation permissions.

## 10. AI / LLM / agent security

Garak, Promptfoo, model-evaluation frameworks, OWASP GenAI test suites,
custom prompt-injection regression tests and agent/tool policy tests.

VEYRA should test:

- prompt injection / indirect prompt injection
- sensitive-information disclosure
- model and data poisoning
- system-prompt leakage
- excessive agency
- improper output handling
- vector/embedding weaknesses
- unbounded consumption
- tool misuse
- memory/context poisoning
- insecure inter-agent communication
- agent supply-chain risk
- unexpected code execution
- human-agent trust failures

## 11. Security operations / detection engineering

Sigma, YARA, Suricata rules, Zeek detections, OpenSearch/Elastic/Splunk/
Sentinel-compatible event ingestion, STIX/TAXII threat-intelligence feeds,
MISP-compatible IOC exchange and case-management integrations.

## 12. Defensive response

SOAR connectors should include ticketing, notification, IAM, firewall/WAF,
EDR and cloud-control integrations. Every high-impact action must pass through
the same approval/audit boundary.

## Tool connector contract

Every tool adapter should declare:

```text
name
version
category
purpose
target_types
read_write_level
required_authorization
isolation_profile
approval_level
rate_limit
credential_requirements
input_schema
output_schema
evidence_schema
rollback_strategy
audit_events
```

### Principle

**VEYRA should be the security team's control plane, not a web-based Kali
terminal.** That lets the platform recognize almost any relevant tool while
keeping dangerous execution constrained to authorized environments.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
