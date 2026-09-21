# VEYRA v2.7 — Per-Tool Help Catalog

This file is the **human-readable companion to the 477-entry Tool Marketplace**. Every registered tool has a help object in the API and UI. The guidance is intentionally safe and educational: it explains what the tool is for, where it belongs in VEYRA, what evidence to expect, and how to use it within an authorized workflow. It does not provide attack recipes, credential-attack instructions, payloads, persistence, C2 or evasion instructions.

**Catalog entries:** 477

## Universal tool workflow

1. Confirm ownership/authorization and exact scope.
2. Check the tool access tier and worker requirement.
3. Read the tool help card before selecting a run profile.
4. Use a named, governed profile rather than arbitrary shell flags.
5. Review the generated contract and approval state.
6. Run on the appropriate managed worker.
7. Validate output and preserve provenance/evidence.
8. Correlate findings with Risk, Security Graph, ATT&CK/ATLAS, SOC and remediation.

## Tool cards

### 1. Nmap

- **ID:** `nmap`
- **Category:** Network Discovery
- **Purpose:** Asset/service discovery
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 2. Masscan

- **ID:** `masscan`
- **Category:** Network Discovery
- **Purpose:** High-speed exposure inventory
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 3. RustScan

- **ID:** `rustscan`
- **Category:** Network Discovery
- **Purpose:** Fast port inventory
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 4. Naabu

- **ID:** `naabu`
- **Category:** Network Discovery
- **Purpose:** Port discovery
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 5. arp-scan

- **ID:** `arp-scan`
- **Category:** Network Discovery
- **Purpose:** Local network discovery
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `own_network`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 6. Netdiscover

- **ID:** `netdiscover`
- **Category:** Network Discovery
- **Purpose:** LAN discovery
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `own_network`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 7. Amass

- **ID:** `amass`
- **Category:** Attack Surface
- **Purpose:** Asset/domain discovery
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_scope`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 8. Subfinder

- **ID:** `subfinder`
- **Category:** Attack Surface
- **Purpose:** Passive subdomain discovery
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_scope`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 9. Assetfinder

- **ID:** `assetfinder`
- **Category:** Attack Surface
- **Purpose:** Passive asset discovery
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_scope`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 10. dnsx

- **ID:** `dnsx`
- **Category:** Attack Surface
- **Purpose:** DNS validation
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_scope`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 11. httpx

- **ID:** `httpx`
- **Category:** Attack Surface
- **Purpose:** HTTP service inventory
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_scope`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 12. Burp Suite

- **ID:** `burp-suite`
- **Category:** Web/API
- **Purpose:** Web application security assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 13. OWASP ZAP

- **ID:** `owasp-zap`
- **Category:** Web/API
- **Purpose:** Web application security assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 14. Nuclei

- **ID:** `nuclei`
- **Category:** Web/API
- **Purpose:** Template-based vulnerability assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 15. Nikto

- **ID:** `nikto`
- **Category:** Web/API
- **Purpose:** Web server posture assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 16. Gobuster

- **ID:** `gobuster`
- **Category:** Web/API
- **Purpose:** Content discovery
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 17. Feroxbuster

- **ID:** `feroxbuster`
- **Category:** Web/API
- **Purpose:** Content discovery
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 18. FFUF

- **ID:** `ffuf`
- **Category:** Web/API
- **Purpose:** Web content/fuzzing assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 19. Dirsearch

- **ID:** `dirsearch`
- **Category:** Web/API
- **Purpose:** Content discovery
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 20. Wapiti

- **ID:** `wapiti`
- **Category:** Web/API
- **Purpose:** Web vulnerability assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 21. WhatWeb

- **ID:** `whatweb`
- **Category:** Web/API
- **Purpose:** Technology fingerprinting
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_scope`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 22. SQLMap

- **ID:** `sqlmap`
- **Category:** Web/API
- **Purpose:** Authorized SQL injection assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 23. Metasploit Framework

- **ID:** `metasploit-framework`
- **Category:** Exploit Validation
- **Purpose:** Authorized vulnerability validation
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_lab_only`
- **Safe workflow:** Use an isolated lab or explicitly approved validation worker. Confirm the suspected weakness and preserve evidence; do not use an unrestricted shell.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 24. Core Impact

- **ID:** `core-impact`
- **Category:** Exploit Validation
- **Purpose:** Authorized penetration testing
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_lab_only`
- **Safe workflow:** Use an isolated lab or explicitly approved validation worker. Confirm the suspected weakness and preserve evidence; do not use an unrestricted shell.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 25. Impacket

- **ID:** `impacket`
- **Category:** Identity/Network
- **Purpose:** Authorized protocol/security assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_lab_only`
- **Safe workflow:** Use authorized identity/network telemetry to understand trust relationships and suspicious activity while preserving evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 26. NetExec

- **ID:** `netexec`
- **Category:** Identity/Network
- **Purpose:** Authorized Windows/network assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_lab_only`
- **Safe workflow:** Use authorized identity/network telemetry to understand trust relationships and suspicious activity while preserving evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 27. BloodHound

- **ID:** `bloodhound`
- **Category:** Identity
- **Purpose:** Identity attack-path analysis
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_scope`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 28. Certipy

- **ID:** `certipy`
- **Category:** Identity
- **Purpose:** AD CS security assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_lab_only`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 29. Kerbrute

- **ID:** `kerbrute`
- **Category:** Identity
- **Purpose:** Kerberos identity assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_lab_only`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 30. Hashcat

- **ID:** `hashcat`
- **Category:** Credential Audit
- **Purpose:** Authorized password-strength auditing
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `offline_audit_only`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 31. John the Ripper

- **ID:** `john-the-ripper`
- **Category:** Credential Audit
- **Purpose:** Authorized password-strength auditing
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `offline_audit_only`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 32. Hydra

- **ID:** `hydra`
- **Category:** Credential Audit
- **Purpose:** Authorized authentication testing
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_lab_only`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 33. Medusa

- **ID:** `medusa`
- **Category:** Credential Audit
- **Purpose:** Authorized authentication testing
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_lab_only`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 34. Wireshark

- **ID:** `wireshark`
- **Category:** Network Defense
- **Purpose:** Packet analysis
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `analyst_workstation`
- **Safe workflow:** Inspect telemetry from networks you manage, identify anomalous protocols/flows, and turn validated observations into detections.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 35. tshark

- **ID:** `tshark`
- **Category:** Network Defense
- **Purpose:** Packet analysis
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `analyst_workstation`
- **Safe workflow:** Inspect telemetry from networks you manage, identify anomalous protocols/flows, and turn validated observations into detections.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 36. tcpdump

- **ID:** `tcpdump`
- **Category:** Network Defense
- **Purpose:** Packet capture
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `own_network`
- **Safe workflow:** Inspect telemetry from networks you manage, identify anomalous protocols/flows, and turn validated observations into detections.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 37. Zeek

- **ID:** `zeek`
- **Category:** Network Defense
- **Purpose:** Network security monitoring
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `sensor`
- **Safe workflow:** Inspect telemetry from networks you manage, identify anomalous protocols/flows, and turn validated observations into detections.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 38. Suricata

- **ID:** `suricata`
- **Category:** Network Defense
- **Purpose:** IDS/NSM
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `sensor`
- **Safe workflow:** Inspect telemetry from networks you manage, identify anomalous protocols/flows, and turn validated observations into detections.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 39. Snort

- **ID:** `snort`
- **Category:** Network Defense
- **Purpose:** IDS/NSM
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `sensor`
- **Safe workflow:** Inspect telemetry from networks you manage, identify anomalous protocols/flows, and turn validated observations into detections.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 40. OpenVAS/Greenbone

- **ID:** `openvas-greenbone`
- **Category:** Vulnerability
- **Purpose:** Vulnerability assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess approved hosts, packages, images or applications; de-duplicate findings, map severity/KEV, and track remediation evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 41. Nessus

- **ID:** `nessus`
- **Category:** Vulnerability
- **Purpose:** Vulnerability assessment/import
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess approved hosts, packages, images or applications; de-duplicate findings, map severity/KEV, and track remediation evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 42. Trivy

- **ID:** `trivy`
- **Category:** Cloud/Container
- **Purpose:** Container/Kubernetes/package security
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess images and workloads before deployment, correlate vulnerabilities with runtime exposure, and verify fixes in CI or an approved worker.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 43. Grype

- **ID:** `grype`
- **Category:** Cloud/Container
- **Purpose:** SBOM/image vulnerability scanning
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess images and workloads before deployment, correlate vulnerabilities with runtime exposure, and verify fixes in CI or an approved worker.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 44. Syft

- **ID:** `syft`
- **Category:** Cloud/Container
- **Purpose:** SBOM generation
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess images and workloads before deployment, correlate vulnerabilities with runtime exposure, and verify fixes in CI or an approved worker.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 45. Semgrep

- **ID:** `semgrep`
- **Category:** AppSec
- **Purpose:** SAST/security rules
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 46. Bandit

- **ID:** `bandit`
- **Category:** AppSec
- **Purpose:** Python security analysis
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 47. CodeQL

- **ID:** `codeql`
- **Category:** AppSec
- **Purpose:** Code security analysis
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 48. Checkov

- **ID:** `checkov`
- **Category:** IaC
- **Purpose:** Infrastructure-as-code security
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Scan approved infrastructure definitions before deployment; prioritize identity, public exposure, secrets and encryption controls.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 49. Terrascan

- **ID:** `terrascan`
- **Category:** IaC
- **Purpose:** Infrastructure-as-code security
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Scan approved infrastructure definitions before deployment; prioritize identity, public exposure, secrets and encryption controls.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 50. tfsec

- **ID:** `tfsec`
- **Category:** IaC
- **Purpose:** Terraform security analysis
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Scan approved infrastructure definitions before deployment; prioritize identity, public exposure, secrets and encryption controls.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 51. Prowler

- **ID:** `prowler`
- **Category:** Cloud
- **Purpose:** CSPM/security auditing
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `read_only_cloud`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 52. Scout Suite

- **ID:** `scout-suite`
- **Category:** Cloud
- **Purpose:** Multi-cloud security auditing
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `read_only_cloud`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 53. CloudSploit

- **ID:** `cloudsploit`
- **Category:** Cloud
- **Purpose:** Cloud configuration assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `read_only_cloud`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 54. Kubescape

- **ID:** `kubescape`
- **Category:** Kubernetes
- **Purpose:** Kubernetes posture/security
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 55. kube-bench

- **ID:** `kube-bench`
- **Category:** Kubernetes
- **Purpose:** CIS benchmark checks
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 56. kube-hunter

- **ID:** `kube-hunter`
- **Category:** Kubernetes
- **Purpose:** Kubernetes security assessment
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_lab_only`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 57. Falco

