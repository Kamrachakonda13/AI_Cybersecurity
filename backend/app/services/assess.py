"""AegisX v1.2 authorized assessment service — SAFE subset only.

Safety boundary (deliberate):
- NO port scanning of arbitrary hosts, NO exploitation (Metasploit), NO active
  Burp/Nuclei payload injection, NO arbitrary shell, NO credential brute force.
- Only passive/low-impact web-posture checks over HTTPS/HTTP with short timeouts:
  security headers, TLS presence, server/tech disclosure, robots/sitemap hints.
- Target must be an explicit http(s) URL; blocked: non-http schemes, userinfo in
  URL, cloud metadata IP (169.254.169.254), loopback is allowed ONLY for lab use
  and is flagged. Private-range targets require approval_required=True handling
  (job stays pending_approval, no fetch performed).
- Rate limited in-memory (per-target cooldown), all jobs audit-logged.

This gives "vulnerability assessment on any URL" for posture issues while the
offensive tooling (Nmap/Nuclei/Metasploit/Burp) is represented as governed
connectors in TOOL_CATALOG, executed only in an isolated authorized lab —
not from the browser.
"""
import ipaddress
import time
from urllib.parse import urlparse

import httpx

TOOL_CATALOG = [
    {"name": "Nmap (governed connector)", "category": "offensive/network",
     "maps_to": "Asset discovery + /api/network/ports + Security Graph",
     "safety": "Runs only in isolated lab with written scope; browser triggers approval job, never raw scan."},
    {"name": "Nuclei (governed templates)", "category": "offensive/web",
     "maps_to": "Findings pipeline (safe header/TLS templates in v1.2)",
     "safety": "Only non-intrusive templates; intrusive ones need approval + lab isolation."},
    {"name": "Burp Suite (workflow import)", "category": "offensive/web",
     "maps_to": "Import findings -> /api/ingest/findings (planned)",
     "safety": "No active scan from UI; import scan files after authorized test."},
    {"name": "Metasploit (validation only)", "category": "offensive/validation",
     "maps_to": "AuditEvent only — exploit execution is DISABLED in this platform",
     "safety": "Disabled. Records manual validation notes, never launches exploits."},
    {"name": "Garak / Prompt-injection probes", "category": "ai-security",
     "maps_to": "AIAsset risk + approval_boundary",
     "safety": "Probes run against lab AI gateway with red-team approval."},
    {"name": "NeMo Guardrails policy check", "category": "ai-security",
     "maps_to": "AI investigation advisory mode",
     "safety": "Policy-as-data; no model weights touched."},
    {"name": "Prowler / Scout Suite", "category": "cloud",
     "maps_to": "/api/cloud/resources posture inventory",
     "safety": "Read-only CSPM polling with scoped IAM role."},
    {"name": "Trivy / Checkov", "category": "cloud/supply-chain",
     "maps_to": "Findings (container/IaC) — adapter stub in v1.2",
     "safety": "Scans repo/image refs in CI, not prod from browser."},
    {"name": "Wireshark / Zeek / Suricata signals", "category": "network/defense",
     "maps_to": "/api/ingest/network-flows ingestion",
     "safety": "Telemetry ingest only; no packet capture from UI."},
    {"name": "Splunk / Elastic SIEM forwarding", "category": "defense/siem",
     "maps_to": "/api/audit + findings export",
     "safety": "Outbound webhook with scoped token (planned)."},
    {"name": "HashiCorp Vault", "category": "defense/secrets",
     "maps_to": "Secret refs for connectors (env, never in DB)",
     "safety": "App reads secrets from env; no secret material in API."},
{"name": "Masscan / RustScan / Naabu", "category": "offensive/network",
     "maps_to": "Approved exposure discovery imports",
     "safety": "Lab or explicitly authorized scope; results imported as evidence."},
    {"name": "Amass / Subfinder / Assetfinder / DNSx", "category": "reconnaissance",
     "maps_to": "Approved external-attack-surface inventory",
     "safety": "Scope-bound discovery only; no arbitrary targets."},
    {"name": "OWASP ZAP / Nikto / Gobuster / Feroxbuster / FFUF / Dirsearch", "category": "offensive/web",
     "maps_to": "Web/API assessment result adapters",
     "safety": "Active testing only in isolated approved assessment workers."},
    {"name": "OpenVAS / Greenbone / Nessus-compatible imports", "category": "vulnerability-management",
     "maps_to": "Normalized Findings pipeline",
     "safety": "Import approved scan results; scanner execution remains governed."},
    {"name": "Semgrep / Bandit / CodeQL SARIF / dependency scanners", "category": "application-security",
     "maps_to": "Code and dependency findings",
     "safety": "CI/repository scans; no production mutation."},
    {"name": "Trivy / Grype / Syft / Checkov / Terrascan", "category": "supply-chain",
     "maps_to": "Container, SBOM and IaC findings",
     "safety": "Prefer CI artifacts and read-only registries."},
    {"name": "BloodHound / NetExec / Impacket / Certipy / Kerbrute", "category": "identity-assessment",
     "maps_to": "Identity graph and privilege-path evidence",
     "safety": "Authorized directory assessment only; credential attack workflows disabled."},
    {"name": "Hashcat / John / Hydra / Medusa", "category": "credential-audit",
     "maps_to": "Password-policy/audit result imports",
     "safety": "Catalogued for authorized audit work; no browser-based credential attacks."},
    {"name": "Zeek / Suricata / Snort / Wireshark / tshark / tcpdump", "category": "network-detection",
     "maps_to": "Flow, DNS, protocol and detection telemetry",
     "safety": "Own sensors/captures only; no packet capture initiated by browser."},
    {"name": "Sysmon / osquery / Velociraptor / Wazuh-compatible events", "category": "endpoint-detection",
     "maps_to": "Endpoint process, file, registry and authentication telemetry",
     "safety": "Managed endpoints only with agent authorization."},
    {"name": "Volatility / Autopsy / Sleuth Kit / Hayabusa / Chainsaw", "category": "dfir",
     "maps_to": "Forensic evidence imports and timeline reconstruction",
     "safety": "Analyze forensic copies; preserve chain of custody."},
    {"name": "YARA / ClamAV / capa / Ghidra / radare2 / Rizin / IDA", "category": "malware-analysis",
     "maps_to": "Static-analysis evidence and reverse-engineering annotations",
     "safety": "Samples handled in isolated analyst/sandbox environments; API never executes samples."},
    {"name": "Kubescape / kube-bench / kube-hunter / Falco", "category": "kubernetes-security",
     "maps_to": "Cluster posture and runtime findings",
     "safety": "Read-only posture by default; active tests only in lab."},
    {"name": "Prowler / Scout Suite / CloudSploit", "category": "cloud-posture",
     "maps_to": "CSPM inventory and Findings",
     "safety": "Read-only scoped cloud roles."},
    {"name": "Garak / Promptfoo / OWASP GenAI tests", "category": "ai-security",
     "maps_to": "AIAsset evaluation and regression findings",
     "safety": "Lab/private AI targets + approval; no third-party probing."},
    {"name": "MISP / STIX-TAXII / Sigma / YARA rule feeds", "category": "threat-intelligence",
     "maps_to": "IOC, detection and threat-intelligence enrichment",
     "safety": "Inbound intelligence is treated as untrusted data and validated before use."},
    {"name": "MCP / A2A security adapters", "category": "agent-security",
     "maps_to": "Agent/tool inventory, policy decisions and inter-agent telemetry",
     "safety": "Tool calls are capability-scoped and approval-gated; no autonomous privilege expansion."},
    {"name": "OpenTelemetry", "category": "ai-observability",
     "maps_to": "LLM, tool, retrieval, memory and approval traces",
     "safety": "Telemetry only; secrets and sensitive payloads require redaction policies."},
]

