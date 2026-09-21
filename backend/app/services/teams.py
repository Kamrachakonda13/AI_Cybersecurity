"""Red / Blue team content + severity remediation playbooks (defensive only).

Help — structure and dependencies:
- `SEVERITY_PLAYBOOKS[CRITICAL|HIGH|MEDIUM|LOW]`: {answer, why, fix_steps[], verify}.
  Bands MUST match `severity()` in `services/risk.py` and `SEV_HELP` in the frontend.
- `CATEGORY_PLAYBOOKS[17 keys]`: per-shape fixes (kev, brute_force, ai_internet, eml…).
  The `category` query pattern in `GET /api/remediation` must list the same keys.
- `RED_TEAM` / `BLUE_TEAM`: doctrine + tool tables + AI techniques + exercises,
  served by `GET /api/teams/red|blue` and rendered by RedTeamView/BlueTeamView.
- Offensive tools are recognise-and-analyse intel only (no exploit instructions).

Everything here is hardening, detection and response guidance for systems you
own. No exploit instructions, no payloads, no C2 operation, no retaliation.
Offensive tools are listed so defenders recognise and analyse them — each entry
says what attackers use it for (one line), what it looks like from the defence,
and the governed lab use. Details that would help someone attack are omitted.
"""

SEVERITY_PLAYBOOKS = {
    "CRITICAL": {
        "answer": "Fix immediately (hours, not days). Validated exploit path likely exists.",
        "why": "Risk ≥ 80: internet reach + high CVSS and/or active exploitation (KEV) + "
               "sensitive data or privileged access combined.",
        "fix_steps": [
            "1. Contain first: restrict exposure (WAF rule / security-group / take admin path offline) — do not delete logs.",
            "2. Patch or mitigate: apply vendor fix; if no patch, disable the feature/path and add compensating control.",
            "3. Credential sweep: rotate secrets/tokens for affected service + review privileged sessions for the blast window.",
            "4. Verify: re-run assessment + check finding status flips to closed; keep audit trail.",
        ],
        "verify": "Re-assessment clean, exposure removed, no new anomalous sessions in 24h.",
    },
    "HIGH": {
        "answer": "Fix this cycle (days). Strong risk combo that becomes CRITICAL with one change.",
        "why": "Risk 60–79: e.g. exposed service with CVSS 7+, P5 identity without MFA, public cloud store.",
        "fix_steps": [
            "1. Reduce one big factor: remove internet exposure OR drop privilege OR enable MFA.",
            "2. Apply hardening: patch, least-privilege role, bucket/LB policy fix.",
            "3. Add detection: alert on anomalous sessions + high-risk flows to this asset.",
            "4. Verify: risk recompute drops below 60; review in next standup.",
        ],
        "verify": "Risk < 60 on recompute, control evidenced in audit log.",
    },
    "MEDIUM": {
        "answer": "Harden soon (sprint). Real weakness, no full exploit chain yet.",
        "why": "Risk 35–59: missing headers, anomalous session, macro-capable doc, suspicious DNS.",
        "fix_steps": [
            "1. Apply the cheap fix: add header, block macro, tighten scope, confirm DNS verdict.",
            "2. Confirm no escalation: check related flows/logins for the same entity.",
            "3. Schedule the durable fix (policy-as-code / baseline update).",
        ],
        "verify": "Posture check passes; no correlated failed logins in 7d.",
    },
    "LOW": {
        "answer": "Hygiene — fix opportunistically, track to zero.",
        "why": "Risk < 35: banner disclosure, minor misconfig, parsed-clean artifact.",
        "fix_steps": [
            "1. Suppress the signal: minimise banner, set header, document exception if accepted.",
            "2. Batch with nearby work; close with evidence link.",
        ],
        "verify": "Finding closed with evidence; exception recorded if accepted.",
    },
}