- **ID:** `falco`
- **Category:** Kubernetes
- **Purpose:** Runtime detection
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `sensor`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 58. osquery

- **ID:** `osquery`
- **Category:** Endpoint
- **Purpose:** Endpoint telemetry/query
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `endpoint_agent`
- **Safe workflow:** Use the managed collector/agent on consented endpoints, collect telemetry, investigate anomalies, and avoid arbitrary remote execution.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 59. Sysmon

- **ID:** `sysmon`
- **Category:** Endpoint
- **Purpose:** Windows endpoint telemetry
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `endpoint_agent`
- **Safe workflow:** Use the managed collector/agent on consented endpoints, collect telemetry, investigate anomalies, and avoid arbitrary remote execution.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 60. Velociraptor

- **ID:** `velociraptor`
- **Category:** DFIR
- **Purpose:** Endpoint investigation
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Acquire authorized artifacts, hash originals, analyze copies, preserve chain of custody, and record conclusions with confidence.
- **Expected evidence:** artifact hash, metadata, timeline, chain-of-custody reference
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 61. Volatility 3

- **ID:** `volatility-3`
- **Category:** DFIR
- **Purpose:** Memory forensics
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_analysis_worker`
- **Safe workflow:** Acquire authorized artifacts, hash originals, analyze copies, preserve chain of custody, and record conclusions with confidence.
- **Expected evidence:** artifact hash, metadata, timeline, chain-of-custody reference
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 62. Autopsy

- **ID:** `autopsy`
- **Category:** DFIR
- **Purpose:** Disk forensics
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `analyst_workstation`
- **Safe workflow:** Acquire authorized artifacts, hash originals, analyze copies, preserve chain of custody, and record conclusions with confidence.
- **Expected evidence:** artifact hash, metadata, timeline, chain-of-custody reference
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 63. Sleuth Kit

- **ID:** `sleuth-kit`
- **Category:** DFIR
- **Purpose:** Filesystem forensics
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_analysis_worker`
- **Safe workflow:** Acquire authorized artifacts, hash originals, analyze copies, preserve chain of custody, and record conclusions with confidence.
- **Expected evidence:** artifact hash, metadata, timeline, chain-of-custody reference
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 64. YARA

- **ID:** `yara`
- **Category:** Malware
- **Purpose:** Static malware classification
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_analysis_worker`
- **Safe workflow:** Analyze samples in isolated analysis workers, begin with static indicators/capabilities, and preserve hashes and evidence.
- **Expected evidence:** file hash, static indicators, capabilities, analysis notes
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 65. ClamAV

- **ID:** `clamav`
- **Category:** Malware
- **Purpose:** Malware scanning
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_analysis_worker`
- **Safe workflow:** Analyze samples in isolated analysis workers, begin with static indicators/capabilities, and preserve hashes and evidence.
- **Expected evidence:** file hash, static indicators, capabilities, analysis notes
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 66. capa

- **ID:** `capa`
- **Category:** Malware
- **Purpose:** Capability identification
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_analysis_worker`
- **Safe workflow:** Analyze samples in isolated analysis workers, begin with static indicators/capabilities, and preserve hashes and evidence.
- **Expected evidence:** file hash, static indicators, capabilities, analysis notes
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 67. Ghidra

- **ID:** `ghidra`
- **Category:** Reverse Engineering
- **Purpose:** Static reverse engineering
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_analysis_worker`
- **Safe workflow:** Open a copy in an isolated workspace, inspect metadata/imports/strings/control flow, map behavior to detections, and preserve hashes.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 68. radare2

- **ID:** `radare2`
- **Category:** Reverse Engineering
- **Purpose:** Static reverse engineering
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_analysis_worker`
- **Safe workflow:** Open a copy in an isolated workspace, inspect metadata/imports/strings/control flow, map behavior to detections, and preserve hashes.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 69. Rizin

- **ID:** `rizin`
- **Category:** Reverse Engineering
- **Purpose:** Static reverse engineering
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_analysis_worker`
- **Safe workflow:** Open a copy in an isolated workspace, inspect metadata/imports/strings/control flow, map behavior to detections, and preserve hashes.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 70. binwalk

- **ID:** `binwalk`
- **Category:** Firmware
- **Purpose:** Firmware/file analysis
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_analysis_worker`
- **Safe workflow:** Analyze authorized firmware images offline, inventory components/configuration, identify exposed services, and document remediation.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 71. foremost

- **ID:** `foremost`
- **Category:** Forensics
- **Purpose:** File carving
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_analysis_worker`
- **Safe workflow:** Extract metadata and recover relevant artifacts from authorized evidence copies without modifying the original evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 72. ExifTool

- **ID:** `exiftool`
- **Category:** Forensics
- **Purpose:** Metadata extraction
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_analysis_worker`
- **Safe workflow:** Extract metadata and recover relevant artifacts from authorized evidence copies without modifying the original evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 73. MISP

- **ID:** `misp`
- **Category:** Threat Intelligence
- **Purpose:** IOC exchange
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_connector`
- **Safe workflow:** Normalize indicators with source and confidence, correlate against internal telemetry, and keep attribution hypotheses separate from confirmed facts.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 74. STIX/TAXII

- **ID:** `stix-taxii`
- **Category:** Threat Intelligence
- **Purpose:** Threat-intel transport
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_connector`
- **Safe workflow:** Normalize indicators with source and confidence, correlate against internal telemetry, and keep attribution hypotheses separate from confirmed facts.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 75. Sigma

- **ID:** `sigma`
- **Category:** Detection Engineering
- **Purpose:** Portable detection rules
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Create portable detections, test against known telemetry, measure false positives and coverage, and version-control the rule.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 76. NeuralTrust

- **ID:** `neuraltrust`
- **Category:** AI Security
- **Purpose:** Agent runtime security, posture and AI red teaming integration
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_connector`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 77. Lakera Guard / Check Point AI Guardrails

