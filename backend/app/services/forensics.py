"""VEYRA lawful forensics & reverse-engineering — STATIC ANALYSIS ONLY.

Lawful-defensive scope:
- Analyze artifacts YOU own (lab binaries, quarantined attachments, local PCAP-derived
  logs) to understand how an outside attacker tried to get in.
- NEVER executes the sample, NEVER runs dynamic detonation, NEVER "hacks back".
  No payload delivery, no remote access, no credential use, no exploitation.
- Files are read in memory, size-capped, hashed, string-scanned and discarded.
  Every analysis is audit-logged with chain-of-custody fields (filename, sha256).

Kali tools are represented as governed mappings: the platform performs the safe
subset (hashes, strings, header/IOC heuristics); full tools (Ghidra, Volatility,
Wireshark, Autopsy) run on an analyst workstation against lab copies — not in
this API.
"""
import hashlib
import io
import re
import struct
import zipfile

MAX_BYTES = 5 * 1024 * 1024  # 5 MB hard cap

KALI_FORENSICS_CATALOG = [
    {"kali_tool": "sha256sum / hashdeep", "category": "identify",
     "veyra": "Hash + file-type header shown for every upload",
     "safety": "Read-only hashing. Safe."},
    {"kali_tool": "strings / binwalk -E", "category": "static-strings",
     "veyra": "Printable-string extraction (≥4 chars, capped sample)",
     "safety": "No execution. Safe."},
    {"kali_tool": "YARA / ClamAV", "category": "signatures",
     "veyra": "Built-in heuristic rules (suspicious keywords, reverse-shell patterns)",
     "safety": "String matching only — not a full AV verdict."},
    {"kali_tool": "Ghidra / radare2 / objdump", "category": "reverse-engineering",
     "veyra": "Header + section hints (ELF/PE); full disassembly happens on analyst workstation",
     "safety": "API never disassembles/executes; open copies in Ghidra locally."},
    {"kali_tool": "Wireshark / tshark / tcpdump", "category": "network-forensics",
     "veyra": "Map extracted IPs/URLs to Security Graph + flows (`/api/graph/answer?kind=connection_owner`)",
     "safety": "Analyze captures you own; never sniff third-party networks."},
    {"kali_tool": "Volatility / Autopsy / Sleuth Kit / foremost", "category": "host-disk-memory",
     "veyra": "Correlate hostname/user/process via Endpoint + Identity views",
     "safety": "Run against forensic IMAGES of your own lab hosts with write-blockers."},
    {"kali_tool": "exiftool / file", "category": "metadata",
     "veyra": "Magic-number type detection (ELF, PE, PDF, ZIP/APK/JAR, PNG, JPEG)",
     "safety": "Header read only. Safe."},
    {"kali_tool": "Metasploit / Burp-active / exploit-db", "category": "offensive-DISABLED",
     "veyra": "NOT exposed. Findings record what the attacker likely used; no replay.",
     "safety": "Disabled by design — analysis, not retaliation."},
]

SUSPICIOUS_KEYWORDS = [
    "mimikatz", "sekurlsa", "psexec", "powershell -enc", "powershell -e ",
    "cmd.exe /c", "/etc/shadow", "/etc/passwd", "chmod +x", "curl | sh",
    "wget | sh", "nc -e", "/bin/bash -i", "reverse shell", "meterpreter",
    "cobalt strike", "beacon", "ransom", "decrypt your files", "all your files",
]

REVERSE_SHELL_RES = [
    r"bash\s+-i\s+>&\s+/dev/tcp/\S+",
    r"/dev/tcp/\d+\.\d+\.\d+\.\d+/\d+",
    r"socket\.socket\(\).*connect\(\s*\(",
    r"nc(\.exe)?\s+.*\s+-e\s+\S+",
    r"powershell.*(IEX|Invoke-Mimikatz|DownloadString)",
]

IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
URL_RE = re.compile(r"https?://[^\s'\"<>]+", re.IGNORECASE)


def _strings(data: bytes, min_len: int = 4, cap: int = 400):
    """Extract printable ASCII runs (static, no execution). Capped at `cap` strings so huge binaries stay cheap."""
    out, cur = [], []
    for b in data:
        if 32 <= b < 127:
            cur.append(chr(b))
        else:
            if len(cur) >= min_len:
                out.append("".join(cur))
                if len(out) >= cap:
                    break
            cur = []
    if cur and len(cur) >= min_len and len(out) < cap:
        out.append("".join(cur))
    return out


