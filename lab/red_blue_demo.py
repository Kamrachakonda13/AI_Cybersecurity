#!/usr/bin/env python3
"""VEYRA red vs blue demo — runs ENTIRELY against local lab + local API.
Red: passive posture assessment of lab target (approval-governed).
Blue: ingest synthetic attack telemetry, then verify graph/attack-path/audit.

Usage:
  python3 lab/red_blue_demo.py [--api http://localhost:8000] [--target http://localhost:4101]
"""
import argparse, json, sys, urllib.request

def call(api, method, path, body=None):
    req = urllib.request.Request(api + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except Exception as e:
        print(f"! {method} {path} failed: {e}"); sys.exit(1)

p = argparse.ArgumentParser()
p.add_argument("--api", default="http://localhost:8000")
p.add_argument("--target", default="http://localhost:4101")
a = p.parse_args()

print("== RED TEAM: approval-governed posture assessment ==")
s, r = call(a.api, "POST", "/api/assessments/web", {"url": a.target})
print(f"step 1 (no approval): {r.get('status')} — {r.get('message','')[:100]}")
# Backend resolves lab via its own DNS; rewrite host for in-cluster fetch:
in_cluster = a.target.replace("localhost", "vulnerable-web").replace("127.0.0.1", "vulnerable-web")
s, r = call(a.api, "POST", "/api/assessments/web", {"url": in_cluster, "approval_confirmed": True})
print(f"step 2 (approved, {in_cluster}): {r.get('status')} header_score={r.get('header_score')} findings={len(r.get('findings',[]))}")

print("\n== BLUE TEAM: ingest synthetic attack telemetry ==")
s, r = call(a.api, "POST", "/api/ingest/network-flows",
    [{"src_ip": "10.10.40.8", "dst_ip": "10.10.20.17", "dst_port": 443,
      "src_asset_id": 4, "dst_asset_id": 1, "bytes_out": 1840000, "risk_score": 74}])
print("flows ingested:", r)
s, r = call(a.api, "POST", "/api/ingest/sessions",
    [{"username": "red-lab", "source_ip": "10.10.40.99", "application": "Lab Attacker",
      "asset_id": 1, "auth_method": "password-spray (simulated)", "privileged": True, "anomaly_score": 0.91}])
print("sessions ingested:", r)

print("\n== BLUE TEAM: verify detection ==")
s, paths = call(a.api, "GET", "/api/graph/attack-path?max_paths=3")
print(f"attack paths: {len(paths['paths'])} to {paths['sensitive_targets']} sensitive targets")
for pth in paths["paths"][:2]:
    print(f" - {pth['target_label']} ({pth['length']} hops)")
s, ans = call(a.api, "GET", "/api/graph/answer?kind=connection_owner")
top = ans["results"][0] if ans["results"] else {}
print("top anomalous session:", top)
print("\nDemo complete. Check UI: Security Graph + Offensive Security + audit log.")
