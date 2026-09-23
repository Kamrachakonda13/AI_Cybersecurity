"""Dashboard routes for FastAPI."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.connectors.registry import ConnectorRegistry
from src.dashboard.chunks_query import fetch_chunks, count_chunks, list_sources
from src.dashboard.permissions_query import build_matrix, get_accessible_chunks
from src.dashboard.users_query import list_users_with_access_counts, get_user_chunks
from src.dashboard.duplicates_query import get_duplicates_summary
from src.dashboard.metrics_query import (
    summary_metrics, tokens_by_route, latency_buckets, recent_requests
)
from src.dashboard.pipeline_query import (
    read_sync_state, read_connector_status, read_recent_runs, run_pipeline_now
)

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

from src.dashboard.auth import (
    clear_session_cookie,
    require_dashboard_user,
    set_session_cookie,
    verify_credentials,
)

# Public routes (login/logout) — NOT gated
public_router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Gated routes — every route declared on this router requires a session
router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(require_dashboard_user)],
)


def _gather_stats():
    stats = {
        "total_sources": 0, "loaded_sources": 0, "failed_sources": 0,
        "total_documents": 0, "total_chunks": 0,
        "active_chunks": 0, "deleted_chunks": 0,
        "duplicate_groups": 0,
    }
    connectors_info = []

    try:
        registry = ConnectorRegistry.from_manifest("data/connectors/registry.json")
        entries = registry.list_sources()
        stats["total_sources"] = len(entries)

        for entry in entries:
            info = {
                "name": entry["name"],
                "source_system": entry.get("source_system", entry["name"]),
                "status": entry["status"],
                "document_count": None,
                "error": None,
            }
            if entry["status"] == "loaded":
                stats["loaded_sources"] += 1
                try:
                    connector = registry.get(entry["name"])
                    docs = list(connector.list_changed_since(cursor=None))
                    info["document_count"] = len(docs)
                    stats["total_documents"] += len(docs)
                except Exception as e:
                    info["error"] = str(e)[:80]
            else:
                stats["failed_sources"] += 1
                info["error"] = entry.get("error", "unknown")
            connectors_info.append(info)
    except Exception as e:
        connectors_info.append({
            "name": "registry", "source_system": "error", "status": "failed",
            "document_count": None, "error": str(e)[:100],
        })

    try:
        import psycopg2
        db_url = os.getenv("DATABASE_URL", "postgresql://raguser:ragpass@localhost:5432/ragdb")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE deleted_at IS NULL) AS active,
                COUNT(*) FILTER (WHERE deleted_at IS NOT NULL) AS deleted
            FROM chunks
        """)
        row = cur.fetchone()
        stats["active_chunks"] = row[0] or 0
        stats["deleted_chunks"] = row[1] or 0
        stats["total_chunks"] = stats["active_chunks"] + stats["deleted_chunks"]
        cur.close()
        conn.close()
    except Exception:
        pass

    sync_info = {"documents_indexed": 0, "total_chunks": 0}
    try:
        from src.sync_state import SyncState
        s = SyncState("data/sync_state.db")
        sync = s.stats()
        sync_info["documents_indexed"] = sync["documents"]
        sync_info["total_chunks"] = sync["chunks"]
    except Exception:
        pass

    try:
        from src.dedup import find_duplicates
        registry = ConnectorRegistry.from_manifest("data/connectors/registry.json")
        result = find_duplicates(registry)
        stats["duplicate_groups"] = result["duplicate_groups"]
    except Exception:
        pass

    return stats, connectors_info, sync_info




def _list_sources_detailed():
    registry = ConnectorRegistry.from_manifest("data/connectors/registry.json")
    entries = registry.list_sources()
    out = []

    for entry in entries:
        info = {
            "name": entry["name"],
            "source_system": entry.get("source_system", entry["name"]),
            "status": entry["status"],
            "document_count": 0,
            "clearances": {},
            "teams": {},
            "error": None,
        }
        if entry["status"] != "loaded":
            info["error"] = entry.get("error", "unknown")
            out.append(info)
            continue

        try:
            connector = registry.get(entry["name"])
            docs = list(connector.list_changed_since(cursor=None))
            info["document_count"] = len(docs)

            clearance_counter = {}
            team_counter = {}
            for d in docs:
                try:
                    acl = connector.get_acl(d["source_id"])
                    cl = acl.get("clearance_level", "INTERNAL")
                    tm = acl.get("owner_team", "unknown")
                    clearance_counter[cl] = clearance_counter.get(cl, 0) + 1
                    team_counter[tm] = team_counter.get(tm, 0) + 1
                except Exception:
                    continue
            info["clearances"] = clearance_counter
            info["teams"] = team_counter
        except Exception as e:
            info["error"] = str(e)[:80]

        out.append(info)

    return out