def detect_type(data: bytes) -> str:
    """Magic-number file typing (ELF/PE/PDF/ZIP/PNG/JPEG/shebang/text). Header bytes only — never executes."""
    if data.startswith(b"\x7fELF"):
        return "ELF executable (Linux)"
    if data.startswith(b"MZ"):
        return "PE executable (Windows MZ)"
    if data.startswith(b"%PDF"):
        return "PDF document"
    if data.startswith(b"PK\x03\x04"):
        return "ZIP archive (may be JAR/APK/DOCX)"
    if data.startswith(b"\x89PNG"):
        return "PNG image"
    if data.startswith(b"\xff\xd8\xff"):
        return "JPEG image"
    if data.startswith(b"#!"):
        first = data.split(b"\n", 1)[0][:80].decode("utf-8", "ignore")
        return f"Script ({first})"
    try:
        data.decode("utf-8")
        return "Text / script (utf-8 decodable)"
    except Exception:
        return "Unknown binary"


def analyze_bytes(data: bytes, filename: str = "upload") -> dict:
    """Pure static analysis. Never executes input."""
    size = len(data)
    sha256 = hashlib.sha256(data).hexdigest()
    ftype = detect_type(data)
    strs = _strings(data)
    blob = data.decode("utf-8", "ignore").lower()

    flags: list[dict] = []
    artifact: dict = {"kind": "generic"}
    lname = (filename or "").lower()

    for kw in SUSPICIOUS_KEYWORDS:
        if kw.lower() in blob:
            flags.append({"rule": f"keyword:{kw}", "severity": "HIGH",
                          "why": f"Contains attacker-tooling keyword '{kw}' — "
                                 "common in intrusions, rare in benign files."})
    for pat in REVERSE_SHELL_RES:
        m = re.search(pat, blob, re.IGNORECASE)
        if m:
            flags.append({"rule": f"pattern:{pat[:40]}…", "severity": "CRITICAL",
                          "why": f"Matches reverse-shell pattern '{m.group(0)[:60]}' — "
                                 "strong indicator of remote-access attempt."})

    # ---- phishing email (.eml): headers + links + attachments, stdlib only ----
    if lname.endswith(".eml") or blob.lstrip().startswith(("from ", "from:", "received:")):
        artifact = _parse_eml(data)
        for u in artifact.get("urls", [])[:10]:
            if re.search(r"(login|verify|password|invoice|payment|urgent)", u, re.I):
                flags.append({"rule": "phish:social-engineering-url", "severity": "HIGH",
                              "why": f"Link '{u[:70]}' pairs sensitive lure words with an external URL — "
                                     "classic credential-theft shape. Do not click; verify sender via known channel."})
                break
        if not artifact.get("has_spf_dkim"):
            flags.append({"rule": "phish:no-auth-headers", "severity": "MEDIUM",
                          "why": "No Authentication-Results/SPF/DKIM headers — sender is unverified. "
                                 "Check your mail gateway verdict before trusting."})
        if artifact.get("attachments"):
            flags.append({"rule": "phish:attachment", "severity": "MEDIUM",
                          "why": f"Carries attachment(s): {', '.join(artifact['attachments'][:3])} — "
                                 "open only the lab copy via static analysis, never the original."})

    # ---- PDF extras: JS / launch / embedded files ----
    if data.startswith(b"%PDF"):
        pdf_flags = []
        for token, label in ((b"/JavaScript", "embedded JavaScript"), (b"/OpenAction", "auto-run action"),
                             (b"/EmbeddedFile", "embedded file"), (b"/Launch", "launch action")):
            if token in data:
                pdf_flags.append(label)
        artifact = {"kind": "pdf", "objects": pdf_flags}
        if pdf_flags:
            flags.append({"rule": "pdf:active-content", "severity": "HIGH",
                          "why": f"PDF contains {', '.join(pdf_flags)} — top malicious-PDF shape. "
                                 "Review in a sandboxed reader on your workstation."})

    # ---- Office OOXML (docx/xlsx/pptm…): zip member list, macro + external links ----
    if lname.endswith(("docx", ".xlsx", ".pptx", ".docm", ".xlsm", ".pptm")) or (
            data.startswith(b"PK\x03\x04") and b"word/" in data[:4000]):
        artifact = _parse_ooxml(data)
        if artifact.get("has_macro"):
            flags.append({"rule": "doc:macro", "severity": "HIGH",
                          "why": "Contains vbaProject.bin (macro) — number-one document attack vector. "
                                 "Never enable macros; inspect strings only."})
        if artifact.get("external_links"):
            flags.append({"rule": "doc:external-link", "severity": "MEDIUM",
                          "why": f"External relationships: {', '.join(artifact['external_links'][:3])} — "
                                 "could pull a remote payload/template."})

    # ---- binaries: PE/ELF header details (struct only, no disassembly) ----
    if data.startswith(b"MZ"):
        artifact = _parse_pe(data)
        for dll in artifact.get("suspicious_imports", []):
            flags.append({"rule": f"pe:suspicious-import:{dll}", "severity": "HIGH",
                          "why": f"References '{dll}' — frequent in injection/credential tools. "
                                 "Confirm in Ghidra on your workstation."})
            break
    elif data.startswith(b"\x7fELF"):
        artifact = _parse_elf(data)

    # ---- packet capture (.pcap): header + flows + DNS names, stdlib struct ----
    if lname.endswith((".pcap", ".cap")) or data[:4] in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4"):
        artifact = _parse_pcap(data)
        for d in artifact.get("dns_names", [])[:5]:
            if re.search(r"(tk|xyz|top|gq|dyndns|duckdns|ngrok|onion)", d):
                flags.append({"rule": "pcap:suspicious-domain", "severity": "HIGH",
                              "why": f"Capture queries '{d}' — TLD/DDNS shape common in C2. "
                                     "Correlate with DNS view + flows."})
                break
        if artifact.get("packet_count", 0) and not flags:
            flags.append({"rule": "pcap:parsed", "severity": "LOW",
                          "why": f"Parsed {artifact['packet_count']} packet(s), "
                                 f"{len(artifact.get('flows', []))} flow(s). No known-bad domain shape."})

    ips = sorted({i for i in IP_RE.findall(blob)
                  if not i.startswith(("0.", "255."))})[:20]
    urls = sorted(set(URL_RE.findall(data.decode("utf-8", "ignore"))))[:20]
    if ips:
        flags.append({"rule": "ioc:embedded-ip", "severity": "MEDIUM",
                      "why": f"{len(ips)} embedded IP(s) — pivot to Security Graph "
                             "to see if any talked to your assets."})
    if urls:
        flags.append({"rule": "ioc:embedded-url", "severity": "MEDIUM",
                      "why": f"{len(urls)} embedded URL(s) — check proxy/DNS logs before visiting."})
    if ftype.startswith(("PE executable", "ELF executable")):
        flags.append({"rule": "type:executable", "severity": "MEDIUM",
                      "why": f"{ftype} — executables from untrusted sources need "
                             "workstation-grade review (Ghidra) before any handling."})

    level = "LOW"
    if any(f["severity"] == "CRITICAL" for f in flags):
        level = "CRITICAL"
    elif any(f["severity"] == "HIGH" for f in flags):
        level = "HIGH"
    elif flags:
        level = "MEDIUM"

    level_help = {
        "CRITICAL": "CRITICAL: reverse-shell/exploit pattern — isolate host, preserve image, escalate.",
        "HIGH": "HIGH: attacker-tooling keywords — treat as hostile until proven otherwise.",
        "MEDIUM": "MEDIUM: IOCs/executable type — correlate with flows + identity before closing.",
        "LOW": "LOW: no known-bad patterns — still verify provenance.",
    }[level]

    return {"filename": filename, "sha256": sha256, "size": size, "file_type": ftype,
            "risk": level, "risk_help": level_help,
            "flags": flags, "indicator_ips": ips, "indicator_urls": urls,
            "artifact": artifact,
            "strings_sample": strs[:60], "strings_total": len(strs),
            "safety": "Static analysis only. Sample was NOT executed. Do not hack back — "
                      "preserve evidence and follow your incident-response process."}