- **ID:** `lakera-guard---check-point-ai-guardrails`
- **Category:** AI Security
- **Purpose:** Prompt injection, jailbreak and data-leakage runtime defense
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_connector`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 78. TrojAI

- **ID:** `trojai`
- **Category:** AI Security
- **Purpose:** Model vulnerability and adversarial stress-testing integration
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_connector`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 79. CalypsoAI / F5 AI Security

- **ID:** `calypsoai---f5-ai-security`
- **Category:** AI Security
- **Purpose:** Inference-layer AI security and guardrails integration
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_connector`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 80. Garak

- **ID:** `garak`
- **Category:** AI Security
- **Purpose:** LLM security evaluation
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 81. Promptfoo

- **ID:** `promptfoo`
- **Category:** AI Security
- **Purpose:** LLM/agent evaluation
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `lab_or_approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 82. Adversarial Robustness Toolbox

- **ID:** `adversarial-robustness-toolbox`
- **Category:** AI Security
- **Purpose:** ML adversarial robustness testing
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 83. NeMo Guardrails

- **ID:** `nemo-guardrails`
- **Category:** AI Security
- **Purpose:** LLM guardrails/policy enforcement
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 84. Robust Intelligence

- **ID:** `robust-intelligence`
- **Category:** AI Security
- **Purpose:** AI security/validation platform integration
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_connector`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 85. HiddenLayer

- **ID:** `hiddenlayer`
- **Category:** AI Security
- **Purpose:** AI model security platform integration
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_connector`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 86. adaptixc2

- **ID:** `adaptixc2`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: adaptixc2
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 87. airgeddon

- **ID:** `airgeddon`
- **Category:** AI Security
- **Purpose:** Kali security utility: airgeddon
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 88. altdns

- **ID:** `altdns`
- **Category:** Attack Surface
- **Purpose:** Kali security utility: altdns
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 89. android-sdk

- **ID:** `android-sdk`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: android-sdk
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 90. apple-bleee

- **ID:** `apple-bleee`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: apple-bleee
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 91. arjun

- **ID:** `arjun`
- **Category:** Web/API
- **Purpose:** Kali security utility: arjun
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 92. arsenal-ng

- **ID:** `arsenal-ng`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: arsenal-ng
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 93. autorecon

- **ID:** `autorecon`
- **Category:** Attack Surface
- **Purpose:** Kali security utility: autorecon
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 94. azurehound

- **ID:** `azurehound`
- **Category:** Cloud
- **Purpose:** Kali security utility: azurehound
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 95. b374k

- **ID:** `b374k`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: b374k
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 96. berate-ap

- **ID:** `berate-ap`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: berate-ap
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 97. bettercap-ui

- **ID:** `bettercap-ui`
- **Category:** Wireless
- **Purpose:** Kali security utility: bettercap-ui
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 98. bing-ip2hosts

- **ID:** `bing-ip2hosts`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: bing-ip2hosts
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 99. bloodhound

- **ID:** `bloodhound-2`
- **Category:** Identity
- **Purpose:** Kali security utility: bloodhound
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 100. bloodhound-ce-python

- **ID:** `bloodhound-ce-python`
- **Category:** Identity
- **Purpose:** Kali security utility: bloodhound-ce-python
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 101. bloodhound.py

- **ID:** `bloodhoundpy`
- **Category:** Identity
- **Purpose:** Kali security utility: bloodhound.py
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 102. bloodyad

- **ID:** `bloodyad`
- **Category:** Identity
- **Purpose:** Kali security utility: bloodyad
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 103. bopscrk

- **ID:** `bopscrk`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: bopscrk
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 104. bpf-linker

- **ID:** `bpf-linker`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: bpf-linker
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 105. bruteforce-luks

- **ID:** `bruteforce-luks`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: bruteforce-luks
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 106. bruteforce-salted-openssl

- **ID:** `bruteforce-salted-openssl`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: bruteforce-salted-openssl
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 107. bruteforce-wallet

- **ID:** `bruteforce-wallet`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: bruteforce-wallet
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 108. bruteshark

- **ID:** `bruteshark`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: bruteshark
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 109. brutespray

- **ID:** `brutespray`
- **Category:** Credential Audit
- **Purpose:** Kali security utility: brutespray
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 110. caido

- **ID:** `caido`
- **Category:** AI Security
- **Purpose:** Kali security utility: caido
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 111. caido-cli

- **ID:** `caido-cli`
- **Category:** AI Security
- **Purpose:** Kali security utility: caido-cli
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 112. calicoctl

- **ID:** `calicoctl`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: calicoctl
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 113. capstone-tool

- **ID:** `capstone-tool`
- **Category:** Reverse Engineering
- **Purpose:** Kali security utility: capstone-tool
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Open a copy in an isolated workspace, inspect metadata/imports/strings/control flow, map behavior to detections, and preserve hashes.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 114. certgraph

- **ID:** `certgraph`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: certgraph
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 115. certi

- **ID:** `certi`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: certi
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 116. chainsaw

- **ID:** `chainsaw`
- **Category:** AI Security
- **Purpose:** Kali security utility: chainsaw
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 117. changeme

- **ID:** `changeme`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: changeme
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 118. chaosreader

- **ID:** `chaosreader`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: chaosreader
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 119. chisel

- **ID:** `chisel`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: chisel
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 120. chisel-common-binaries

- **ID:** `chisel-common-binaries`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: chisel-common-binaries
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 121. cilium-cli

- **ID:** `cilium-cli`
- **Category:** Kubernetes
- **Purpose:** Kali security utility: cilium-cli
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 122. cisco7crack

- **ID:** `cisco7crack`
- **Category:** Credential Audit
- **Purpose:** Kali security utility: cisco7crack
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 123. cloud-enum

- **ID:** `cloud-enum`
- **Category:** Cloud
- **Purpose:** Kali security utility: cloud-enum
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 124. cloudbrute

- **ID:** `cloudbrute`
- **Category:** Cloud
- **Purpose:** Kali security utility: cloudbrute
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 125. cmseek

- **ID:** `cmseek`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: cmseek
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 126. cntlm

- **ID:** `cntlm`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: cntlm
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 127. coercer

- **ID:** `coercer`
- **Category:** Identity
- **Purpose:** Kali security utility: coercer
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 128. colly

- **ID:** `colly`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: colly
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 129. cosign

- **ID:** `cosign`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: cosign
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 130. crack

- **ID:** `crack`
- **Category:** Credential Audit
- **Purpose:** Kali security utility: crack
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 131. crackmapexec

- **ID:** `crackmapexec`
- **Category:** Credential Audit
- **Purpose:** Kali security utility: crackmapexec
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 132. cri-tools

- **ID:** `cri-tools`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: cri-tools
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 133. crlfuzz

- **ID:** `crlfuzz`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: crlfuzz
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 134. crowbar

- **ID:** `crowbar`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: crowbar
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 135. cupid-hostapd

- **ID:** `cupid-hostapd`
- **Category:** Wireless
- **Purpose:** Kali security utility: cupid-hostapd
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 136. cupid-wpasupplicant

- **ID:** `cupid-wpasupplicant`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: cupid-wpasupplicant
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 137. defectdojo

- **ID:** `defectdojo`
- **Category:** AppSec
- **Purpose:** Kali security utility: defectdojo
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 138. detect-it-easy

- **ID:** `detect-it-easy`
- **Category:** Reverse Engineering
- **Purpose:** Kali security utility: detect-it-easy
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Open a copy in an isolated workspace, inspect metadata/imports/strings/control flow, map behavior to detections, and preserve hashes.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 139. dirbuster

- **ID:** `dirbuster`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: dirbuster
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 140. dislocker

- **ID:** `dislocker`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: dislocker
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 141. dnscat2

- **ID:** `dnscat2`
- **Category:** Attack Surface
- **Purpose:** Kali security utility: dnscat2
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 142. dnsgen

- **ID:** `dnsgen`
- **Category:** Attack Surface
- **Purpose:** Kali security utility: dnsgen
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 143. dnstwist

- **ID:** `dnstwist`
- **Category:** Attack Surface
- **Purpose:** Kali security utility: dnstwist
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 144. donut

- **ID:** `donut`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: donut
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 145. dscan

- **ID:** `dscan`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: dscan
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 146. dufflebag

- **ID:** `dufflebag`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: dufflebag
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 147. dumpsterdiver

- **ID:** `dumpsterdiver`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: dumpsterdiver
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 148. dwarf2json

- **ID:** `dwarf2json`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: dwarf2json
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 149. eaphammer

- **ID:** `eaphammer`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: eaphammer
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 150. eksctl

