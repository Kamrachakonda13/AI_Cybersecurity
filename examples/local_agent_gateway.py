"""Minimal organization-owned/local agent integration example.

This example only asks AegisX for a policy decision. It does not execute tools.
Replace the placeholder token with a workload identity mechanism in production.
"""
import os
import sys
import requests

BASE = os.getenv("VEYRA_URL", "http://localhost:8000")
AGENT_ID = os.getenv("VEYRA_AGENT_ID", "internal-soc-agent")

# Require the token from the environment. Never hardcode it.
TOKEN = os.getenv("VEYRA_TOKEN")
if not TOKEN:
    sys.exit(
        "VEYRA_TOKEN is not set. Export it before running this example:\n"
        "    export VEYRA_TOKEN='<your-workload-token>'"
    )

payload = {
    "agent_id": AGENT_ID,
    "operation": "chat",
    "provider": "local",
    "model": "internal-model",
    "input": "Summarize the approved security evidence for this case.",
    "metadata": {"case_id": "CASE-001"},
}

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

try:
    r = requests.post(
        f"{BASE}/v1/policy/decide",
        json=payload,
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
except requests.RequestException as exc:
    sys.exit(f"Policy decision request failed: {exc}")

print(r.json())