CATEGORY_PLAYBOOKS = {
    "exposure": {"answer": "Asset is internet-reachable.",
                 "fix_steps": ["Confirm business need; if none, remove public IP/port-forward.",
                               "Else front with WAF + allowlist, keep Security Graph path reviewed."],
                 "verify": "Exposure tile count drops; attack-path shortens."},
    "kev": {"answer": "Vulnerability is on CISA KEV (actively exploited).",
            "fix_steps": ["Patch now per vendor advisory; if unpatchable, disable/shield the vector.",
                          "Hunt: same indicator across assets (threat-intel view)."],
            "verify": "No KEV-flagged open findings."},
    "privilege": {"answer": "P4–P5 identity can reach sensitive workloads.",
                  "fix_steps": ["Apply least privilege: split admin vs daily role; scope service account to named APIs.",
                                "Require MFA (human) / workload identity (service); review quarterly."],
                  "verify": "Privileged tile drops; sessions show expected auth methods."},
    "mfa": {"answer": "MFA missing on capable account.",
            "fix_steps": ["Enforce MFA/SSO; break-glass account goes in vault with alerting."],
            "verify": "Identity view shows MFA enabled."},
    "cloud_public": {"answer": "Cloud resource publicly reachable with risky config.",
                     "fix_steps": ["Set Block-Public-Access / private endpoint; fix cited misconfiguration (IaC).",
                                   "Add CSPM check (Prowler/Trivy) to CI."],
                     "verify": "Cloud view shows INTERNAL; rescan clean."},
    "ai_internet": {"answer": "AI app/agent exposed; tool + data egress surface.",
                    "fix_steps": ["Put gateway behind auth; allowlist tools; cap retrieval scope to tenant data.",
                                  "Add output guardrail (PII/secret redaction) + approval for high-impact actions."],
                    "verify": "AI inventory shows internal or guarded exposure; retrieval audit clean."},
    "headers": {"answer": "Security headers missing (HSTS/CSP/X-Frame…).",
                "fix_steps": ["Add HSTS (https only), CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy."],
                "verify": "Header score 100 on re-assess."},
    "banner": {"answer": "Server banner discloses stack/version.",
               "fix_steps": ["Set ServerTokens Prod / minimal banner; hide version in errors."],
               "verify": "Banner finding gone on re-assess."},
    "plaintext_http": {"answer": "Plaintext HTTP in use.",
                       "fix_steps": ["Redirect http→https, enable HSTS, close port 80 where possible."],
                       "verify": "Assessment shows https + HSTS present."},
    "brute_force": {"answer": "≥5 failed logins: brute-force/password-spray candidate.",
                    "fix_steps": ["Confirm IP ownership; rate-limit + alert; force MFA; lock targeted accounts per policy.",
                                  "Rotate creds if any success interleaved; preserve logs."],
                    "verify": "No new fails from IP in 24h; MFA enforced."},
    "unexpected_port": {"answer": "Service not in baseline (drift or backdoor).",
                        "fix_steps": ["Identify owner/process; kill unauthorised listener, remove persistence, re-baseline."],
                        "verify": "Ports view shows EXPECTED only."},
    "high_flow": {"answer": "High-risk flow (volume/destination).",
                  "fix_steps": ["Confirm business need; block/allowlist destination; inspect endpoint for the process."],
                  "verify": "Flow risk < 50 or allowlisted with ticket."},
    "anomaly_session": {"answer": "Anomalous/privileged session.",
                        "fix_steps": ["Step-up auth; revoke session; review actions in audit during window."],
                        "verify": "Anomaly decays; auth method expected."},
    "macro": {"answer": "Document macro (vbaProject.bin).",
              "fix_steps": ["Never enable; block macros by policy; rebuild doc without code."],
              "verify": "Re-upload shows no macro flag."},
    "pdf": {"answer": "PDF active content (JS/OpenAction/embedded).",
            "fix_steps": ["Open only in sandboxed reader; extract text statically; regenerate clean PDF."],
            "verify": "Re-upload shows no active-content flag."},
    "pcap": {"answer": "Capture contains suspicious domain/flow shape.",
             "fix_steps": ["Block domain at DNS/proxy (your infra); hunt same domain in DNS view; isolate host if beaconing."],
             "verify": "No further hits to domain in 7d."},
    "eml": {"answer": "Phishing-shaped email.",
            "fix_steps": ["Report via mail gateway; never click; verify sender out-of-band; purge siblings by Message-ID."],
            "verify": "Gateway verdict recorded; users notified if it reached inbox."},
}