- **ID:** `eksctl`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: eksctl
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 151. email2phonenumber

- **ID:** `email2phonenumber`
- **Category:** AI Security
- **Purpose:** Kali security utility: email2phonenumber
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 152. emailharvester

- **ID:** `emailharvester`
- **Category:** AI Security
- **Purpose:** Kali security utility: emailharvester
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 153. enum4linux-ng

- **ID:** `enum4linux-ng`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: enum4linux-ng
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 154. evil-ssdp

- **ID:** `evil-ssdp`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: evil-ssdp
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 155. evil-winrm-py

- **ID:** `evil-winrm-py`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: evil-winrm-py
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 156. evilginx2

- **ID:** `evilginx2`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: evilginx2
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 157. exiflooter

- **ID:** `exiflooter`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: exiflooter
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 158. exploitdb-bin-sploits

- **ID:** `exploitdb-bin-sploits`
- **Category:** Exploit Validation
- **Purpose:** Kali security utility: exploitdb-bin-sploits
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use an isolated lab or explicitly approved validation worker. Confirm the suspected weakness and preserve evidence; do not use an unrestricted shell.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 159. exploitdb-papers

- **ID:** `exploitdb-papers`
- **Category:** Exploit Validation
- **Purpose:** Kali security utility: exploitdb-papers
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use an isolated lab or explicitly approved validation worker. Confirm the suspected weakness and preserve evidence; do not use an unrestricted shell.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 160. faraday

- **ID:** `faraday`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: faraday
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 161. faraday-agent-dispatcher

- **ID:** `faraday-agent-dispatcher`
- **Category:** AI Security
- **Purpose:** Kali security utility: faraday-agent-dispatcher
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 162. faraday-cli

- **ID:** `faraday-cli`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: faraday-cli
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 163. fatcat

- **ID:** `fatcat`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: fatcat
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 164. feroxbuster

- **ID:** `feroxbuster-2`
- **Category:** Web/API
- **Purpose:** Kali security utility: feroxbuster
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 165. finalrecon

- **ID:** `finalrecon`
- **Category:** Attack Surface
- **Purpose:** Kali security utility: finalrecon
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 166. findomain

- **ID:** `findomain`
- **Category:** AI Security
- **Purpose:** Kali security utility: findomain
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 167. fluxion

- **ID:** `fluxion`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: fluxion
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 168. freeradius

- **ID:** `freeradius`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: freeradius
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 169. gdb-peda

- **ID:** `gdb-peda`
- **Category:** Reverse Engineering
- **Purpose:** Kali security utility: gdb-peda
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Open a copy in an isolated workspace, inspect metadata/imports/strings/control flow, map behavior to detections, and preserve hashes.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 170. gef

- **ID:** `gef`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: gef
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 171. gemini-cli

- **ID:** `gemini-cli`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: gemini-cli
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 172. getallurls

- **ID:** `getallurls`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: getallurls
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 173. getsploit

- **ID:** `getsploit`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: getsploit
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 174. gitleaks

- **ID:** `gitleaks`
- **Category:** AppSec
- **Purpose:** Kali security utility: gitleaks
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 175. gitxray

- **ID:** `gitxray`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: gitxray
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 176. godoh

- **ID:** `godoh`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: godoh
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 177. golang-github-binject-go-donut

- **ID:** `golang-github-binject-go-donut`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: golang-github-binject-go-donut
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 178. goldeneye

- **ID:** `goldeneye`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: goldeneye
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 179. goofile

- **ID:** `goofile`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: goofile
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 180. google-nexus-tools

- **ID:** `google-nexus-tools`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: google-nexus-tools
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 181. goshs

- **ID:** `goshs`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: goshs
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 182. gospider

- **ID:** `gospider`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: gospider
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 183. gowitness

- **ID:** `gowitness`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: gowitness
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 184. graudit

- **ID:** `graudit`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: graudit
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 185. gsocket

- **ID:** `gsocket`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: gsocket
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 186. gtkhash

- **ID:** `gtkhash`
- **Category:** Credential Audit
- **Purpose:** Kali security utility: gtkhash
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 187. h8mail

- **ID:** `h8mail`
- **Category:** AI Security
- **Purpose:** Kali security utility: h8mail
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 188. hak5-wifi-coconut

- **ID:** `hak5-wifi-coconut`
- **Category:** Wireless
- **Purpose:** Kali security utility: hak5-wifi-coconut
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 189. hashrat

- **ID:** `hashrat`
- **Category:** Credential Audit
- **Purpose:** Kali security utility: hashrat
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 190. havoc

- **ID:** `havoc`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: havoc
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 191. hb-honeypot

- **ID:** `hb-honeypot`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: hb-honeypot
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 192. hcxtools

- **ID:** `hcxtools`
- **Category:** Wireless
- **Purpose:** Kali security utility: hcxtools
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 193. hekatomb

- **ID:** `hekatomb`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: hekatomb
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 194. hexstrike-ai

- **ID:** `hexstrike-ai`
- **Category:** AI Security
- **Purpose:** Kali security utility: hexstrike-ai
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 195. hexwalk

- **ID:** `hexwalk`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: hexwalk
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 196. hoaxshell

- **ID:** `hoaxshell`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: hoaxshell
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 197. horst

- **ID:** `horst`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: horst
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 198. hostapd-mana

- **ID:** `hostapd-mana`
- **Category:** Wireless
- **Purpose:** Kali security utility: hostapd-mana
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 199. hosthunter

- **ID:** `hosthunter`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: hosthunter
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 200. hostsman

- **ID:** `hostsman`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: hostsman
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 201. htshells

- **ID:** `htshells`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: htshells
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 202. httprobe

- **ID:** `httprobe`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: httprobe
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 203. httpx-toolkit

- **ID:** `httpx-toolkit`
- **Category:** Web/API
- **Purpose:** Kali security utility: httpx-toolkit
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 204. hubble

- **ID:** `hubble`
- **Category:** Kubernetes
- **Purpose:** Kali security utility: hubble
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 205. humble

- **ID:** `humble`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: humble
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 206. hurl

- **ID:** `hurl`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: hurl
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 207. ibombshell

- **ID:** `ibombshell`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: ibombshell
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 208. ident-user-enum

- **ID:** `ident-user-enum`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: ident-user-enum
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 209. imhex

- **ID:** `imhex`
- **Category:** Reverse Engineering
- **Purpose:** Kali security utility: imhex
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Open a copy in an isolated workspace, inspect metadata/imports/strings/control flow, map behavior to detections, and preserve hashes.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 210. inspy

- **ID:** `inspy`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: inspy
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 211. instaloader

- **ID:** `instaloader`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: instaloader
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 212. ipv6toolkit

- **ID:** `ipv6toolkit`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: ipv6toolkit
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 213. ismtp

- **ID:** `ismtp`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: ismtp
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 214. ivre

- **ID:** `ivre`
- **Category:** Network Discovery
- **Purpose:** Kali security utility: ivre
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 215. joplin

- **ID:** `joplin`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: joplin
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 216. jsp-file-browser

- **ID:** `jsp-file-browser`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: jsp-file-browser
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 217. kali-community-wallpapers

- **ID:** `kali-community-wallpapers`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: kali-community-wallpapers
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 218. kerberoast

- **ID:** `kerberoast`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: kerberoast
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 219. knocker

- **ID:** `knocker`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: knocker
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 220. koadic

- **ID:** `koadic`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: koadic
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 221. krbrelayx

- **ID:** `krbrelayx`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: krbrelayx
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 222. kubernetes-helm

- **ID:** `kubernetes-helm`
- **Category:** Kubernetes
- **Purpose:** Kali security utility: kubernetes-helm
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 223. kustomize

- **ID:** `kustomize`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: kustomize
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 224. lapsdumper

- **ID:** `lapsdumper`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: lapsdumper
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 225. ldeep

- **ID:** `ldeep`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: ldeep
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 226. legba

- **ID:** `legba`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: legba
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 227. ligolo-mp

- **ID:** `ligolo-mp`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: ligolo-mp
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 228. ligolo-ng

- **ID:** `ligolo-ng`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: ligolo-ng
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 229. ligolo-ng-common-binaries

- **ID:** `ligolo-ng-common-binaries`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: ligolo-ng-common-binaries
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 230. linkedin2username

- **ID:** `linkedin2username`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: linkedin2username
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 231. linux-exploit-suggester