_LAST_RUN: dict[str, float] = {}
COOLDOWN_SECONDS = 30

BLOCKED_IPS = {"169.254.169.254"}

# Secure local lab allowlist — ONLY these non-IP hostnames are treated as lab targets.
# Everything else non-IP is treated as public internet (still passive-checks only).
LAB_HOSTS = {"vulnerable-web", "localhost", "lab-vulnerable-web"}


def is_lab_host(host: str) -> bool:
    """True for lab-only hostnames (`LAB_HOSTS`, `*.lab`). Lab hosts are treated as private → approval gate applies."""
    h = host.lower()
    return h in LAB_HOSTS or h.endswith(".lab") or h.endswith(".lab.local")


def validate_target(url: str) -> dict:
    """Validate an assessment target. Returns {host, private, scheme, lab} or raises ValueError.

    Rejects: non-http(s) schemes, userinfo URLs, cloud-metadata IP. `private`
    forces the approval gate in `POST /api/assessments/web`; `lab` adds the lab hint.
    """
    try:
        p = urlparse(url.strip())
    except Exception as e:
        raise ValueError(f"Unparseable URL: {e}")
    if p.scheme not in ("http", "https"):
        raise ValueError("Only http(s) URLs are assessed")
    if not p.hostname:
        raise ValueError("URL must include a hostname")
    if "@" in (p.netloc or "") and p.username:
        raise ValueError("Userinfo in URL is not allowed")
    host = p.hostname
    if host in BLOCKED_IPS:
        raise ValueError("Cloud metadata endpoints are never assessed")
    lab = is_lab_host(host)
    private = lab
    try:
        ip = ipaddress.ip_address(host)
        private = ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        h = host.lower()
        if not lab:
            private = h in ("localhost",) or h.endswith(".local") or h.endswith(".internal")
    return {"host": host, "private": private, "scheme": p.scheme, "lab": lab}


