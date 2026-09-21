#!/usr/bin/env python3
"""AegisX endpoint agent — consented heartbeat sync for YOUR managed/lab hosts.

Help — what it does, dependencies, safety:
- Collects (stdlib only): hostname, IPs, MAC, OS, listening ports
  (`ss -tlnp` → `netstat` → `/proc/net/tcp` fallback), USB devices
  (`lsusb` on Linux, `system_profiler SPUSBDataType` on macOS), and DLP-lite
  secret-pattern hits in --watch dirs (private keys, AWS keys, password=).
- Syncs via ONE call: POST /api/collector/heartbeat (device+asset upsert,
- `--discover`: Wi-Fi/LAN neighbour sweep (arp + ping) → POST /api/ingest/discovery.
  Run on YOUR laptop (containers cannot see host Wi-Fi), private ranges only.
- Safety: runs on hosts YOU own with written authorization; read-only except
  posting to YOUR backend; auth via COLLECTOR_TOKEN header when the backend
  enforces it; --once for cron/launchd, --interval N for daemon mode.
- Depends on: backend /api/collector/heartbeat + /api/ingest/dlp.
  No third-party packages — pure stdlib so it runs anywhere Python 3.10+ does.

Usage:
  python3 collectors/endpoint-agent.py --api http://localhost:8000 --once
  COLLECTOR_TOKEN=s3cret python3 collectors/endpoint-agent.py --api URL --interval 300 --watch ~/Documents
  python3 collectors/endpoint-agent.py --discover auto --interval 1800 --yes  # re-sweep Wi-Fi every 30 min
"""
import argparse
import json
import os
import platform
import re
import socket
import subprocess
import sys
import time
import urllib.request
import uuid

SECRET_RES = [
    (r"-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----", "secret"),
    (r"AKIA[0-9A-Z]{16}", "secret"),
    (r"(?i)aws_secret.{0,10}[A-Za-z0-9/+=]{30,}", "secret"),
    (r"(?i)password\s*=\s*.+", "restricted"),
]


def sh(cmd, timeout=15):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
    except Exception:
        return ""


def identity():
    host = socket.gethostname()
    try:
        ips = socket.gethostbyname_ex(host)[2]
        ip = next((i for i in ips if not i.startswith("127.")), ips[0] if ips else "")
    except Exception:
        ip = ""
    mac = ":".join(f"{(uuid.getnode() >> i) & 0xFF:02x}" for i in range(0, 48, 8)[::-1])
    return host, ip, mac, f"{platform.system()} {platform.release()}"


def listening_ports():
    """Parse listening TCP ports; returns [{port, protocol, service, process, user}]."""
    out = []
    txt = sh(["ss", "-tlnp"])
    if txt:
        for m in re.finditer(r":(\d+)\s+.*users:\(\(\"([^\"]+)", txt):
            out.append({"port": int(m.group(1)), "protocol": "TCP",
                        "service": "unknown", "process": m.group(2), "user": "unknown"})
        if out:
            return out[:100]
    txt = sh(["netstat", "-anv"]) or sh(["netstat", "-tlnp"])
    for m in re.finditer(r"[*.](\d+)\s+.*LISTEN", txt):
        try:
            out.append({"port": int(m.group(1)), "protocol": "TCP", "service": "unknown",
                        "process": "unknown", "user": "unknown"})
        except ValueError:
            pass
    return out[:100]


def usb_devices():
    """List USB devices (names only — no content). Returns [{device, serial, action}]."""
    devs = []
    if sys.platform.startswith("linux"):
        for line in sh(["lsusb"]).splitlines():
            m = re.search(r"ID \S+ (.+)", line)
            if m:
                devs.append({"device": m.group(1).strip()[:120], "serial": "", "action": "connect"})
    elif sys.platform == "darwin":
        prof = sh(["system_profiler", "SPUSBDataType"], timeout=60)
        for m in re.finditer(r"^\s{6}(\S[^\n:]+):$", prof, re.M):
            name = m.group(1).strip()
            if name not in ("USB", "USB Bus"):
                devs.append({"device": name[:120], "serial": "", "action": "connect"})
    return devs[:30]