- **ID:** `linux-exploit-suggester`
- **Category:** Exploit Validation
- **Purpose:** Kali security utility: linux-exploit-suggester
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use an isolated lab or explicitly approved validation worker. Confirm the suspected weakness and preserve evidence; do not use an unrestricted shell.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 232. llm-tools-nmap

- **ID:** `llm-tools-nmap`
- **Category:** AI Security
- **Purpose:** Kali security utility: llm-tools-nmap
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 233. maltego-teeth

- **ID:** `maltego-teeth`
- **Category:** Attack Surface
- **Purpose:** Kali security utility: maltego-teeth
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 234. maryam

- **ID:** `maryam`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: maryam
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 235. massdns

- **ID:** `massdns`
- **Category:** Attack Surface
- **Purpose:** Kali security utility: massdns
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 236. mcp-kali-server

- **ID:** `mcp-kali-server`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: mcp-kali-server
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 237. merlin-agent

- **ID:** `merlin-agent`
- **Category:** AI Security
- **Purpose:** Kali security utility: merlin-agent
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 238. merlin-server

- **ID:** `merlin-server`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: merlin-server
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 239. metasploitmcp

- **ID:** `metasploitmcp`
- **Category:** Exploit Validation
- **Purpose:** Kali security utility: metasploitmcp
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use an isolated lab or explicitly approved validation worker. Confirm the suspected weakness and preserve evidence; do not use an unrestricted shell.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 240. mitm6

- **ID:** `mitm6`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: mitm6
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 241. mongo-tools

- **ID:** `mongo-tools`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: mongo-tools
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 242. mssqlpwner

- **ID:** `mssqlpwner`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: mssqlpwner
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 243. multiforcer

- **ID:** `multiforcer`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: multiforcer
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 244. mxcheck

- **ID:** `mxcheck`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: mxcheck
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 245. naabu

- **ID:** `naabu-2`
- **Category:** Network Discovery
- **Purpose:** Kali security utility: naabu
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 246. name-that-hash

- **ID:** `name-that-hash`
- **Category:** Credential Audit
- **Purpose:** Kali security utility: name-that-hash
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 247. nbtscan-unixwiz

- **ID:** `nbtscan-unixwiz`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: nbtscan-unixwiz
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 248. netscanner

- **ID:** `netscanner`
- **Category:** Network Discovery
- **Purpose:** Kali security utility: netscanner
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 249. nextnet

- **ID:** `nextnet`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: nextnet
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 250. nmapsi4

- **ID:** `nmapsi4`
- **Category:** Network Discovery
- **Purpose:** Kali security utility: nmapsi4
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 251. nuclei

- **ID:** `nuclei-2`
- **Category:** Web/API
- **Purpose:** Kali security utility: nuclei
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 252. obsidian

- **ID:** `obsidian`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: obsidian
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 253. odat

- **ID:** `odat`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: odat
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 254. oletools

- **ID:** `oletools`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: oletools
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 255. opentaxii

- **ID:** `opentaxii`
- **Category:** Threat Intelligence
- **Purpose:** Kali security utility: opentaxii
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Normalize indicators with source and confidence, correlate against internal telemetry, and keep attribution hypotheses separate from confirmed facts.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 256. osrframework

- **ID:** `osrframework`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: osrframework
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 257. owl

- **ID:** `owl`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: owl
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 258. pacu

- **ID:** `pacu`
- **Category:** Cloud
- **Purpose:** Kali security utility: pacu
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 259. parsero

- **ID:** `parsero`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: parsero
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 260. passdetective

- **ID:** `passdetective`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: passdetective
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 261. patchleaks

- **ID:** `patchleaks`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: patchleaks
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 262. payloadsallthethings

- **ID:** `payloadsallthethings`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: payloadsallthethings
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 263. peirates

- **ID:** `peirates`
- **Category:** Kubernetes
- **Purpose:** Kali security utility: peirates
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 264. penelope

- **ID:** `penelope`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: penelope
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 265. phishery

- **ID:** `phishery`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: phishery
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 266. photon

- **ID:** `photon`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: photon
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 267. phpggc

- **ID:** `phpggc`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: phpggc
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 268. phpsploit

- **ID:** `phpsploit`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: phpsploit
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 269. pnscan

- **ID:** `pnscan`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: pnscan
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 270. pocsuite3

- **ID:** `pocsuite3`
- **Category:** Exploit Validation
- **Purpose:** Kali security utility: pocsuite3
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use an isolated lab or explicitly approved validation worker. Confirm the suspected weakness and preserve evidence; do not use an unrestricted shell.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 271. pompem

- **ID:** `pompem`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: pompem
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 272. portspoof

- **ID:** `portspoof`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: portspoof
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 273. poshc2

- **ID:** `poshc2`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: poshc2
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 274. princeprocessor

- **ID:** `princeprocessor`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: princeprocessor
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 275. proxify

- **ID:** `proxify`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: proxify
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 276. proximoth

- **ID:** `proximoth`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: proximoth
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 277. proxmark3

- **ID:** `proxmark3`
- **Category:** Wireless
- **Purpose:** Kali security utility: proxmark3
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 278. pskracker

- **ID:** `pskracker`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: pskracker
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 279. pspy

- **ID:** `pspy`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: pspy
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 280. pwncat

- **ID:** `pwncat`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: pwncat
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 281. pyinstxtractor

- **ID:** `pyinstxtractor`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: pyinstxtractor
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 282. python3-atomic-operator

- **ID:** `python3-atomic-operator`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: python3-atomic-operator
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 283. python3-dploot

- **ID:** `python3-dploot`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: python3-dploot
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 284. python3-ldapdomaindump

- **ID:** `python3-ldapdomaindump`
- **Category:** AI Security
- **Purpose:** Kali security utility: python3-ldapdomaindump
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 285. python3-pyinstaller

- **ID:** `python3-pyinstaller`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: python3-pyinstaller
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 286. python3-wsgidav

- **ID:** `python3-wsgidav`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: python3-wsgidav
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 287. quark-engine

- **ID:** `quark-engine`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: quark-engine
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 288. raven

- **ID:** `raven`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: raven
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 289. reconspider

- **ID:** `reconspider`
- **Category:** Attack Surface
- **Purpose:** Kali security utility: reconspider
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 290. redeye

- **ID:** `redeye`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: redeye
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 291. redsnarf

- **ID:** `redsnarf`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: redsnarf
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 292. rev-proxy-grapher

- **ID:** `rev-proxy-grapher`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: rev-proxy-grapher
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 293. ridenum

- **ID:** `ridenum`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: ridenum
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 294. rling

- **ID:** `rling`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: rling
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 295. robotstxt

- **ID:** `robotstxt`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: robotstxt
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 296. ropper

- **ID:** `ropper`
- **Category:** Reverse Engineering
- **Purpose:** Kali security utility: ropper
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Open a copy in an isolated workspace, inspect metadata/imports/strings/control flow, map behavior to detections, and preserve hashes.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 297. routersploit

- **ID:** `routersploit`
- **Category:** Exploit Validation
- **Purpose:** Kali security utility: routersploit
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use an isolated lab or explicitly approved validation worker. Confirm the suspected weakness and preserve evidence; do not use an unrestricted shell.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 298. rubeus

- **ID:** `rubeus`
- **Category:** Identity
- **Purpose:** Kali security utility: rubeus
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 299. ruby-pedump

- **ID:** `ruby-pedump`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: ruby-pedump
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 300. s3scanner

- **ID:** `s3scanner`
- **Category:** Attack Surface
- **Purpose:** Kali security utility: s3scanner
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 301. sara

- **ID:** `sara`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: sara
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 302. sentrypeer

- **ID:** `sentrypeer`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: sentrypeer
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 303. sharphound

- **ID:** `sharphound`
- **Category:** Identity
- **Purpose:** Kali security utility: sharphound
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 304. sharpshooter

- **ID:** `sharpshooter`
- **Category:** Identity
- **Purpose:** Kali security utility: sharpshooter
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 305. shed

- **ID:** `shed`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: shed
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 306. shell-gpt

- **ID:** `shell-gpt`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: shell-gpt
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 307. shellfire

- **ID:** `shellfire`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: shellfire
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 308. sherlock

- **ID:** `sherlock`
- **Category:** Attack Surface
- **Purpose:** Kali security utility: sherlock
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 309. sickle-pdk

- **ID:** `sickle-pdk`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: sickle-pdk
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 310. sigma-cli

