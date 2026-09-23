"""Adapter for the separately maintained Agentic RAG ingestion fabric."""
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from .routes import require_admin

router = APIRouter(prefix="/enterprise/rag", tags=["enterprise intelligence"])


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


def _base_url() -> str:
    return os.getenv("AGENTIC_RAG_URL", "http://localhost:8100").rstrip("/")


def _headers() -> dict[str, str]:
    token = os.getenv("AGENTIC_RAG_TOKEN", "").strip()
    return {"Authorization": f"Bearer {token}"} if token else {}


def _request(method: str, path: str, **kwargs):
    try:
        with httpx.Client(base_url=_base_url(), timeout=10.0) as client:
            response = client.request(
                method, path, headers=_headers(), **kwargs)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502, detail=f"Agentic RAG service returned {exc.response.status_code}") from exc
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=503, detail="Agentic RAG service is unavailable") from exc


@router.get("/status")
def status(_: bool = Depends(require_admin)):
    health = _request("GET", "/health")
    try:
        metrics = _request("GET", "/metrics")
    except HTTPException:
        metrics = {"available": False}
    return {"service": "agentic-rag", "base_url": _base_url(), "health": health, "metrics": metrics}


@router.post("/ask")
def ask(req: AskRequest, request: Request, _: bool = Depends(require_admin)):
    if not os.getenv("AGENTIC_RAG_TOKEN", "").strip():
        raise HTTPException(
            status_code=503, detail="AGENTIC_RAG_TOKEN is not configured")
    result = _request("POST", "/ask", json={"question": req.question})
    return {"source": "agentic-rag", "tenant": request.headers.get("X-VEYRA-Tenant", "default"), **result}


@router.get("/connectors")
def connectors(_: bool = Depends(require_admin)):
    return _request("GET", "/admin/connectors")
