"""Per-tool guided run forms (Kali-style UX without a browser shell).

Each registered tool gets a parameter schema the console renders as a guided
form (dropdowns + text fields). Schemas intentionally use *named profiles*,
never raw shell flags: the API only ever stages a governed job contract
(target + scope + params + approval) for an isolated worker. No command string
is accepted, stored, or executed by the API.

`get_form(tool)` merges the category default with any tool-specific override.
`build_contract_fields(tool, params)` folds submitted values into the
(target, scope, params) triple used by the job endpoints and raises
ValueError on policy violations (e.g. non-scanner Metasploit modules).
"""
from __future__ import annotations

ENVIRONMENTS = ["lab", "approved_worker"]


def _base(extra: list[dict] | None = None) -> list[dict]:
    fields = [
        {"name": "target", "label": "Target", "type": "text", "required": True,
         "placeholder": "lab-web / 10.10.20.0/24 / https://lab-app/",
         "help": "Explicit in-scope target only (lab asset, owned host/CIDR, approved app)."},
        {"name": "scope", "label": "Scope (comma separated)", "type": "textarea", "required": True,
         "placeholder": "lab-web, 10.10.20.17",
         "help": "Every asset/network this run may touch. Out-of-scope = rejected."},
    ]
    if extra:
        fields.extend(extra)
    fields.extend([
        {"name": "environment", "label": "Execution environment", "type": "select",
         "options": ENVIRONMENTS, "default": "lab", "required": True,
         "help": "Isolated lab, or an approved worker. The API never executes tools itself."},
        {"name": "purpose", "label": "Purpose", "type": "text", "required": True,
         "default": "Authorized security assessment",
         "help": "Why this run is authorized (change ticket, exercise name)."},
        {"name": "approval_ticket", "label": "Approval ticket", "type": "text", "required": False,
         "placeholder": "CHG-1234 (sudo runs skip this — approval is implicit)",
         "help": "Non-sudo runs require a ticket; sudo approval is automatic."},
    ])
    return fields


PROFILE = lambda label, options, default=None, help="": {
    "name": "profile", "label": label, "type": "select",
    "options": options, "default": default or options[0], "required": True, "help": help}