def _get_source_documents(name: str, limit: int = 100):
    registry = ConnectorRegistry.from_manifest("data/connectors/registry.json")
    try:
        connector = registry.get(name)
    except Exception as e:
        return None, []

    docs_out = []
    try:
        changes = list(connector.list_changed_since(cursor=None))
    except Exception:
        changes = []

    for change in changes[:limit]:
        source_id = change.get("source_id", "")
        entry = {
            "source_id": source_id,
            "title": change.get("title", ""),
            "mime_type": change.get("mime_type", ""),
            "last_modified": change.get("last_modified", ""),
            "clearance_level": "UNKNOWN",
            "owner_team": "unknown",
            "share_scope": "team",
        }
        try:
            acl = connector.get_acl(source_id)
            entry["clearance_level"] = acl.get("clearance_level", "UNKNOWN")
            entry["owner_team"] = acl.get("owner_team", "unknown")
            entry["share_scope"] = acl.get("share_scope", "team")
        except Exception:
            pass
        docs_out.append(entry)

    info = {
        "name": name,
        "source_system": getattr(connector, "SOURCE_SYSTEM", name),
        "document_count": len(changes),
        "clearances": {},
        "teams": {},
    }
    for d in docs_out:
        cl = d["clearance_level"]
        tm = d["owner_team"]
        info["clearances"][cl] = info["clearances"].get(cl, 0) + 1
        info["teams"][tm] = info["teams"].get(tm, 0) + 1

    return info, docs_out


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def dashboard_home(request: Request):
    stats, connectors, sync_state = _gather_stats()
    return templates.TemplateResponse(
        request=request,
        name="overview.html",
        context={
            "active_page": "overview",
            "stats": stats,
            "connectors": connectors,
            "sync_state": sync_state,
        },
    )

@router.get("/sources", response_class=HTMLResponse)
def dashboard_sources(request: Request):
    sources = _list_sources_detailed()
    total_docs = sum(s["document_count"] for s in sources)
    return templates.TemplateResponse(
        request=request,
        name="sources.html",
        context={
            "active_page": "sources",
            "sources": sources,
            "total_docs": total_docs,
        },
    )


@router.get("/sources/{name}", response_class=HTMLResponse)
def dashboard_source_detail(request: Request, name: str):
    info, docs = _get_source_documents(name)
    if info is None:
        return HTMLResponse(
            content=f"<h1>Connector not found: {name}</h1><p><a href='/dashboard/sources'>Back to sources</a></p>",
            status_code=404,
        )
    return templates.TemplateResponse(
        request=request,
        name="source_detail.html",
        context={
            "active_page": "sources",
            "source": info,
            "documents": docs,
        },
    )

@router.get("/chunks", response_class=HTMLResponse)
def dashboard_chunks(
    request: Request,
    q: str = "",
    source: str = "",
    clearance: str = "",
    team: str = "",
    offset: int = 0,
    limit: int = 50,
):
    limit = min(max(limit, 10), 500)
    offset = max(offset, 0)

    filters = {
        "q": q or None,
        "source": source or None,
        "clearance": clearance or None,
        "team": team or None,
    }

    total = count_chunks(
        query=filters["q"],
        source=filters["source"],
        clearance=filters["clearance"],
        team=filters["team"],
    )

    chunks = fetch_chunks(
        query=filters["q"],
        source=filters["source"],
        clearance=filters["clearance"],
        team=filters["team"],
        limit=limit,
        offset=offset,
    )

    sources = list_sources()

    # Build a query string for pagination links
    qs_parts = []
    for k, v in filters.items():
        if v:
            qs_parts.append(f"{k}={v}")
    query_string = "&".join(qs_parts)

    return templates.TemplateResponse(
        request=request,
        name="chunks.html",
        context={
            "active_page": "chunks",
            "chunks": chunks,
            "total": total,
            "offset": offset,
            "limit": limit,
            "filters": filters,
            "sources": sources,
            "query_string": query_string,
        },
    )

@router.get("/permissions", response_class=HTMLResponse)
def dashboard_permissions(request: Request):
    matrix = build_matrix()
    return templates.TemplateResponse(
        request=request,
        name="permissions.html",
        context={
            "active_page": "permissions",
            "teams": matrix["teams"],
            "sources": matrix["sources"],
            "cells": matrix["cells"],
        },
    )


