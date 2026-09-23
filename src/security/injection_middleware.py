"""
Phase 9.4 — FastAPI middleware that inspects request bodies for
prompt injection before forwarding to the route handler.

Design:
  - BaseHTTPMiddleware — runs on every request
  - Only inspects POST bodies for configured paths (default: /ask, /ask/agent)
  - Skips /token, /dashboard/*, /admin/*, /health (not user-content endpoints)
  - On detection: returns 403 with a structured reason
  - Every block is logged to data/security/blocked.jsonl (append-only)
  - Fail-open: if the classifier itself errors, allow the request and log
    the error. Availability > paranoia for internal tooling.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

BLOCKED_LOG = Path("data/security/blocked.jsonl")

INSPECT_PATHS = {"/ask", "/ask/agent"}
SKIP_PATHS_PREFIX = ("/dashboard", "/admin", "/docs", "/openapi", "/redoc")


def _log_block(record: dict) -> None:
    BLOCKED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with BLOCKED_LOG.open("a") as f:
        f.write(json.dumps(record) + "\n")


class InjectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only inspect configured paths
        if request.url.path not in INSPECT_PATHS:
            return await call_next(request)

        if request.url.path.startswith(SKIP_PATHS_PREFIX):
            return await call_next(request)

        if request.method != "POST":
            return await call_next(request)

        # Read body, then put it back for the route handler
        body = await request.body()
        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Not JSON — let the route handler deal with it
            return await call_next(request)

        # Extract the user question
        question = payload.get("question") or payload.get("query") or ""
        if not question:
            return await call_next(request)

        # Classify
        try:
            from src.security.injection_classifier import classify
            verdict = classify(question)
        except Exception as e:
            # Fail-open
            _log_block({
                "ts": time.time(),
                "event": "classifier_error",
                "error": f"{type(e).__name__}: {e}",
                "path": request.url.path,
            })
            return await call_next(request)

        if verdict.is_injection:
            record = {
                "ts": time.time(),
                "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "event": "blocked",
                "path": request.url.path,
                "category": verdict.category,
                "confidence": verdict.confidence,
                "source": verdict.source,
                "matched_pattern": verdict.matched_pattern,
                "question_preview": question[:200],
            }
            _log_block(record)

            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Request blocked by injection firewall",
                    "category": verdict.category,
                    "confidence": verdict.confidence,
                    "source": verdict.source,
                },
            )

        return await call_next(request)


def recent_blocks(limit: int = 50) -> list[dict]:
    """Read the last N blocked attempts (for the dashboard page)."""
    if not BLOCKED_LOG.exists():
        return []
    lines = BLOCKED_LOG.read_text().splitlines()[-limit:]
    out = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return list(reversed(out))