CATEGORY_FORMS: dict[str, list[dict]] = {
    "Network Discovery": _base([PROFILE("Scan profile",
        ["Host discovery", "Quick port sweep", "Service versions", "OS fingerprint", "Vulnerability scripts"],
        help="Named capability set — the worker maps this to its approved tool flags.")] + [
        {"name": "ports", "label": "Ports (optional)", "type": "text", "required": False,
         "placeholder": "80,443 or 1-1024", "help": "Leave blank for the profile default."}]),
    "Attack Surface": _base([PROFILE("Collection profile",
        ["Passive first", "DNS validation", "HTTP inventory", "Full surface map"])]),
    "Web/API": _base([
        {"name": "target_url", "label": "Target URL", "type": "text", "required": True,
         "placeholder": "http://vulnerable-web:4101/",
         "help": "Authorized application URL. Duplicated into target/scope for the contract."},
        PROFILE("Assessment profile",
        ["Passive mapping", "Safe active checks", "Content discovery", "Full assessment"],
        help="Safe checks only; intrusive modules stay disabled by worker policy.")]),
    "Exploit Validation": _base([PROFILE("Validation profile",
        ["Dry-run plan only", "Scanner modules only", "Supervised validation"],
        help="Exploit/payload execution is never staged from the console.")]),
    "Identity/Network": _base([PROFILE("Assessment profile",
        ["Read-only enumeration", "Attack-path modeling", "Supervised validation"])]),
    "Identity": _base([PROFILE("Assessment profile",
        ["Trust-path modeling", "Privilege mapping", "Supervised validation"])]),
    "Credential Audit": _base([
        {"name": "dataset_ref", "label": "Authorized dataset reference", "type": "text", "required": True,
         "placeholder": "AUDIT-2026-014 (offline hash set — never a live login)",
         "help": "Reference to an offline, authorized audit dataset. The console never accepts passwords."},
        PROFILE("Audit profile", ["Hash strength audit", "Policy compliance check"])]),
    "Network Defense": _base([
        {"name": "interface", "label": "Capture interface / sensor", "type": "text", "required": False,
         "placeholder": "eth0 (own network/sensor only)"},
        {"name": "capture_filter", "label": "Capture filter (BPF)", "type": "text", "required": False,
         "placeholder": "tcp port 443",
         "help": " Berkeley-packet-filter expression evaluated by the worker."},
        {"name": "duration_seconds", "label": "Duration (seconds)", "type": "number", "required": False,
         "default": 60, "help": "Bounded capture window."}]),
    "Vulnerability": _base([PROFILE("Scan profile",
        ["Discovery", "Standard assessment", "Compliance audit"])]),
    "Cloud/Container": _base([
        {"name": "artifact", "label": "Image / path / SBOM", "type": "text", "required": True,
         "placeholder": "registry/org/app:1.4 or ./sbom.json"},
        PROFILE("Severity threshold", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])]),
    "AppSec": _base([
        {"name": "repo_ref", "label": "Repository / path", "type": "text", "required": True,
         "placeholder": "git@org/repo @ commit (CI checkout)"},
        PROFILE("Rule pack", ["Security audit", "OWASP Top 10", "Secrets scan"])]),
    "IaC": _base([
        {"name": "repo_ref", "label": "Terraform / manifest path", "type": "text", "required": True,
         "placeholder": "./infra/"},
        PROFILE("Policy pack", ["CIS baseline", "Public-exposure focus", "Secrets focus"])]),
    "Cloud": _base([PROFILE("Assessment profile",
        ["Read-only inventory", "Exposure review", "Privilege review"],
        help="Cloud connectors are read-only; changes go through change control.")]),
    "Kubernetes": _base([PROFILE("Assessment profile",
        ["CIS benchmark", "Posture review", "Runtime anomaly review"])]),
    "Endpoint": _base([
        {"name": "query_pack", "label": "Query pack / check", "type": "text", "required": False,
         "placeholder": "startup-items, listening-ports",
         "help": "Telemetry queries for managed endpoints — never remote execution."}]),
    "DFIR": _base([
        {"name": "artifact_ref", "label": "Evidence artifact reference", "type": "text", "required": True,
         "placeholder": "CASE-014 mem image sha256:… (analyzed copies only)",
         "help": "Hashes of authorized evidence copies; originals stay preserved."},
        PROFILE("Analysis profile", ["Triage", "Timeline", "Deep dive"])]),
    "Malware": _base([
        {"name": "artifact_ref", "label": "Sample reference (hash)", "type": "text", "required": True,
         "placeholder": "sha256:… (isolated analysis worker only)"},
        PROFILE("Analysis profile", ["Static triage", "Capabilities", "Full static"])]),
    "Reverse Engineering": _base([
        {"name": "artifact_ref", "label": "Sample reference (hash)", "type": "text", "required": True,
         "placeholder": "sha256:…"},
        PROFILE("Analysis profile", ["Strings + imports", "Control flow", "Full static"])]),
    "Firmware": _base([
        {"name": "artifact_ref", "label": "Firmware image reference", "type": "text", "required": True,
         "placeholder": "vendor-fw-1.4.bin (offline copy)"},
        PROFILE("Analysis profile", ["File inventory", "Embedded services", "Full review"])]),
    "Forensics": _base([
        {"name": "artifact_ref", "label": "Evidence reference", "type": "text", "required": True,
         "placeholder": "disk image / file set (authorized copy)"},
        PROFILE("Extraction profile", ["Metadata", "File carving", "Timeline"])]),
    "Threat Intelligence": _base([
        {"name": "feed", "label": "Feed / file reference", "type": "text", "required": True,
         "placeholder": "misp-event-8841 / iocs.csv"},
        PROFILE("Action", ["Normalize + correlate", "Enrich cases", "Publish internally"])]),
    "Detection Engineering": _base([
        {"name": "rule", "label": "Detection rule (Sigma/YAML)", "type": "textarea", "required": True,
         "placeholder": "title: …\ndetection: …",
         "help": "Portable rule text — tested against known telemetry, never live ammo."},
        PROFILE("Action", ["Validate", "Deploy to lab", "Measure coverage"])]),
    "AI Security": _base([
        {"name": "gateway", "label": "Lab gateway / model ref", "type": "text", "required": True,
         "placeholder": "http://lab-ai:4120 (lab/private + approval only)"},
        PROFILE("Evaluation profile", ["Prompt-injection battery", "Data-leakage battery", "Full red battery"])]),
}

