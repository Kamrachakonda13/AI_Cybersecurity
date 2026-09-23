import sys
import time
from pathlib import Path

# Add project root so `from src.x import y` resolves
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import Depends, FastAPI, HTTPException  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from src.admin_api import router as admin_router
from src.dashboard.routes import public_router as dashboard_public_router, router as dashboard_router
from src.agent import run_agent  # noqa: E402
from src.audit import log_request  # noqa: E402
from src.auth import current_user, issue_token  # noqa: E402
from src.security.injection_middleware import InjectionMiddleware  # noqa: E402
from src.generate import generate  # noqa: E402
from src.graph_retrieve import graph_retrieve  # noqa: E402
from src.guardrail import check_input  # noqa: E402
from src.hybrid_retrieve import hybrid_retrieve  # noqa: E402
from src.metrics import snapshot as metrics_snapshot  # noqa: E402
from src.rerank import rerank  # noqa: E402
from src.router import route  # noqa: E402
from src.traces import get_trace, list_traces  # noqa: E402

app = FastAPI(title="Hybrid + Graph + Agentic RAG API with RBAC")
app.include_router(admin_router)
app.include_router(dashboard_public_router)
app.include_router(dashboard_router)


# ---------------------------------------------------------------------------
# 7.22 — Session middleware
# ---------------------------------------------------------------------------
# Decodes the dashboard session cookie (if present) and exposes the user
# on request.state.current_user. Silently no-ops on missing/invalid tokens
# — this does NOT gate anything; the router dependency does that.

from starlette.middleware.base import BaseHTTPMiddleware  # noqa: E402
from starlette.requests import Request as _StarletteRequest  # noqa: E402


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: _StarletteRequest, call_next):
        request.state.current_user = None
        token = request.cookies.get("rag_session")
        if token:
            try:
                from src.auth import ROLE_CLEARANCE, decode_token
                payload = decode_token(token)
                request.state.current_user = {
                    "user_id": payload["sub"],
                    "role": payload.get("role"),
                    "tenant_id": payload.get("tenant_id"),
                    "clearance": ROLE_CLEARANCE.get(payload.get("role"), "PUBLIC"),
                }
            except Exception:
                pass
        return await call_next(request)


app.add_middleware(SessionMiddleware)
app.add_middleware(InjectionMiddleware)

# ---------------------------------------------------------------------------
# 7.22 — No-store cache headers on /dashboard/*
# ---------------------------------------------------------------------------
# Prevents the browser back button from re-rendering a gated page from
# cache after logout. The server still 307s on the real request; this just
# stops the browser from painting the stale snapshot.