- **ID:** `sigma-cli`
- **Category:** Threat Intelligence
- **Purpose:** Kali security utility: sigma-cli
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Normalize indicators with source and confidence, correlate against internal telemetry, and keep attribution hypotheses separate from confirmed facts.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 311. silenttrinity

- **ID:** `silenttrinity`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: silenttrinity
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 312. sippts

- **ID:** `sippts`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: sippts
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 313. slimtoolkit

- **ID:** `slimtoolkit`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: slimtoolkit
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 314. sliver

- **ID:** `sliver`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: sliver
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 315. sn0int

- **ID:** `sn0int`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: sn0int
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 316. snmpenum

- **ID:** `snmpenum`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: snmpenum
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 317. snowdrop

- **ID:** `snowdrop`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: snowdrop
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 318. sparrow-wifi

- **ID:** `sparrow-wifi`
- **Category:** Wireless
- **Purpose:** Kali security utility: sparrow-wifi
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 319. spire

- **ID:** `spire`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: spire
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 320. sploitscan

- **ID:** `sploitscan`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: sploitscan
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 321. spray

- **ID:** `spray`
- **Category:** Credential Audit
- **Purpose:** Kali security utility: spray
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 322. sprayhound

- **ID:** `sprayhound`
- **Category:** Credential Audit
- **Purpose:** Kali security utility: sprayhound
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 323. sprayingtoolkit

- **ID:** `sprayingtoolkit`
- **Category:** Credential Audit
- **Purpose:** Kali security utility: sprayingtoolkit
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 324. spraykatz

- **ID:** `spraykatz`
- **Category:** Credential Audit
- **Purpose:** Kali security utility: spraykatz
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 325. sqlmc

- **ID:** `sqlmc`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: sqlmc
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 326. sshuttle

- **ID:** `sshuttle`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: sshuttle
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 327. sslstrip

- **ID:** `sslstrip`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: sslstrip
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 328. sstimap

- **ID:** `sstimap`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: sstimap
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 329. stegcracker

- **ID:** `stegcracker`
- **Category:** Credential Audit
- **Purpose:** Kali security utility: stegcracker
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only authorized offline audit material or a dedicated lab. Treat credentials as secrets, minimize exposure, and record the audit scope.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 330. subfinder

- **ID:** `subfinder-2`
- **Category:** Attack Surface
- **Purpose:** Kali security utility: subfinder
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 331. subjack

- **ID:** `subjack`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: subjack
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 332. sublist3r

- **ID:** `sublist3r`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: sublist3r
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 333. syft

- **ID:** `syft-2`
- **Category:** AppSec
- **Purpose:** Kali security utility: syft
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 334. tailscale

- **ID:** `tailscale`
- **Category:** AI Security
- **Purpose:** Kali security utility: tailscale
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 335. teamsploit

- **ID:** `teamsploit`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: teamsploit
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 336. terraform

- **ID:** `terraform`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: terraform
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 337. testssl.sh

- **ID:** `testsslsh`
- **Category:** Web/API
- **Purpose:** Kali security utility: testssl.sh
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 338. tetragon

- **ID:** `tetragon`
- **Category:** Kubernetes
- **Purpose:** Kali security utility: tetragon
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 339. tinja

- **ID:** `tinja`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: tinja
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 340. tookie-osint

- **ID:** `tookie-osint`
- **Category:** Attack Surface
- **Purpose:** Kali security utility: tookie-osint
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 341. trivy

- **ID:** `trivy-2`
- **Category:** AppSec
- **Purpose:** Kali security utility: trivy
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 342. trufflehog

- **ID:** `trufflehog`
- **Category:** AppSec
- **Purpose:** Kali security utility: trufflehog
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 343. tundeep

- **ID:** `tundeep`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: tundeep
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 344. unblob

- **ID:** `unblob`
- **Category:** Reverse Engineering
- **Purpose:** Kali security utility: unblob
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Open a copy in an isolated workspace, inspect metadata/imports/strings/control flow, map behavior to detections, and preserve hashes.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 345. unhide.rb

- **ID:** `unhiderb`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: unhide.rb
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 346. unicorn-magic

- **ID:** `unicorn-magic`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: unicorn-magic
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 347. uro

- **ID:** `uro`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: uro
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 348. vopono

- **ID:** `vopono`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: vopono
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 349. vwifi-tool

- **ID:** `vwifi-tool`
- **Category:** Wireless
- **Purpose:** Kali security utility: vwifi-tool
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 350. waybackpy

- **ID:** `waybackpy`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: waybackpy
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 351. web-cache-vulnerability-scanner

- **ID:** `web-cache-vulnerability-scanner`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: web-cache-vulnerability-scanner
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 352. websploit

- **ID:** `websploit`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: websploit
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 353. wgetpaste

- **ID:** `wgetpaste`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: wgetpaste
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 354. whatmask

- **ID:** `whatmask`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: whatmask
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 355. wifiphisher

- **ID:** `wifiphisher`
- **Category:** Wireless
- **Purpose:** Kali security utility: wifiphisher
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 356. wifipumpkin3

- **ID:** `wifipumpkin3`
- **Category:** Wireless
- **Purpose:** Kali security utility: wifipumpkin3
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 357. wig

- **ID:** `wig`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: wig
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 358. wig-ng

- **ID:** `wig-ng`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: wig-ng
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 359. witnessme

- **ID:** `witnessme`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: witnessme
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 360. wixl

- **ID:** `wixl`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: wixl
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 361. wmi-client

- **ID:** `wmi-client`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: wmi-client
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 362. wordlistraider

- **ID:** `wordlistraider`
- **Category:** AI Security
- **Purpose:** Kali security utility: wordlistraider
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 363. wotmate

- **ID:** `wotmate`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: wotmate
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 364. wpa-sycophant

- **ID:** `wpa-sycophant`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: wpa-sycophant
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 365. wpprobe

- **ID:** `wpprobe`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: wpprobe
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 366. xsrfprobe

- **ID:** `xsrfprobe`
- **Category:** Web/API
- **Purpose:** Kali security utility: xsrfprobe
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 367. xsstrike

- **ID:** `xsstrike`
- **Category:** Web/API
- **Purpose:** Kali security utility: xsstrike
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 368. zonedb

- **ID:** `zonedb`
- **Category:** Security Utilities
- **Purpose:** Kali security utility: zonedb
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 369. ADRecon

- **ID:** `adrecon`
- **Category:** Identity
- **Purpose:** Advanced identity capability: ADRecon
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 370. AI-SPM Connector

- **ID:** `ai-spm-connector`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: AI-SPM Connector
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 371. ART

- **ID:** `art`
- **Category:** Security Utilities
- **Purpose:** Advanced security utilities capability: ART
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 372. AgentDojo

- **ID:** `agentdojo`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: AgentDojo
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 373. AgentWarden

- **ID:** `agentwarden`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: AgentWarden
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 374. Aircrack-ng

- **ID:** `aircrack-ng`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: Aircrack-ng
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 375. Airgeddon

- **ID:** `airgeddon-2`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: Airgeddon
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 376. Arjun

- **ID:** `arjun-2`
- **Category:** Web/API
- **Purpose:** Advanced web/api capability: Arjun
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 377. Arkime

- **ID:** `arkime`
- **Category:** Network Discovery
- **Purpose:** Advanced network discovery capability: Arkime
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 378. BTLEJack

- **ID:** `btlejack`
- **Category:** Wireless
- **Purpose:** Advanced wireless capability: BTLEJack
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 379. Bettercap

- **ID:** `bettercap`
- **Category:** Wireless
- **Purpose:** Advanced wireless capability: Bettercap
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 380. BloodHound CE

- **ID:** `bloodhound-ce`
- **Category:** Identity
- **Purpose:** Advanced identity capability: BloodHound CE
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 381. BloodyAD

- **ID:** `bloodyad-2`
- **Category:** Identity
- **Purpose:** Advanced identity capability: BloodyAD
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 382. CAPA

- **ID:** `capa-2`
- **Category:** DFIR
- **Purpose:** Advanced dfir capability: CAPA
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Acquire authorized artifacts, hash originals, analyze copies, preserve chain of custody, and record conclusions with confidence.
- **Expected evidence:** artifact hash, metadata, timeline, chain-of-custody reference
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 383. Cartography

- **ID:** `cartography`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: Cartography
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 384. Chainsaw

- **ID:** `chainsaw-2`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: Chainsaw
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 385. Cilium

- **ID:** `cilium`
- **Category:** Kubernetes
- **Purpose:** Advanced kubernetes capability: Cilium
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 386. Cloud Custodian