# Flagship tools get Kali-flavoured, still-governed forms. Keys must match
# TOOL_REGISTRY names in services/admin_tools.py.
TOOL_FORMS: dict[str, list[dict]] = {
    "Nmap": _base([PROFILE("Scan profile",
        ["Host discovery", "Quick port sweep", "Service versions", "OS fingerprint", "Vulnerability scripts"],
        help="Kali equivalent, governed: host discovery → ping sweep; service versions → service detection; vulnerability scripts → safe vuln scripts. No raw flags leave the console.")] + [
        {"name": "ports", "label": "Ports (optional)", "type": "text", "required": False, "placeholder": "80,443 or 1-1024"},
        {"name": "timing", "label": "Timing template", "type": "select", "required": False,
         "options": ["Polite", "Normal", "Aggressive (lab only)"], "default": "Normal"}]),
    "Wireshark": _base([
        {"name": "interface", "label": "Interface / sensor", "type": "text", "required": True, "placeholder": "analyst workstation capture"},
        {"name": "capture_filter", "label": "Display/capture filter", "type": "text", "required": False, "placeholder": "http or dns"},
        {"name": "duration_seconds", "label": "Duration (seconds)", "type": "number", "required": False, "default": 120}]),
    "tcpdump": _base([
        {"name": "interface", "label": "Interface (own network)", "type": "text", "required": True, "placeholder": "eth0"},
        {"name": "capture_filter", "label": "BPF filter", "type": "text", "required": False, "placeholder": "tcp port 443"},
        {"name": "duration_seconds", "label": "Duration (seconds)", "type": "number", "required": False, "default": 60}]),
    "Metasploit Framework": _base([
        {"name": "module", "label": "Auxiliary scanner module", "type": "select", "required": True,
         "options": ["auxiliary/scanner/portscan/tcp", "auxiliary/scanner/http/http_version",
                     "auxiliary/scanner/smb/smb_version", "auxiliary/scanner/ssh/ssh_version"],
         "help": "Console offers scanner (auxiliary) modules only — exploit/payload modules are never staged from here."},
        PROFILE("Run mode", ["Dry-run plan only", "Supervised validation"])]),
    "Hydra": _base([
        {"name": "service", "label": "Service under test", "type": "select", "required": True,
         "options": ["ssh", "ftp", "http-post-form", "smb", "rdp"]},
        {"name": "username_ref", "label": "Authorized username list ref", "type": "text", "required": True,
         "placeholder": "LAB-USERS-03 (no live credentials in the console)"},
        {"name": "dataset_ref", "label": "Authorized credential-set ref", "type": "text", "required": True,
         "placeholder": "AUDIT-2026-014",
         "help": "Isolated-lab authentication testing against an authorized set. No passwords are entered here, ever."},
        PROFILE("Intensity", ["Single attempt (verify lockout)", "Supervised batch"])]),
    "Hashcat": _base([
        {"name": "dataset_ref", "label": "Offline hash-set reference", "type": "text", "required": True,
         "placeholder": "AUDIT-2026-014 (offline strength audit only)"},
        PROFILE("Audit profile", ["Fast audit", "Deep audit"])]),
    "John the Ripper": _base([
        {"name": "dataset_ref", "label": "Offline hash-set reference", "type": "text", "required": True,
         "placeholder": "AUDIT-2026-014 (offline strength audit only)"},
        PROFILE("Audit profile", ["Fast audit", "Deep audit"])]),
    "SQLMap": _base([
        {"name": "target_url", "label": "Authorized test URL", "type": "text", "required": True,
         "placeholder": "http://vulnerable-web:4101/item?id=1"},
        PROFILE("Assessment depth", ["Detect only", "Enumerate DBMS (supervised)", "Full assessment (supervised)"],
        help="Isolated-lab injection assessment with approval. No destructive payloads.")]),
    "Burp Suite": _base([
        {"name": "target_url", "label": "Authorized test app", "type": "text", "required": True,
         "placeholder": "http://vulnerable-web:4101/"},
        PROFILE("Engagement profile", ["Passive mapping", "Guided active checks (supervised)"])]),
    "OWASP ZAP": _base([
        {"name": "target_url", "label": "Authorized test app", "type": "text", "required": True,
         "placeholder": "http://vulnerable-web:4101/"},
        PROFILE("Scan profile", ["Baseline", "Full scan (supervised)"])]),
    "Nuclei": _base([
        {"name": "target_url", "label": "Target", "type": "text", "required": True,
         "placeholder": "http://vulnerable-web:4101/"},
        PROFILE("Template set", ["Safe templates", "Reviewed custom set"])]),
    "BloodHound": _base([PROFILE("Collection profile",
        ["Session collection (read-only)", "Trust-path modeling", "Privilege mapping"])]),
    "OpenVAS/Greenbone": _base([
        {"name": "target_url", "label": "Targets", "type": "text", "required": True, "placeholder": "lab-web, 10.10.20.17"},
        PROFILE("Scan config", ["Discovery", "Full and fast", "Compliance"])]),
    "Garak": _base([
        {"name": "gateway", "label": "Lab model gateway", "type": "text", "required": True, "placeholder": "http://lab-ai:4120"},
        PROFILE("Probe set", ["Prompt-injection battery", "Data-leakage battery", "Full red battery"])]),
    "YARA": _base([
        {"name": "artifact_ref", "label": "Sample/directory reference", "type": "text", "required": True, "placeholder": "quarantine/CASE-014/"},
        {"name": "rule", "label": "Rule pack reference", "type": "text", "required": False, "placeholder": "corp-yara-2026 (isolated analysis worker)"}]),
}