def check_cooldown(target: str):
    """In-memory per-host rate limit (`COOLDOWN_SECONDS`). Raises ValueError when too soon; called by the web-assessment route before fetching."""
    now = time.time()
    last = _LAST_RUN.get(target, 0)
    if now - last < COOLDOWN_SECONDS:
        raise ValueError(f"Rate limited: retry in {int(COOLDOWN_SECONDS - (now - last))}s")
    _LAST_RUN[target] = now


SECURITY_HEADERS = ["strict-transport-security", "content-security-policy",
                    "x-frame-options", "x-content-type-options",
                    "referrer-policy", "permissions-policy"]


def score_headers(headers: dict) -> dict:
    """Score 6 security headers → {score 0–100, present[], missing[]}. Pure function; each missing header becomes a finding in `assess_web_posture`."""
    present = [h for h in SECURITY_HEADERS if h in {k.lower() for k in headers}]
    missing = [h for h in SECURITY_HEADERS if h not in {k.lower() for k in headers}]
    score = round(100 * len(present) / len(SECURITY_HEADERS), 1)
    return {"score": score, "present": present, "missing": missing}


async def assess_web_posture(url: str) -> dict:
    """Passive fetch (single GET, 8s timeout, no payloads) + header/TLS/banner/robots heuristics.

    Depends on: `httpx`, `score_headers`. Returns findings with MEDIUM for missing
    HSTS/CSP, LOW for other headers/banner, HIGH for plaintext HTTP. Called only
    after `validate_target` + approval gate + `check_cooldown` pass in the route.
    """
    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, max_redirects=3,
                                 headers={"User-Agent": "AegisX-PostureCheck/1.2 (authorized assessment)"}) as c:
        r = await c.get(url)
        headers = dict(r.headers)
        hs = score_headers(headers)
        findings = []
        for h in hs["missing"]:
            findings.append({"severity": "MEDIUM" if h in ("strict-transport-security", "content-security-policy") else "LOW",
                             "title": f"Missing security header: {h}",
                             "detail": "Posture hardening — no exploit payload was sent."})
        server = headers.get("server", "")
        if server:
            findings.append({"severity": "LOW", "title": f"Server banner discloses: {server[:80]}",
                             "detail": "Consider minimizing banner disclosure."})
        if url.startswith("http://"):
            findings.append({"severity": "HIGH", "title": "Plaintext HTTP (no TLS)",
                             "detail": "URL uses http; enforce https + HSTS."})
        try:
            robots = await c.get(url.rstrip("/") + "/robots.txt")
            robots_hint = robots.status_code == 200
        except Exception:
            robots_hint = False
        return {"final_url": str(r.url), "http_status": r.status_code,
                "https": str(r.url).startswith("https://"),
                "header_score": hs["score"], "headers_present": hs["present"],
                "headers_missing": hs["missing"], "server": server,
                "robots_txt": robots_hint, "findings": findings}