- **ID:** `cloud-custodian`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: Cloud Custodian
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 387. CloudFox

- **ID:** `cloudfox`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: CloudFox
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 388. CloudMapper

- **ID:** `cloudmapper`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: CloudMapper
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 389. CloudQuery

- **ID:** `cloudquery`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: CloudQuery
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 390. Coercer

- **ID:** `coercer-2`
- **Category:** Identity
- **Purpose:** Advanced identity capability: Coercer
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 391. CyberSecEval

- **ID:** `cyberseceval`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: CyberSecEval
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 392. CycloneDX CLI

- **ID:** `cyclonedx-cli`
- **Category:** AppSec
- **Purpose:** Advanced appsec capability: CycloneDX CLI
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 393. Dalfox

- **ID:** `dalfox`
- **Category:** Web/API
- **Purpose:** Advanced web/api capability: Dalfox
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 394. Datree

- **ID:** `datree`
- **Category:** Security Utilities
- **Purpose:** Advanced security utilities capability: Datree
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 395. DeepEval

- **ID:** `deepeval`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: DeepEval
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 396. DefectDojo

- **ID:** `defectdojo-2`
- **Category:** AppSec
- **Purpose:** Advanced appsec capability: DefectDojo
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 397. Dependency-Track

- **ID:** `dependency-track`
- **Category:** AppSec
- **Purpose:** Advanced appsec capability: Dependency-Track
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 398. Eric Zimmerman Tools

- **ID:** `eric-zimmerman-tools`
- **Category:** DFIR
- **Purpose:** Advanced dfir capability: Eric Zimmerman Tools
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Acquire authorized artifacts, hash originals, analyze copies, preserve chain of custody, and record conclusions with confidence.
- **Expected evidence:** artifact hash, metadata, timeline, chain-of-custody reference
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 399. Fickling

- **ID:** `fickling`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: Fickling
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 400. GNU Radio

- **ID:** `gnu-radio`
- **Category:** Security Utilities
- **Purpose:** Advanced security utilities capability: GNU Radio
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 401. Giskard

- **ID:** `giskard`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: Giskard
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 402. Gitleaks

- **ID:** `gitleaks-2`
- **Category:** AppSec
- **Purpose:** Advanced appsec capability: Gitleaks
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 403. Guardrails AI

- **ID:** `guardrails-ai`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: Guardrails AI
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 404. HTTPX

- **ID:** `httpx-2`
- **Category:** Web/API
- **Purpose:** Advanced web/api capability: HTTPX
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 405. HackRF tools

- **ID:** `hackrf-tools`
- **Category:** Wireless
- **Purpose:** Advanced wireless capability: HackRF tools
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 406. Hayabusa

- **ID:** `hayabusa`
- **Category:** DFIR
- **Purpose:** Advanced dfir capability: Hayabusa
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Acquire authorized artifacts, hash originals, analyze copies, preserve chain of custody, and record conclusions with confidence.
- **Expected evidence:** artifact hash, metadata, timeline, chain-of-custody reference
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 407. Hostapd-MANA

- **ID:** `hostapd-mana-2`
- **Category:** Wireless
- **Purpose:** Advanced wireless capability: Hostapd-MANA
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 408. Hubble

- **ID:** `hubble-2`
- **Category:** Kubernetes
- **Purpose:** Advanced kubernetes capability: Hubble
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 409. IAMGraph

- **ID:** `iamgraph`
- **Category:** Security Utilities
- **Purpose:** Advanced security utilities capability: IAMGraph
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 410. IVRE

- **ID:** `ivre-2`
- **Category:** Network Discovery
- **Purpose:** Advanced network discovery capability: IVRE
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 411. Inspect AI

- **ID:** `inspect-ai`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: Inspect AI
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 412. Interactsh

- **ID:** `interactsh`
- **Category:** Security Utilities
- **Purpose:** Advanced security utilities capability: Interactsh
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 413. Invariant

- **ID:** `invariant`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: Invariant
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 414. KAPE

- **ID:** `kape`
- **Category:** DFIR
- **Purpose:** Advanced dfir capability: KAPE
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Acquire authorized artifacts, hash originals, analyze copies, preserve chain of custody, and record conclusions with confidence.
- **Expected evidence:** artifact hash, metadata, timeline, chain-of-custody reference
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 415. KICS

- **ID:** `kics`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: KICS
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 416. Katana

- **ID:** `katana`
- **Category:** Web/API
- **Purpose:** Advanced web/api capability: Katana
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 417. Kismet

- **ID:** `kismet`
- **Category:** Wireless
- **Purpose:** Advanced wireless capability: Kismet
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 418. Kiterunner

- **ID:** `kiterunner`
- **Category:** Web/API
- **Purpose:** Advanced web/api capability: Kiterunner
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Select an authorized application, begin with mapping/passive checks, review findings, then use only the approved active assessment profile.
- **Expected evidence:** URLs/endpoints, HTTP metadata, alerts/findings, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 419. KubeLinter

- **ID:** `kubelinter`
- **Category:** Kubernetes
- **Purpose:** Advanced kubernetes capability: KubeLinter
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 420. LDAPDomainDump

- **ID:** `ldapdomaindump`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: LDAPDomainDump
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 421. Langfuse

- **ID:** `langfuse`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: Langfuse
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 422. LlamaFirewall

- **ID:** `llamafirewall`
- **Category:** Security Utilities
- **Purpose:** Advanced security utilities capability: LlamaFirewall
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 423. MLflow

- **ID:** `mlflow`
- **Category:** Security Utilities
- **Purpose:** Advanced security utilities capability: MLflow
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 424. MemProcFS

- **ID:** `memprocfs`
- **Category:** DFIR
- **Purpose:** Advanced dfir capability: MemProcFS
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Acquire authorized artifacts, hash originals, analyze copies, preserve chain of custody, and record conclusions with confidence.
- **Expected evidence:** artifact hash, metadata, timeline, chain-of-custody reference
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 425. ModelScan

- **ID:** `modelscan`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: ModelScan
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 426. ModelScan CLI

- **ID:** `modelscan-cli`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: ModelScan CLI
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 427. NVIDIA NeMo Safety

- **ID:** `nvidia-nemo-safety`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: NVIDIA NeMo Safety
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 428. NetBox

- **ID:** `netbox`
- **Category:** Network Discovery
- **Purpose:** Advanced network discovery capability: NetBox
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 429. Netdisco

- **ID:** `netdisco`
- **Category:** Network Discovery
- **Purpose:** Advanced network discovery capability: Netdisco
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 430. Ntop

- **ID:** `ntop`
- **Category:** Network Discovery
- **Purpose:** Advanced network discovery capability: Ntop
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 431. OSV-Scanner

- **ID:** `osv-scanner`
- **Category:** AppSec
- **Purpose:** Advanced appsec capability: OSV-Scanner
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 432. OWASP Amass

- **ID:** `owasp-amass`
- **Category:** Attack Surface
- **Purpose:** Advanced attack surface capability: OWASP Amass
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Start with an approved asset/domain list, prefer passive collection, validate ownership, then perform only the approved assessment stage.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 433. OWASP Dependency-Check

- **ID:** `owasp-dependency-check`
- **Category:** AppSec
- **Purpose:** Advanced appsec capability: OWASP Dependency-Check
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 434. OpenAI Evals

- **ID:** `openai-evals`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: OpenAI Evals
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 435. OpenSearch Security Analytics

- **ID:** `opensearch-security-analytics`
- **Category:** Security Utilities
- **Purpose:** Advanced security utilities capability: OpenSearch Security Analytics
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 436. OpenTelemetry GenAI

- **ID:** `opentelemetry-genai`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: OpenTelemetry GenAI
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 437. Pacu

- **ID:** `pacu-2`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: Pacu
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 438. Parliament

- **ID:** `parliament`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: Parliament
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 439. Peirates

- **ID:** `peirates-2`
- **Category:** Kubernetes
- **Purpose:** Advanced kubernetes capability: Peirates
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 440. PetitPotam

- **ID:** `petitpotam`
- **Category:** Security Utilities
- **Purpose:** Advanced security utilities capability: PetitPotam
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 441. Phoenix Arize

- **ID:** `phoenix-arize`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: Phoenix Arize
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 442. PingCastle

- **ID:** `pingcastle`
- **Category:** Identity
- **Purpose:** Advanced identity capability: PingCastle
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 443. Plaso

