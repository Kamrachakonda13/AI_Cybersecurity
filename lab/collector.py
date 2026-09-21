#!/usr/bin/env python3
"""AegisX consented device collector — READ-ONLY by default.

Collects devices YOU own for the Endpoint inventory:
  - passive: parses local `arp -a` neighbour table (no packets sent)
  - --active: ICMP ping-sweep of ONE explicit CIDR you type in (lab only),
    refuses anything that is not RFC1918.

Browsing history is NEVER scraped. To populate DNS panels, export artefacts
YOU are entitled to (router DNS log, Pi-hole query log, or your own browser
history export) and POST them to /api/ingest/dns. Same for logins: forward
syslog/auth.log lines from YOUR OWN hosts to /api/ingest/logins.

Usage:
  python3 lab/collector.py --api http://localhost:8000 --dry-run
  python3 lab/collector.py --api http://localhost:8000 --post --owner "Blue team"
  python3 lab/collector.py --active 192.168.1.0/24 --post
"""
import argparse
import ipaddress
import json
import re
import socket
import struct
import subprocess
import sys
import time
import urllib.request

ARP_RE = re.compile(r"\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-f:]+)", re.I)


def arp_table():
    try:
        out = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=10).stdout
    except Exception as e:
        print(f"! cannot read arp table: {e}")
        return []
    devs = []
    for m in ARP_RE.finditer(out):
        ip, mac = m.group(1), m.group(2).lower()
        if mac in ("ff:ff:ff:ff:ff:ff", "<incomplete>"):
            continue
        try:
            host = socket.gethostbyaddr(ip)[0]
        except Exception:
            host = f"host-{ip.replace('.', '-')}"
        devs.append({"hostname": host, "ip_address": ip, "mac": mac, "os": "", "owner": ""})
    return devs


def ping_sweep(cidr: str):
    try:
        net = ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        sys.exit("! invalid CIDR")
    if not (net.is_private and net.prefixlen >= 16):
        sys.exit("! refusing: active sweep allowed only on YOUR private /16-or-smaller lab range")
    print(f"  sweeping {net} (ICMP echo, 1s timeout each, may take a while)…")
    found = []
    for ip in list(net.hosts())[:254]:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW if hasattr(socket, "SOCK_RAW") else socket.SOCK_DGRAM,
                          socket.IPPROTO_ICMP) if False else None
        # Portable path: system ping, one packet, one second
        try:
            r = subprocess.run(["ping", "-c", "1", "-W", "1", str(ip)],
                               capture_output=True, timeout=5)
            if r.returncode == 0:
                found.append({"hostname": f"host-{str(ip).replace('.', '-')}",
                              "ip_address": str(ip), "mac": "", "os": "", "owner": ""})
        except Exception:
            pass
    return found


def post(api, path, body):
    req = urllib.request.Request(api + path, method="POST",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


p = argparse.ArgumentParser()
p.add_argument("--api", default="http://localhost:8000")
p.add_argument("--owner", default="")
p.add_argument("--dry-run", action="store_true")
p.add_argument("--post", action="store_true")
p.add_argument("--active", metavar="CIDR", default="")
a = p.parse_args()

devs = arp_table()
print(f"passive arp neighbours: {len(devs)}")
if a.active:
    ans = input(f"Type YES to ping-sweep {a.active} (your own lab only): ")
    if ans.strip() != "YES":
        sys.exit("aborted — no packets sent")
    devs += ping_sweep(a.active)
    print(f"active sweep found: {len(devs)} total")

for d in devs:
    d["owner"] = a.owner
    d["source"] = "lab-collector"

if a.dry_run or not a.post:
    print(json.dumps(devs[:10], indent=1))
    print("(dry run — nothing sent. Re-run with --post to ingest.)")
else:
    print(post(a.api, "/api/ingest/devices", devs))
    disc = [{"ip_address": d["ip_address"], "mac": d.get("mac", ""),
             "hostname": d["hostname"], "source": "lab-collector"} for d in devs if d.get("ip_address")]
    if disc:
        print(post(a.api, "/api/ingest/discovery", disc))
        print(f"({len(disc)} neighbours also posted to Wi-Fi discovery.)")
    print("Reminder: you may only ingest devices/networks you own or are authorised for, "
          "with users notified per policy.")