@router.get("/permissions/{team}/{source}", response_class=HTMLResponse)
def dashboard_permissions_detail(request: Request, team: str, source: str):
    chunks = get_accessible_chunks(team, source)
    return templates.TemplateResponse(
        request=request,
        name="permissions_detail.html",
        context={
            "active_page": "permissions",
            "team": team,
            "source": source,
            "chunks": chunks,
        },
    )

@router.get("/users", response_class=HTMLResponse)
def dashboard_users(request: Request):
    users = list_users_with_access_counts()
    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context={
            "active_page": "users",
            "users": users,
        },
    )


@router.get("/users/{user_id}", response_class=HTMLResponse)
def dashboard_user_detail(request: Request, user_id: str):
    user, chunks = get_user_chunks(user_id)
    if user is None:
        return HTMLResponse(
            content=f"<h1>User not found: {user_id}</h1><p><a href='/dashboard/users'>Back to users</a></p>",
            status_code=404,
        )
    total_chunks = 72  # baseline; could be computed from a count query
    return templates.TemplateResponse(
        request=request,
        name="user_detail.html",
        context={
            "active_page": "users",
            "user": user,
            "chunks": chunks,
            "total_chunks": total_chunks,
        },
    )

@router.get("/duplicates", response_class=HTMLResponse)
def dashboard_duplicates(request: Request):
    stats = get_duplicates_summary()
    return templates.TemplateResponse(
        request=request,
        name="duplicates.html",
        context={
            "active_page": "duplicates",
            "stats": stats,
        },
    )

@router.get("/pipeline", response_class=HTMLResponse)
def dashboard_pipeline(request: Request):
    sync = read_sync_state()
    connectors = read_connector_status()
    runs = read_recent_runs()
    return templates.TemplateResponse(
        request=request,
        name="pipeline.html",
        context={
            "active_page": "pipeline",
            "sync": sync,
            "connectors": connectors,
            "runs": runs,
        },
    )


from fastapi import Form
from fastapi.responses import RedirectResponse


@router.post("/pipeline/run")
def dashboard_pipeline_run(dry_run: str = Form("false")):
    is_dry = dry_run.lower() == "true"
    try:
        run_pipeline_now(dry_run=is_dry)
    except Exception as e:
        print(f"Pipeline run failed: {e}")
    return RedirectResponse(url="/dashboard/pipeline", status_code=303)

@router.get("/metrics", response_class=HTMLResponse)
def dashboard_metrics(request: Request):
    import json as _json
    summary = summary_metrics()
    routes = tokens_by_route()
    latency = latency_buckets()
    requests = recent_requests(20)

    return templates.TemplateResponse(
        request=request,
        name="metrics.html",
        context={
            "active_page": "metrics",
            "summary": summary,
            "routes_json": _json.dumps(routes),
            "latency_json": _json.dumps(latency),
            "requests": requests,
        },
    )


@router.get("/architecture", response_class=HTMLResponse)
def dashboard_architecture(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="architecture.html",
        context={
            "active_page": "architecture",
        },
    )

# ---------------------------------------------------------------------------
# 7.22 — Login / logout (public_router, ungated)
# ---------------------------------------------------------------------------

@public_router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, error: int = 0):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": bool(error)},
    )


@public_router.post("/login")
def login_submit(
    user_id: str = Form(...),
    password: str = Form(...),
):
    user = verify_credentials(user_id, password)
    if user is None:
        return RedirectResponse(url="/dashboard/login?error=1", status_code=303)

    response = RedirectResponse(url="/dashboard", status_code=303)
    set_session_cookie(response, user["user_id"], user["role"], user["tenant_id"])
    return response


@public_router.get("/logout")
def logout():
    response = RedirectResponse(url="/dashboard/login", status_code=303)
    clear_session_cookie(response)
    # 7.22 — tell the browser to drop cookies for this origin on logout.
    # We use "cookies" (not "cache") because Cache-Control: no-store on
    # /dashboard/* already prevents gated pages from being cached.
    response.headers["Clear-Site-Data"] = '"cookies"'
    return response


@router.get("/security", response_class=HTMLResponse)
def dashboard_security(request: Request):
    import json as _json
    from src.dashboard.security_query import (
        summary as _summary,
        blocks_by_category as _by_cat,
        blocks_by_source as _by_src,
        recent_blocks as _recent,
    )
    return templates.TemplateResponse(
        request=request,
        name="security.html",
        context={
            "active_page": "security",
            "summary": _summary(),
            "cat_json": _json.dumps(_by_cat()),
            "src_json": _json.dumps(_by_src()),
            "blocks": _recent(50),
        },
    )