- **ID:** `plaso`
- **Category:** DFIR
- **Purpose:** Advanced dfir capability: Plaso
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Acquire authorized artifacts, hash originals, analyze copies, preserve chain of custody, and record conclusions with confidence.
- **Expected evidence:** artifact hash, metadata, timeline, chain-of-custody reference
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 444. Polaris

- **ID:** `polaris`
- **Category:** Security Utilities
- **Purpose:** Advanced security utilities capability: Polaris
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 445. Policy Sentry

- **ID:** `policy-sentry`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: Policy Sentry
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 446. Principal Mapper

- **ID:** `principal-mapper`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: Principal Mapper
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 447. ProjectDiscovery Cloud

- **ID:** `projectdiscovery-cloud`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: ProjectDiscovery Cloud
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 448. Protect AI

- **ID:** `protect-ai`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: Protect AI
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 449. Proxmark3

- **ID:** `proxmark3-2`
- **Category:** Wireless
- **Purpose:** Advanced wireless capability: Proxmark3
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 450. Purple Knight

- **ID:** `purple-knight`
- **Category:** Identity
- **Purpose:** Advanced identity capability: Purple Knight
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 451. PyRIT

- **ID:** `pyrit`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: PyRIT
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 452. Rubeus

- **ID:** `rubeus-2`
- **Category:** Identity
- **Purpose:** Advanced identity capability: Rubeus
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 453. Samba-tool

- **ID:** `samba-tool`
- **Category:** Security Utilities
- **Purpose:** Advanced security utilities capability: Samba-tool
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 454. ScoutSuite

- **ID:** `scoutsuite`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: ScoutSuite
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 455. Security Onion

- **ID:** `security-onion`
- **Category:** Endpoint
- **Purpose:** Advanced endpoint capability: Security Onion
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the managed collector/agent on consented endpoints, collect telemetry, investigate anomalies, and avoid arbitrary remote execution.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 456. Semgrep AI rules

- **ID:** `semgrep-ai-rules`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: Semgrep AI rules
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 457. SharpHound

- **ID:** `sharphound-2`
- **Category:** Identity
- **Purpose:** Advanced identity capability: SharpHound
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use an approved directory or identity scope to map relationships, privilege paths and configuration weaknesses. Prioritize least privilege and MFA remediation.
- **Expected evidence:** accounts, relationships, privilege paths, configuration evidence
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 458. Sigma CLI

- **ID:** `sigma-cli-2`
- **Category:** Threat Intelligence
- **Purpose:** Advanced threat intelligence capability: Sigma CLI
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Normalize indicators with source and confidence, correlate against internal telemetry, and keep attribution hypotheses separate from confirmed facts.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 459. Snyk CLI

- **ID:** `snyk-cli`
- **Category:** AppSec
- **Purpose:** Advanced appsec capability: Snyk CLI
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 460. Starboard

- **ID:** `starboard`
- **Category:** Security Utilities
- **Purpose:** Advanced security utilities capability: Starboard
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the tool for its documented supporting security task inside an approved worker, inspect output, and preserve relevant evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 461. Steampipe

- **ID:** `steampipe`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: Steampipe
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 462. Stratus Red Team

- **ID:** `stratus-red-team`
- **Category:** Cloud
- **Purpose:** Advanced cloud capability: Stratus Red Team
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use read-only or explicitly approved cloud access, inventory resources and permissions, identify exposure, then remediate through change control.
- **Expected evidence:** resource IDs, policy/configuration findings, regions, timestamps
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 463. Tetragon

- **ID:** `tetragon-2`
- **Category:** Kubernetes
- **Purpose:** Advanced kubernetes capability: Tetragon
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 464. The Sleuth Kit

- **ID:** `the-sleuth-kit`
- **Category:** DFIR
- **Purpose:** Advanced dfir capability: The Sleuth Kit
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Acquire authorized artifacts, hash originals, analyze copies, preserve chain of custody, and record conclusions with confidence.
- **Expected evidence:** artifact hash, metadata, timeline, chain-of-custody reference
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 465. Timesketch

- **ID:** `timesketch`
- **Category:** DFIR
- **Purpose:** Advanced dfir capability: Timesketch
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Acquire authorized artifacts, hash originals, analyze copies, preserve chain of custody, and record conclusions with confidence.
- **Expected evidence:** artifact hash, metadata, timeline, chain-of-custody reference
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 466. TruffleHog

- **ID:** `trufflehog-2`
- **Category:** AppSec
- **Purpose:** Advanced appsec capability: TruffleHog
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Run code analysis in CI or an approved worker, triage results, justify suppressions, and link remediation to commits/builds.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 467. Ubertooth

- **ID:** `ubertooth`
- **Category:** Wireless
- **Purpose:** Advanced wireless capability: Ubertooth
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 468. Wazuh

- **ID:** `wazuh`
- **Category:** Endpoint
- **Purpose:** Advanced endpoint capability: Wazuh
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use the managed collector/agent on consented endpoints, collect telemetry, investigate anomalies, and avoid arbitrary remote execution.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 469. Weights & Biases Weave

- **ID:** `weights-&-biases-weave`
- **Category:** AI Security
- **Purpose:** Advanced ai security capability: Weights & Biases Weave
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `isolated_ai_worker`
- **Safe workflow:** Assess an approved AI application or agent for prompt/context integrity, tool authorization, RAG/data access, model supply chain and runtime telemetry.
- **Expected evidence:** test case ID, policy decision, model/agent trace, evidence hash
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 470. WiFi Explorer integration

- **ID:** `wifi-explorer-integration`
- **Category:** Wireless
- **Purpose:** Advanced wireless capability: WiFi Explorer integration
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 471. WiFi Pineapple

- **ID:** `wifi-pineapple`
- **Category:** Wireless
- **Purpose:** Advanced wireless capability: WiFi Pineapple
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 472. Wifite2

- **ID:** `wifite2`
- **Category:** Wireless
- **Purpose:** Advanced wireless capability: Wifite2
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Privileged Admin
- **Execution boundary:** `isolated_worker`
- **Safe workflow:** Use only networks you own/manage. Collect wireless metadata or approved lab evidence, compare against the trusted baseline, and preserve observations.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 473. YARA-X

- **ID:** `yara-x`
- **Category:** DFIR
- **Purpose:** Advanced dfir capability: YARA-X
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Acquire authorized artifacts, hash originals, analyze copies, preserve chain of custody, and record conclusions with confidence.
- **Expected evidence:** artifact hash, metadata, timeline, chain-of-custody reference
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 474. ZMap

- **ID:** `zmap`
- **Category:** Network Discovery
- **Purpose:** Advanced network discovery capability: ZMap
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 475. kube-score

- **ID:** `kube-score`
- **Category:** Kubernetes
- **Purpose:** Advanced kubernetes capability: kube-score
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 476. kubeaudit

- **ID:** `kubeaudit`
- **Category:** Kubernetes
- **Purpose:** Advanced kubernetes capability: kubeaudit
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Assess an approved cluster with least-privilege credentials, benchmark posture, inspect risky workloads/services, and preserve evidence.
- **Expected evidence:** tool output, target/scope, timestamp, provenance
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

### 477. ntopng

- **ID:** `ntopng`
- **Category:** Network Discovery
- **Purpose:** Advanced network discovery capability: ntopng
- **VEYRA role:** Provides a governed, auditable entry point with role-based access, scope controls and normalized evidence.
- **Access:** Admin
- **Execution boundary:** `approved_worker`
- **Safe workflow:** Define an owned/approved network scope, run discovery from the appropriate worker, validate hosts/services, then reconcile results with asset inventory.
- **Expected evidence:** hosts, ports/services, timestamps, scope
- **Common mistakes:** Using an asset outside the approved scope; Treating tool output as proof without validation; Ignoring evidence provenance or timestamps
- **Next step:** Validate the result, map it to VEYRA risk/graph/ATT&CK or ATLAS where applicable, remediate, and verify.
- **Help boundary:** Educational and defensive guidance only; no credential attacks, payloads, persistence, C2, evasion or hack-back instructions.

---

## Developer navigation (v2.7)

For source-code explanations, symbol-by-symbol responsibilities, and the feature-to-code map, see [`CODEBASE_GUIDE_V27.md`](CODEBASE_GUIDE_V27.md). For operational commands, see [`../TERMINAL_RUNBOOK.md`](../TERMINAL_RUNBOOK.md). For the current backlog, see [`../TODO.md`](../TODO.md).