# Tools whose console surface is intentionally plan/request-only (no run profiles).
PLAN_ONLY_NOTE = ("This connector stages governed plans and evidence reviews from the "
                  "console; live operation happens in its own approved system.")


def get_form(tool: dict) -> dict:
    """Full runner schema for one registry tool dict."""
    name = tool.get("name", "")
    fields = TOOL_FORMS.get(name) or CATEGORY_FORMS.get(tool.get("category", "")) or _base([])
    return {"tool_id": tool.get("id", ""), "tool": name,
            "category": tool.get("category", ""), "purpose": tool.get("purpose", ""),
            "execution_profile": tool.get("execution_profile", ""),
            "access_tier": tool.get("access_tier", "admin"),
            "privileged_usage": bool(tool.get("privileged_usage")),
            "fields": fields,
            "note": PLAN_ONLY_NOTE if tool.get("execution_profile") in {
                "analyst_workstation", "sensor", "endpoint_agent",
                "approved_connector", "read_only_cloud"} else ""}


def build_contract_fields(tool: dict, params: dict) -> tuple[str, list[str], dict]:
    """Fold runner params into (target, scope, params). Raises ValueError on violations."""
    params = dict(params or {})
    name = tool.get("name", "")
    if name == "Metasploit Framework":
        module = str(params.get("module", ""))
        if not module.startswith("auxiliary/scanner/"):
            raise ValueError("Console stages scanner (auxiliary/) modules only")
    for key in ("target", "target_url", "artifact", "repo_ref", "gateway", "feed", "dataset_ref"):
        val = str(params.get(key, "")).strip()
        if val and key != "target":
            params.setdefault("target", val)
    target = str(params.get("target", "")).strip()
    if not target:
        raise ValueError("target is required")
    raw_scope = params.get("scope", target)
    scope = [x.strip() for x in str(raw_scope).split(",") if x.strip()] or [target]
    if len(scope) > 100:
        raise ValueError("scope must contain 1..100 entries")
    extra = {k: v for k, v in params.items()
             if k not in {"target", "scope", "environment", "purpose", "approval_ticket"} and str(v).strip() != ""}
    return target, scope, extra