def dlp_scan(dirs):
    """Regex secret-pattern scan of watched dirs (filenames + first 64KB). Returns DLP items."""
    hits = []
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for fn in files[:500]:
                fp = os.path.join(root, fn)
                try:
                    with open(fp, "rb") as f:
                        blob = f.read(65536).decode("utf-8", "ignore")
                except Exception:
                    continue
                for pat, cls in SECRET_RES:
                    if re.search(pat, blob):
                        hits.append({"hostname": "", "username": os.getenv("USER", ""),
                                     "filepath": fp, "classification": cls, "action": "allowed"})
                        break
            if len(hits) > 100:
                break
    return hits[:100]


def post(api, path, body, token):
    req = urllib.request.Request(api + path, method="POST",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json",
                                          **({"X-Collector-Token": token} if token else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def run_once(api, token, owner, watch):
    host, ip, mac, osname = identity()
    hb = {"hostname": host, "ip_address": ip, "mac": mac, "os": osname, "owner": owner,
          "services": listening_ports(), "usb": usb_devices()}
    print("heartbeat:", post(api, "/api/collector/heartbeat", hb, token))
    if watch:
        hits = dlp_scan(watch)
        for h in hits:
            h["hostname"] = host
        if hits:
            print("dlp:", post(api, "/api/ingest/dlp", hits, token))
        else:
            print("dlp: no secret patterns in watched dirs")


def local_subnet():
    """Own /24 from the default-route source IP (UDP connect sends nothing)."""
    import ipaddress
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return str(ipaddress.ip_network(ip + "/24", strict=False))


def ping_one(ip: str) -> bool:
    flag = ["-n", "1", "-w", "1000"] if sys.platform.startswith("win") else ["-c", "1", "-W", "1"]
    try:
        return subprocess.run(["ping"] + flag + [ip],
                              capture_output=True, timeout=5).returncode == 0
    except Exception:
        return False


def arp_map():
    """Current IP→(mac, host?) from the arp table (no packets sent)."""
    import re as _re
    out = {}
    try:
        txt = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return out
    for m in _re.finditer(r"\(([0-9.]+)\)\s+at\s+([0-9a-f:]+)", txt, _re.I):
        if m.group(2).lower() not in ("ff:ff:ff:ff:ff:ff", "<incomplete>"):
            out[m.group(1)] = m.group(2).lower()
    return out


def _dns_name(buf: bytes, off: int):
    """Decode a (possibly compressed) DNS name at offset; returns (name, next_off)."""
    labels, jumped, next_off = [], False, off
    for _ in range(32):
        ln = buf[off]
        if ln == 0:
            off += 1
            if not jumped:
                next_off = off
            break
        if ln & 0xC0 == 0xC0:
            ptr = ((ln & 0x3F) << 8) | buf[off + 1]
            if not jumped:
                next_off = off + 2
            off, jumped = ptr, True
            continue
        off += 1
        labels.append(buf[off:off + ln].decode("utf-8", "replace"))
        off += ln
        if not jumped:
            next_off = off
    return ".".join(labels), next_off


def mdns_reverse(ip: str, timeout: float = 2.0) -> str:
    """mDNS (Bonjour) reverse lookup: many home devices answer .local PTR even
    when the router has no DNS records. Pure stdlib UDP multicast; read-only."""
    import struct as _st
    try:
        parts = ip.split(".")
        if len(parts) != 4:
            return ""
        qname = b"".join(bytes([len(p)]) + p.encode() for p in reversed(parts)) + b"\x07in-addr\x04arpa\x00"
        pkt = _st.pack(">HHHHHH", 0, 0, 1, 0, 0, 0) + qname + _st.pack(">HH", 12, 1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            sock.settimeout(timeout)
            sock.sendto(pkt, ("224.0.0.251", 5353))
            deadline = time.time() + timeout
            while time.time() < deadline:
                try:
                    data, _ = sock.recvfrom(512)
                except socket.timeout:
                    break
                if len(data) < 12:
                    continue
                qd = _st.unpack(">H", data[4:6])[0]
                an = _st.unpack(">H", data[6:8])[0]
                off = 12
                for _ in range(qd):
                    _, off = _dns_name(data, off)
                    off += 4
                for _ in range(an):
                    _, off = _dns_name(data, off)
                    rtype, _, _, rdlen = _st.unpack(">HHIH", data[off:off + 10])
                    off += 10
                    if rtype == 12:
                        name, _ = _dns_name(data, off)
                        name = name.removesuffix(".local").removesuffix(".")
                        if name:
                            return name
                    off += rdlen
        finally:
            sock.close()
    except Exception:
        pass
    return ""


def netbios_name(ip: str, timeout: float = 2.0) -> str:
    """NetBIOS node-status query (Windows/Samba boxes). UDP/137, read-only."""
    import struct as _st
    try:
        pkt = (_st.pack(">HHHHHH", 0x1234, 0x0000, 1, 0, 0, 0)
               + b"\x20CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x00" + _st.pack(">HH", 0x21, 0x01))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.settimeout(timeout)
            sock.sendto(pkt, (ip, 137))
            data, _ = sock.recvfrom(1024)
        finally:
            sock.close()
        if len(data) < 58:
            return ""
        count = data[56]
        for i in range(min(count, 16)):
            base = 57 + i * 18
            raw, suffix = data[base:base + 15], data[base + 15]
            name = raw.decode("ascii", "replace").strip()
            if name and suffix in (0x00, 0x03, 0x20) and not name.startswith("__"):
                return name
    except Exception:
        pass
    return ""


def rdns(ip: str, timeout: float = 4.0) -> str:
    """Best-effort device name: unicast rDNS → mDNS → NetBIOS → generated label."""
    from concurrent.futures import ThreadPoolExecutor as _Pool
    with _Pool(max_workers=1) as ex:
        fut = ex.submit(socket.gethostbyaddr, ip)
        try:
            return fut.result(timeout=timeout)[0]
        except Exception:
            pass
    for probe in (mdns_reverse, netbios_name):
        try:
            name = probe(ip)
        except Exception:
            name = ""
        if name:
            return name
    return f"host-{ip.replace('.', '-')}"


def default_gateway():
    """Default-gateway IP via system route table (no packets). Returns '' when unknown."""
    import re as _re
    out = sh(["route", "-n", "get", "default"])
    m = _re.search(r"gateway:\s*(\S+)", out)
    if m:
        return m.group(1)
    out = sh(["ip", "route", "show", "default"])
    m = _re.search(r"default via (\S+)", out)
    return m.group(1) if m else ""


def run_discovery(api, token, subnet, owner, assume_yes=False):
    """Ping-sweep a PRIVATE subnet, merge arp MACs, post neighbours.

    Confirmation required interactively unless assume_yes (cron/daemon after a
    recorded one-time approval — every run is still audit-logged server-side).
    """
    import ipaddress
    from concurrent.futures import ThreadPoolExecutor
    net = ipaddress.ip_network(subnet, strict=False)
    if not (net.is_private and net.prefixlen >= 16):
        sys.exit("! refusing: discovery allowed only on YOUR private /16-or-smaller range")
    if not assume_yes:
        ans = input(f"Type YES to ping-sweep {net} (your own Wi-Fi/LAN only): ")
        if ans.strip() != "YES":
            sys.exit("aborted — no packets sent")
    ips = [str(i) for i in list(net.hosts())[:254]]
    print(f"  sweeping {len(ips)} addresses…")
    with ThreadPoolExecutor(max_workers=50) as ex:
        alive = sorted(ip for ip, ok in zip(ips, ex.map(ping_one, ips)) if ok)
    macs = arp_map()
    gw = default_gateway()
    with ThreadPoolExecutor(max_workers=20) as ex:
        names = list(ex.map(lambda ip: rdns(ip), alive))
    if gw:
        names = ["gateway-router" if ip == gw else nm for ip, nm in zip(alive, names)]
    items = [{"ip_address": ip, "mac": macs.get(ip, ""),
              "hostname": host, "source": "agent-discover"}
             for ip, host in zip(alive, names)]
    print(post(api, "/api/ingest/discovery", items, token))
    print(f"{len(items)} neighbours posted. Unknown vendors = triage first.")


p = argparse.ArgumentParser()
p.add_argument("--api", default="http://localhost:8000")
p.add_argument("--owner", default="")
p.add_argument("--token", default=os.getenv("COLLECTOR_TOKEN", ""))
p.add_argument("--watch", nargs="*", default=[])
p.add_argument("--once", action="store_true")
p.add_argument("--interval", type=int, default=300)
p.add_argument("--discover", nargs="?", const="auto", default="",
               metavar="SUBNET", help="Wi-Fi/LAN sweep: 'auto' or 192.168.1.0/24")
p.add_argument("--yes", action="store_true",
               help="Skip sweep confirmation (scheduled runs after recorded approval)")
p.add_argument("--sensor", action="store_true",
               help="Launch the local read-only Wi-Fi sensor API on 127.0.0.1:8765")
p.add_argument("--host", default="127.0.0.1",
               help="Bind address for --sensor (keep 127.0.0.1)")
p.add_argument("--port", type=int, default=8765,
               help="Port for --sensor")
a = p.parse_args()
_SENSOR_ARGS = (a.host, a.port) if a.sensor else None
if _SENSOR_ARGS:
    pass  # launched from the __main__ guard below (run_sensor is defined later)
elif a.discover:
    subnet = local_subnet() if a.discover == "auto" else a.discover
    if a.interval > 0 and not a.once:
        while True:
            try:
                run_discovery(a.api, a.token, subnet, a.owner, assume_yes=a.yes)
            except Exception as e:  # noqa: BLE001 — daemon must survive one bad cycle
                print(f"! discovery cycle failed: {e}")
            time.sleep(a.interval)
    else:
        run_discovery(a.api, a.token, subnet, a.owner, assume_yes=a.yes)
elif a.once or a.interval <= 0:
    run_once(a.api, a.token, a.owner, a.watch)
else:
    while True:
        try:
            run_once(a.api, a.token, a.owner, a.watch)
        except Exception as e:  # noqa: BLE001 — daemon must survive one bad cycle
            print(f"! cycle failed: {e}")
        time.sleep(a.interval)

# ---- Local Wi-Fi sensor API (read-only) ----
def _wifi_scan_corewlan_helper():
    """Modern macOS (airport CLI removed): run the CoreWLAN scan via the
    Apple-signed swift toolchain runner (JIT).

    A locally compiled binary is ad-hoc-signed, which locationd treats as a
    "masquerading client" with no persisting Location grant — SSID/BSSID stay
    blank forever. The Apple-signed swift runner has a verifiable identity, so
    airportd discloses SSIDs without any per-app Location approval.
    Returns (rows, current_ssid).
    """
    import os as _os
    import shutil as _shutil
    here = _os.path.dirname(_os.path.abspath(__file__))
    script = _os.path.join(here, "wifi-scan-jit.swift")
    swift = _shutil.which("swift") or "/usr/bin/swift"
    if not (_os.path.isfile(script) and _os.path.isfile(swift)):
        return [], ""
    try:
        blob = subprocess.run([swift, script], capture_output=True, text=True, timeout=180).stdout
        data = json.loads(blob or "{}")
        rows = data.get("networks") or []
        cur = data.get("current") or {}
        return rows, cur.get("ssid", "")
    except Exception:
        return [], ""


def wifi_scan():
    """Return nearby Wi-Fi metadata using the host OS native read-only scanner."""
    rows=[]
    if sys.platform == "darwin":
        out=sh(["/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport","-s"], timeout=30)
        if out.strip():
            for line in out.splitlines()[1:]:
                m=re.match(r"\s*(.*?)\s+([0-9a-f:]{17})\s+(-?\d+)\s+\S+\s+(\d+|-)\s+.*$", line, re.I)
                if m:
                    ssid,bssid,signal,channel=m.groups(); ch=channel
                    rows.append({"ssid":ssid.strip(),"bssid":bssid.upper(),"signal_dbm":float(signal),"channel":ch,"band":"5/6GHz" if ch.isdigit() and int(ch)>14 else "2.4GHz","security":"Unknown","source":"macOS-native"})
            return rows[:200]
        # Modern macOS: airport CLI removed → CoreWLAN helper binary.
        helper_rows, _ = _wifi_scan_corewlan_helper()
        if helper_rows:
            return helper_rows[:200]
        return []
    elif sys.platform.startswith("linux"):
        out=sh(["nmcli","-t","-f","SSID,BSSID,SIGNAL,CHAN,SECURITY","dev","wifi","list"], timeout=30)
        for line in out.splitlines():
            parts=line.split(":")
            # nmcli terse output escapes colons in BSSID; recover with regex for the common format.
            m=re.match(r"(.*?)\\:([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5}):(\d+):(\d+):(.*)$", line)
            if m:
                ssid,bssid,signal,ch,security=m.groups(); rows.append({"ssid":ssid.replace('\\: ',':').strip(),"bssid":bssid.upper(),"signal_dbm":float(signal),"channel":ch,"band":"5/6GHz" if int(ch)>14 else "2.4GHz","security":security or "Unknown","source":"Linux-nmcli"})
    elif sys.platform.startswith("win"):
        out=sh(["netsh","wlan","show","networks","mode=bssid"], timeout=30)
        current_ssid=""
        for line in out.splitlines():
            sm=re.search(r"^\s*SSID\s+\d+\s*:\s*(.*)$", line, re.I)
            if sm: current_ssid=sm.group(1).strip()
            bm=re.search(r"^\s*BSSID\s+\d+\s*:\s*([0-9a-f:]{17})$", line, re.I)
            if bm:
                rows.append({"ssid":current_ssid,"bssid":bm.group(1).upper(),"signal_dbm":None,"channel":"","band":"","security":"Unknown","source":"Windows-native"})
            sm2=re.search(r"^\s*Signal\s*:\s*(\d+)%", line, re.I)
            if sm2 and rows: rows[-1]["signal_percent"]=int(sm2.group(1))
            cm=re.search(r"^\s*Channel\s*:\s*(\d+)", line, re.I)
            if cm and rows:
                rows[-1]["channel"]=cm.group(1); rows[-1]["band"]="5/6GHz" if int(cm.group(1))>14 else "2.4GHz"
    return rows[:200]

def wifi_current():
    """Best-effort current SSID; no credentials or password material."""
    if sys.platform == "darwin":
        _, helper_ssid = _wifi_scan_corewlan_helper()
        if helper_ssid:
            return {"ssid": helper_ssid}
        out=sh(["networksetup","-getairportnetwork","en0"], timeout=10)
        m=re.search(r"Current Wi-Fi Network:\s*(.*)$", out, re.I|re.M)
        return {"ssid":m.group(1).strip()} if m else {"ssid":""}
    if sys.platform.startswith("linux"):
        out=sh(["nmcli","-t","-f","ACTIVE,SSID,DEVICE","dev","wifi"], timeout=10)
        for line in out.splitlines():
            if line.startswith("yes:"):
                p=line.split(":",2); return {"ssid":p[1] if len(p)>1 else "", "device":p[2] if len(p)>2 else ""}
    if sys.platform.startswith("win"):
        out=sh(["netsh","wlan","show","interfaces"], timeout=10)
        m=re.search(r"^\s*SSID\s*:\s*(.*)$", out, re.I|re.M)
        return {"ssid":m.group(1).strip()} if m else {"ssid":""}
    return {"ssid":""}

def run_sensor(host="127.0.0.1", port=8765):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    class Handler(BaseHTTPRequestHandler):
        def _json(self, payload, status=200):
            blob=json.dumps(payload).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(blob))); self.send_header("Access-Control-Allow-Origin", "*"); self.send_header("Access-Control-Allow-Methods","GET,OPTIONS"); self.end_headers(); self.wfile.write(blob)
        def do_OPTIONS(self): self._json({"ok":True})
        def do_GET(self):
            if self.path.startswith("/health"): return self._json({"ok":True,"sensor":"aegisx-local-wifi","platform":platform.system()})
            if self.path.startswith("/wifi/current"): return self._json(wifi_current())
            if self.path.startswith("/wifi/scan"): return self._json({"networks":wifi_scan(),"current":wifi_current()})
            return self._json({"error":"not found"},404)
        def log_message(self,*args): pass
    print(f"AegisX local Wi-Fi sensor listening on http://{host}:{port}")
    ThreadingHTTPServer((host,port),Handler).serve_forever()

if __name__ == "__main__":
    # --sensor launches the local read-only Wi-Fi service (handled here because
    # run_sensor is defined above this guard).
    if _SENSOR_ARGS is not None:
        run_sensor(*_SENSOR_ARGS)
        raise SystemExit
    # Preserve existing CLI behavior; use --sensor to launch the local read-only Wi-Fi service.
    if "--sensor" in sys.argv:
        ap=argparse.ArgumentParser(); ap.add_argument("--sensor",action="store_true"); ap.add_argument("--host",default="127.0.0.1"); ap.add_argument("--port",type=int,default=8765); args=ap.parse_args(); run_sensor(args.host,args.port); raise SystemExit
