"""MITRE ATT&CK knowledge + finding coverage (defensive correlation).

Help — design, dependencies:
- `TECHNIQUES`: curated in-code knowledge base (14 enterprise techniques with
  tactic + defender spotting notes, plus 2 MITRE ATLAS *concepts* clearly
  labelled — never fake ATT&CK IDs). No network, no downloads: works offline.
- `map_finding(f)`: pure rule mapper from a finding dict
  {title, severity, kev, exposure, cvss} → technique-ID list. Rules: kev→T1190,
  exposure→T1595, privilege/identity words→T1078, brute/login words→T1110,
  cloud/bucket→T1530, exfil/flow/volume→T1041, ransom→T1486, AI/agent/prompt→
  ATLAS concepts, unexpected service→T1543, missing headers/TLS→T1557.
- `coverage(db)`: maps every `Finding` row, returns per-technique counts +
  unmapped count. Read-only. Served by `GET /api/mitre/coverage`;
  `GET /api/mitre/techniques` returns the base. Consumed by the Ops MITRE panel.
"""
TECHNIQUES = [
    {"id": "T1595", "name": "Active Scanning", "tactic": "Reconnaissance",
     "description": "Adversary probes internet-facing services to find entry points.",
     "spot": "External-exposure findings; scan bursts in flows; /admin probing in audit."},
    {"id": "T1190", "name": "Exploit Public-Facing Application", "tactic": "Initial Access",
     "description": "Exploiting internet-facing software — the KEV kill chain.",
     "spot": "KEV-flagged CRITICAL findings on exposed assets."},
    {"id": "T1133", "name": "External Remote Services", "tactic": "Persistence",
     "description": "Legitimate remote access abused for persistence.",
     "spot": "Unexpected remote services (SSH/RDP) + odd-hour sessions."},
    {"id": "T1078", "name": "Valid Accounts", "tactic": "Persistence",
     "description": "Stolen or over-privileged accounts used as foothold.",
     "spot": "P4–P5 identities, missing MFA, anomalous privileged sessions."},
    {"id": "T1110", "name": "Brute Force", "tactic": "Credential Access",
     "description": "Password spraying / guessing against logins.",
     "spot": "Login-summary candidates (≥5 fails); spray across many users from one IP."},
    {"id": "T1046", "name": "Network Service Discovery", "tactic": "Discovery",
     "description": "Mapping internal services after initial access.",
     "spot": "Lateral flows to many ports; port-ownership anomalies."},
    {"id": "T1018", "name": "Remote System Discovery", "tactic": "Discovery",
     "description": "Finding reachable hosts for lateral movement.",
     "spot": "One host touching many internal IPs in flows/DNS."},
    {"id": "T1059", "name": "Command and Scripting Interpreter", "tactic": "Execution",
     "description": "Running shells/scripts (bash, PowerShell) on target.",
     "spot": "Reverse-shell forensics flags; shells spawned by services."},
    {"id": "T1543", "name": "Create or Modify System Process", "tactic": "Persistence",
     "description": "Rogue services / startup persistence.",
     "spot": "UNEXPECTED service rows (baseline drift)."},
    {"id": "T1005", "name": "Data from Local System", "tactic": "Collection",
     "description": "Staging sensitive local files for theft.",
     "spot": "DLP secret events; mass reads on data hosts."},
    {"id": "T1530", "name": "Data from Cloud Storage", "tactic": "Collection",
     "description": "Grabbing data from buckets/vaults.",
     "spot": "Public cloud findings; CloudTrail-style access anomalies."},
    {"id": "T1041", "name": "Exfiltration Over C2 Channel", "tactic": "Exfiltration",
     "description": "Large/regular outbound transfers to attacker infra.",
     "spot": "High-risk flows (≥70); suspicious DNS TLDs."},
    {"id": "T1557", "name": "Adversary-in-the-Middle", "tactic": "Credential Access",
     "description": "Downgrade/strip protections (plaintext HTTP, missing HSTS).",
     "spot": "Plaintext-HTTP + missing-HSTS posture findings."},
    {"id": "T1486", "name": "Data Encrypted for Impact", "tactic": "Impact",
     "description": "Ransomware-style encryption/extortion.",
     "spot": "Ransom-keyword forensics flags; mass file renames (DLP)."},
    {"id": "ATLAS-PromptInjection", "name": "LLM Prompt Injection (ATLAS concept)", "tactic": "ML Attack Staging",
     "description": "MITRE ATLAS concept: crafted input steering model behaviour.",
     "spot": "Injection patterns in lab AI logs; retrieval of out-of-scope docs."},
    {"id": "ATLAS-DataExtraction", "name": "LLM Data Extraction (ATLAS concept)", "tactic": "ML Attack Staging",
     "description": "MITRE ATLAS concept: extracting training/retrieval data via prompts.",
     "spot": "Cross-tenant retrieval denials; exfil-shaped AI flows."},
]
_BY_ID = {t["id"]: t for t in TECHNIQUES}


def map_finding(f: dict) -> list[str]:
    """Map one finding {title, severity, kev, exposure, cvss} → technique IDs (ordered, deduped)."""
    title = str(f.get("title", "")).lower()
    out: list[str] = []
    if f.get("kev"):
        out.append("T1190")
    if f.get("exposure"):
        out.append("T1595")
    if any(w in title for w in ("privileg", "mfa", "identity", "account", "service account")):
        out.append("T1078")
    if any(w in title for w in ("brute", "spray", "login", "password", "credential")):
        out.append("T1110")
    if any(w in title for w in ("cloud", "bucket", "storage", "vault")):
        out.append("T1530")
    if any(w in title for w in ("exfil", "flow", "transfer", "volume", "beacon", "dns")):
        out.append("T1041")
    if any(w in title for w in ("ransom", "encrypt", "extort")):
        out.append("T1486")
    if any(w in title for w in ("ai ", "ai-", "agent", "prompt", "rag", "vector", "llm", "model")):
        out += ["ATLAS-PromptInjection", "ATLAS-DataExtraction"]
    if any(w in title for w in ("unexpected", "backdoor", "rogue service", "persistence")):
        out.append("T1543")
    if any(w in title for w in ("header", "hsts", "plaintext", "http", "tls", "banner")):
        out.append("T1557")
    if any(w in title for w in ("remote", "ssh", "rdp", "admin panel", "exposed")):
        out.append("T1133")
    seen, deduped = set(), []
    for t in out:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped


def coverage(db) -> dict:
    """Map every Finding row → techniques. Returns {techniques:[{…count}], unmapped, findings}."""
    from ..models import Finding
    counts: dict[str, int] = {}
    unmapped = 0
    rows = db.query(Finding).all()
    for fin in rows:
        tids = map_finding({"title": fin.title, "severity": fin.severity,
                            "kev": fin.kev, "exposure": fin.exposure, "cvss": fin.cvss})
        if not tids:
            unmapped += 1
        for t in tids:
            counts[t] = counts.get(t, 0) + 1
    techs = [{**_BY_ID[tid], "findings": counts[tid]} for tid in sorted(counts)]
    return {"techniques": techs, "unmapped": unmapped, "findings": len(rows)}