# ---------- artifact parsers (stdlib only, no execution) ----------
# Each `_parse_*` helper reads ONE format with struct/zipfile/email only and
# returns plain dicts consumed by `analyze_bytes` (which turns shapes into flags).

def _parse_eml(data: bytes) -> dict:
    """Parse .eml headers/body/attachments (stdlib `email`). Returns kind/from/subject/urls/attachments/has_spf_dkim."""
    from email import policy
    from email.parser import BytesParser
    try:
        msg = BytesParser(policy=policy.default).parsebytes(data)
    except Exception:
        return {"kind": "eml", "urls": [], "attachments": [], "has_spf_dkim": False}
    body = ""
    atts = []
    try:
        body = msg.get_body(preferencelist=("plain", "html")).get_content() if msg.get_body() else ""
    except Exception:
        body = ""
    for part in msg.walk():
        fn = part.get_filename()
        if fn and part.get_content_disposition() == "attachment":
            atts.append(fn)
    text = (str(msg.get("Subject", "")) + "\n" + (body or ""))[:20000]
    urls = sorted(set(URL_RE.findall(text)))[:20]
    hdrs = str(msg.keys())
    return {"kind": "eml", "from": str(msg.get("From", "")), "subject": str(msg.get("Subject", "")),
            "date": str(msg.get("Date", "")), "urls": urls, "attachments": atts[:10],
            "has_spf_dkim": ("Authentication-Results" in hdrs or "DKIM-Signature" in hdrs)}


