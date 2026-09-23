"""
Promptfoo provider for the RAG agent.

Promptfoo calls this file with a JSON payload on stdin. We forward the
query to the running FastAPI server's /ask_agent endpoint with a JWT.

Run the API first:
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import httpx
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

DEFAULT_USER = {
    "user_id": "alice@acme.com",
    "role": "csuite",
    "tenant_id": "acme",
}

ROLE_CLEARANCE = {
    "junior": "PUBLIC",
    "manager": "INTERNAL",
    "csuite": "CONFIDENTIAL",
    "admin": "RESTRICTED",
}


def _get_token(user: dict) -> str:
    response = httpx.post(
        f"{API_BASE}/token",
        json={
            "user_id": user["user_id"],
            "role": user["role"],
            "tenant_id": user["tenant_id"],
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def call_api(prompt: str, options: dict, context: dict) -> dict:
    user = DEFAULT_USER.copy()
    if isinstance(context, dict) and "vars" in context:
        vars_ = context["vars"]
        if "user_role" in vars_:
            user["role"] = vars_["user_role"]
            user["clearance"] = ROLE_CLEARANCE.get(vars_["user_role"], "PUBLIC")

    try:
        token = _get_token(user)
        response = httpx.post(
            f"{API_BASE}/ask_agent",
            json={"question": prompt},
            headers={"Authorization": f"Bearer {token}"},
            timeout=120.0,
        )

        if response.status_code == 400:
            # Guardrail block — return the detail as a refusal
            try:
                body = response.json()
                detail = body.get("detail", "blocked")
            except Exception:
                detail = response.text[:200]
            return {
                "output": json.dumps({
                    "answer": f"Blocked: {detail}",
                    "refused": True,
                    "tool_calls": 0,
                    "steps": [],
                    "http_status": 400,
                }),
            }

        if response.status_code != 200:
            return {
                "output": json.dumps({
                    "answer": f"API_ERROR: {response.status_code}",
                    "refused": False,
                    "tool_calls": 0,
                    "steps": [],
                    "http_status": response.status_code,
                }),
            }

        data = response.json()

        return {
            "output": json.dumps({
                "answer": data.get("answer", ""),
                "refused": data.get("refused", False),
                "tool_calls": data.get("tool_calls", 0),
                "steps": data.get("steps", []),
                "trace_id": data.get("trace_id"),
            }),
        }

    except Exception as e:
        return {
            "output": json.dumps({
                "answer": f"PROVIDER_ERROR: {str(e)[:200]}",
                "refused": False,
                "tool_calls": 0,
                "steps": [],
            }),
            "error": str(e)[:200],
        }