@app.middleware("http")
async def dashboard_no_store(request: _StarletteRequest, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/dashboard"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
        response.headers["Pragma"] = "no-cache"
    return response



# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class AskRequest(BaseModel):
    question: str


class TokenRequest(BaseModel):
    user_id: str
    role: str
    tenant_id: str = "acme"


class Citation(BaseModel):
    id: str
    source: str
    clearance_level: str
    score: float
    kind: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    route: str
    route_reason: str
    refused: bool


class AgentStep(BaseModel):
    kind: str
    payload: dict


class AgentResponse(BaseModel):
    trace_id: str
    answer: str
    steps: list[dict]
    tool_calls: int
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    refused: bool = False


# ---------------------------------------------------------------------------
# Core endpoints (unchanged from Phase 3)
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/token")
def token(req: TokenRequest):
    try:
        t = issue_token(req.user_id, req.role, req.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"access_token": t, "token_type": "bearer"}


def _run_hybrid(user: dict, question: str):
    candidates = hybrid_retrieve(
        question,
        user_clearance=user["clearance"],
        tenant_id=user["tenant_id"],
        top_k=20,
    )
    if not candidates:
        return None, []
    reranked = rerank(question, candidates, top_k=5)
    citations = [
        Citation(
            id=c["id"],
            source=c["source_file"],
            clearance_level=c["clearance_level"],
            score=round(c["rerank_score"], 3),
            kind="chunk",
        )
        for c in reranked
    ]
    context_chunks = [{"id": c["id"], "content": c["content"]} for c in reranked]
    return context_chunks, citations


def _run_graph(question: str):
    result = graph_retrieve(question)
    if not result["matched_entities"]:
        return None, []
    citations = [
        Citation(
            id=f"graph:{r['source']}->{r['target']}",
            source="neo4j",
            clearance_level=r.get("clearance") or "INTERNAL",
            score=1.0,
            kind="graph_edge",
        )
        for r in result["rows"][:10]
    ]
    context_chunks = [{"id": "graph-subgraph", "content": result["context"]}]
    return context_chunks, citations


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, user: dict = Depends(current_user)):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Empty question")

    safe, reason = check_input(req.question)
    if not safe:
        log_request(
            user_id=user["user_id"],
            role=user["role"],
            tenant_id=user["tenant_id"],
            query=req.question,
            returned_chunk_ids=[],
            refused=True,
            reason=reason,
            route="blocked",
        )
        raise HTTPException(status_code=400, detail=reason)

    decision = route(req.question)
    chosen_route = decision["mode"]
    route_reason = decision["reason"]

    if chosen_route == "graph":
        context_chunks, citations = _run_graph(req.question)
        if context_chunks is None:
            chosen_route = "hybrid"
            route_reason = "Graph route had no matching entities; fell back to hybrid"
            context_chunks, citations = _run_hybrid(user, req.question)
    else:
        context_chunks, citations = _run_hybrid(user, req.question)

    if not context_chunks:
        log_request(
            user_id=user["user_id"],
            role=user["role"],
            tenant_id=user["tenant_id"],
            query=req.question,
            returned_chunk_ids=[],
            refused=True,
            reason="No accessible content",
            route=chosen_route,
        )
        return AskResponse(
            answer="I don't know based on the provided context.",
            citations=[],
            route=chosen_route,
            route_reason=route_reason,
            refused=True,
        )

    t0 = time.time()
    answer = generate(req.question, context_chunks, tool=chosen_route)
    latency_ms = int((time.time() - t0) * 1000)

    log_request(
        user_id=user["user_id"],
        role=user["role"],
        tenant_id=user["tenant_id"],
        query=req.question,
        returned_chunk_ids=[c["id"] for c in context_chunks],
        refused=False,
        route=chosen_route,
        latency_ms=latency_ms,
    )

    return AskResponse(
        answer=answer,
        citations=citations,
        route=chosen_route,
        route_reason=route_reason,
        refused=False,
    )


# ---------------------------------------------------------------------------
# Agent endpoint (new in Phase 4)
# ---------------------------------------------------------------------------

@app.post("/ask_agent", response_model=AgentResponse)
def ask_agent(req: AskRequest, user: dict = Depends(current_user)):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Empty question")

    safe, reason = check_input(req.question)
    if not safe:
        log_request(
            user_id=user["user_id"],
            role=user["role"],
            tenant_id=user["tenant_id"],
            query=req.question,
            returned_chunk_ids=[],
            refused=True,
            reason=reason,
            route="blocked",
        )
        raise HTTPException(status_code=400, detail=reason)

    result = run_agent(
        req.question,
        user_clearance=user["clearance"],
        tenant_id=user["tenant_id"],
    )

    log_request(
        user_id=user["user_id"],
        role=user["role"],
        tenant_id=user["tenant_id"],
        query=req.question,
        returned_chunk_ids=[],
        refused=False,
        route="agent",
        prompt_tokens=result["prompt_tokens"],
        completion_tokens=result["completion_tokens"],
        latency_ms=result["latency_ms"],
    )

    return AgentResponse(**result)


# ---------------------------------------------------------------------------
# Observability endpoints (new in Phase 4)
# ---------------------------------------------------------------------------

@app.get("/metrics")
def get_metrics():
    return metrics_snapshot()


@app.get("/traces")
def get_traces(limit: int = 50):
    return {"traces": list_traces(limit=limit)}


@app.get("/traces/{trace_id}")
def get_trace_by_id(trace_id: str):
    steps = get_trace(trace_id)
    if not steps:
        raise HTTPException(status_code=404, detail="Trace not found")
    return {"trace_id": trace_id, "steps": steps}