def _parse_ooxml(data: bytes) -> dict:
    """List Office OOXML zip members; flag `vbaProject.bin` (macro) + external rels. Returns kind/members/has_macro/external_links."""
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        names = z.namelist()[:50]
    except Exception:
        return {"kind": "office", "members": [], "has_macro": False, "external_links": []}
    macro = any("vbaProject.bin" in n for n in names)
    ext = [n for n in names if "_rels" in n or "external" in n.lower()][:5]
    return {"kind": "office", "members": names[:20], "member_count": len(names),
            "has_macro": macro, "external_links": ext}


def _parse_pe(data: bytes) -> dict:
    """Read PE section count via `e_lfanew` + suspicious-import strings. struct only — no disassembly (that is Ghidra's job)."""
    try:
        e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
        n_sec = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    except Exception:
        n_sec = 0
    low = data.decode("utf-8", "ignore").lower()
    sus = [n for n in ("createremotethread", "virtualalloc", "writeprocessmemory",
                       "setwindowshookex", "lsass", "sekurlsa", "mimikatz")
           if n in low][:5]
    return {"kind": "pe", "sections": n_sec, "suspicious_imports": sus}


ELF_MACHINES = {3: "x86", 20: "PowerPC", 21: "PowerPC64", 22: "S390", 40: "ARM",
                62: "x86-64", 183: "AArch64", 243: "RISC-V"}


def _parse_elf(data: bytes) -> dict:
    """Read ELF class/machine (`ELF_MACHINES`) for triage context. Header bytes only."""
    try:
        ei_class = data[4]
        machine = struct.unpack_from("<H" if data[5] == 1 else ">H", data, 18)[0]
    except Exception:
        return {"kind": "elf"}
    return {"kind": "elf", "bits": 64 if ei_class == 2 else 32,
            "machine": ELF_MACHINES.get(machine, f"e_machine={machine}")}


def _parse_pcap(data: bytes, max_packets: int = 2000) -> dict:
    """Minimal pcap reader: Ethernet → IPv4 → TCP/UDP; DNS QNAMEs on udp/53.

    Depends on: `struct` + `_dns_qname`. Caps at `max_packets`. Returns
    kind/packet_count/flows/dns_names for flagging + pivoting to DNS/flows views.
    """
    try:
        magic = data[:4]
        le = magic == b"\xd4\xc3\xb2\xa1"
        bo = "<" if le else ">"
        off = 24
        flows: dict[tuple, int] = {}
        dns: list[str] = []
        n = 0
        while off + 16 <= len(data) and n < max_packets:
            ts_s, ts_u, caplen, _wire = struct.unpack_from(bo + "IIII", data, off)
            off += 16
            pkt = data[off:off + caplen]
            off += caplen
            n += 1
            if len(pkt) < 34:
                continue
            eth = struct.unpack_from(">H", pkt, 12)[0]
            if eth != 0x0800:
                continue
            ihl = (pkt[14] & 0x0F) * 4
            proto = pkt[23]
            src = ".".join(str(b) for b in pkt[26:30])
            dst = ".".join(str(b) for b in pkt[30:34])
            hdro = 14 + ihl
            if len(pkt) < hdro + 4:
                continue
            sp, dp = struct.unpack_from(">HH", pkt, hdro)
            flows[(src, dst, dp, proto)] = flows.get((src, dst, dp, proto), 0) + 1
            if proto == 17 and (sp == 53 or dp == 53) and len(pkt) > hdro + 20:
                qname = _dns_qname(pkt[hdro + 8:])
                if qname:
                    dns.append(qname)
        return {"kind": "pcap", "packet_count": n,
                "flows": [{"src": s, "dst": d, "port": p, "proto": pr, "packets": c}
                          for (s, d, p, pr), c in list(flows.items())[:30]],
                "dns_names": sorted(set(dns))[:20]}
    except Exception:
        return {"kind": "pcap", "packet_count": 0, "flows": [], "dns_names": []}


def _dns_qname(payload: bytes) -> str:
    """Decode one DNS QNAME from a UDP payload. Returns dotted name or '' on any parse failure."""
    try:
        qd = struct.unpack_from(">H", payload, 4)[0]
        if qd != 1:
            return ""
        i, labels = 12, []
        while i < len(payload) and payload[i] and len(labels) < 10:
            ln = payload[i]
            if i + 1 + ln > len(payload) or ln > 63:
                return ""
            labels.append(payload[i + 1:i + 1 + ln].decode("ascii", "ignore"))
            i += 1 + ln
        return ".".join(labels).lower().strip(".")
    except Exception:
        return ""