RED_TEAM = {
    "mission": "Emulate the attacker against lab targets ONLY, so blue can rehearse. Written scope + approval for every run.",
    "rules": ["Lab hostnames only (vulnerable-web, *.lab, localhost). Never external.",
              "Passive/safe checks from VEYRA; heavier tools only in isolated lab with approval.",
              "Stop on first unintentional impact; log everything as audit notes.",
              "Hand every finding to blue with evidence — the goal is detection, not damage."],
    "tool_families": [
        {"name": "Nmap / Masscan", "use": "Attackers map ports/services.",
         "lab": "Service discovery vs vulnerable-web; results reconciled with /api/network/ports baseline.",
         "spot": "UNEXPECTED port rows + connection bursts in flows."},
        {"name": "Nuclei / Nikto / OWASP ZAP", "use": "Template/proxy web checks.",
         "lab": "Safe header/TLS templates via VEYRA assessment; full scans only approved + isolated.",
         "spot": "Header/banner findings + robots/admin probing in audit."},
        {"name": "Burp Suite (manual proxy)", "use": "Inspect/modify own lab traffic.",
         "lab": "Route lab browser via proxy; export findings for import — no active scan from UI.",
         "spot": "Repeated /admin?id=… style probing from one IP."},
        {"name": "sqlmap / Hydra (lab creds)", "use": "Injection + login guessing in attacks.",
         "lab": "Only against seeded lab accounts with approval; every run pre-registered as an exercise.",
         "spot": "Login summary candidate + WAF/validation findings."},
        {"name": "Metasploit / Cobalt Strike / Meterpreter", "use": "Real adversaries' exploitation + C2 (NOT used here).",
         "lab": "DISABLED in VEYRA. Study indicators (process, beacon DNS) so blue can recognise them.",
         "spot": "Reverse-shell forensics flags + beacon-like DNS + privileged sessions."},
        {"name": "Mimikatz / BloodHound / NetExec", "use": "Credential theft + AD mapping in intrusions.",
         "lab": "Discuss indicators only; never run against real directories.",
         "spot": "lsass/sekurlsa keyword flags + P5 session anomalies."},
        {"name": "John / Hashcat", "use": "Offline password cracking of stolen hashes.",
         "lab": "Crack only lab-generated hashes you own to teach password policy.",
         "spot": "Spray-then-crack shows as login candidates first."},
        {"name": "Ghidra / radare2 / binwalk", "use": "Dissect captured malware (your copy).",
         "lab": "Analyse quarantined lab samples on workstation; API gives header/string hints.",
         "spot": "PE/ELF forensics flags + suspicious-import rules."},
    ],
    "ai_techniques": [
        "Prompt-injection drills vs lab AI gateway (/ai/chat): confirm injection is logged, not executed.",
        "Tool-permission review: which agent can reach the vector store? (AI inventory + graph retrieves edges).",
        "Retrieval-scope test: can lab agent read another tenant's docs? Must fail — fix scope.",
        "Guardrail eval: HSTS-like equivalent — output redaction + approval boundary for high-impact actions.",
    ],
    "exercises": ["Posture sweep (approval gate) → hand findings to blue.",
                  "Spray vs lab accounts (pre-registered) → confirm candidate fires.",
                  "Craft benign + malicious samples → confirm forensics flags differ."],
}

BLUE_TEAM = {
    "mission": "Detect, contain and recover on YOUR estate using VEYRA evidence. Human approval before high-impact response.",
    "tools": [
        {"name": "VEYRA Security Graph", "use": "Internet→data paths, port/process ownership, identity reach."},
        {"name": "SIEM (Splunk/Elastic) forwarding", "use": "Audit + findings export for retention and correlation."},
        {"name": "IDS/NSM (Suricata/Zeek/Snort)", "use": "Flow + DNS telemetry feeding ingest endpoints."},
        {"name": "EDR + firewall/WAF", "use": "Contain host, block IP/domain at YOUR perimeter."},
        {"name": "CSPM (Wiz/Prowler/Scout) + IaC (Trivy/Checkov)", "use": "Close cloud_public findings in code."},
        {"name": "Vault + MFA/SSO", "use": "Fix privilege/mfa findings; break-glass with alerting."},
        {"name": "Forensics (Volatility/Autopsy/Wireshark/Ghidra)", "use": "Workstation deep-dives; VEYRA gives static triage."},
        {"name": "AI guardrails (NeMo-style policy, output redaction)", "use": "Fix ai_internet findings; audit retrieval."},
    ],
    "techniques": ["Triage (severity playbooks) → Contain (revoke/block at own perimeter) → "
                   "Eradicate (patch/remove) → Recover (verify) → Lessons (baseline/IaC update).",
                   "Hunt with graph answers: internet_to_data, connection_owner, privileged_access.",
                   "Track MTTR per severity in Governance; exceptions recorded with expiry."],
    "ai_defense": ["Auth on AI gateway; tool allowlists; tenant-scoped retrieval; PII/secret redaction; "
                   "approval for writes/escalations; prompt-injection logging + retrieval audit."],
}
