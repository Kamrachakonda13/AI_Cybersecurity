"""VEYRA FastAPI application entrypoint.

Help — what this file does and what it depends on:
- Builds the FastAPI `app` (title "VEYRA Security Platform") and mounts the
  API `router` from `app.api.routes` (all `/api/*` endpoints) plus `GET /health`.
- `lifespan`: on startup creates every table via `Base.metadata.create_all`
  (models register themselves on `Base` in `app.db` when `app.models` is
  imported) and runs `seed(db)` from `app.services.seed` (idempotent demo data).
  When `THREATINTEL_AUTO_REFRESH=true`, also starts the 24h KEV background loop
  from `app.services.threatintel` (failure-safe: logs only, never crashes boot).
  Depends on: `app.db` (Base, engine, SessionLocal), `app.models` (side-effect
  import registers all entities), `app.services.seed`, `app.api.routes`.
- CORS origins come from the `CORS_ORIGINS` env var (see `backend/.env.example`).
- Run locally: `uvicorn app.main:app` from `backend/`; in Docker via `backend/Dockerfile`.
"""
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from .db import Base, engine, SessionLocal
from .models import *
from .services.seed import seed, seed_identity
from .api.routes import router
from .api.v50_routes import router as v50_router
from .api.enterprise_rag import router as enterprise_rag_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables, seed demo data, optionally start KEV auto-refresh loop."""
    Base.metadata.create_all(bind=engine)
    # POC schema compatibility: add newer columns to existing SQLite/Postgres databases.

    def _ensure_columns(table: str, columns: dict[str, str]):
        try:
            insp = inspect(engine)
            existing = {c["name"] for c in insp.get_columns(table)}
            for name, ddl_type in columns.items():
                if name not in existing:
                    with engine.begin() as conn:
                        conn.execute(
                            text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl_type}"))
        except Exception:
            pass
    _ensure_columns("discovered_hosts", {"trusted": "BOOLEAN DEFAULT FALSE"})
    _ensure_columns("user_tool_permissions", {
                    "expires_at": "TIMESTAMP WITH TIME ZONE"})
    _ensure_columns("security_tool_jobs", {"params": "TEXT DEFAULT '{}'"})
    db = SessionLocal()
    try:
        seed(db)
        seed_identity(db)
    finally:
        db.close()
    if os.getenv("THREATINTEL_AUTO_REFRESH", "false").lower() == "true":
        from .services.threatintel import _auto_refresh_loop
        asyncio.create_task(_auto_refresh_loop())
    yield


# API Versioning Strategy:
# - /api/ : existing console contract retained for frontend compatibility
# - /api/v1/ : versioned alias for API consumers
# - Both surfaces resolve to the same governed handlers during migration
# - Version bump to v5.1.0 on next breaking change
app = FastAPI(title="VEYRA Security Platform",
              version="5.0.0", lifespan=lifespan)
origins = [x.strip() for x in os.getenv(
    "CORS_ORIGINS", "http://localhost:3000").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
app.include_router(router, prefix="/api/v1")
app.include_router(v50_router, prefix="/api")
app.include_router(v50_router, prefix="/api/v1")
app.include_router(enterprise_rag_router, prefix="/api")
app.include_router(enterprise_rag_router, prefix="/api/v1")


@app.get("/health")
def health(): return {"status": "ok",
                      "service": "veyra-api", "version": "5.0.0"}
