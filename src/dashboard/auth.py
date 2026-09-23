"""
Dashboard session auth.

Wraps src.auth's JWT logic for HTML pages. The browser cannot send
Authorization: Bearer headers on <a href> navigation, so we deliver
the same JWT via an httponly cookie.

Credentials are loaded from DASHBOARD_USERS (env), format:
    user_id:password:role:tenant_id[,...]
Example:
    DASHBOARD_USERS=admin:changeme:admin:acme
"""
import os
from typing import Optional

from fastapi import Request
from fastapi.responses import RedirectResponse

from src.auth import ROLE_CLEARANCE, decode_token, issue_token

SESSION_COOKIE = "rag_session"


def _load_users() -> dict[str, dict]:
    """Parse DASHBOARD_USERS env var. Falls back to dev default."""
    raw = os.getenv("DASHBOARD_USERS", "admin:changeme:admin:acme")
    users: dict[str, dict] = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(":")
        if len(parts) != 4:
            continue
        user_id, password, role, tenant_id = parts
        if role not in ROLE_CLEARANCE:
            continue
        users[user_id] = {
            "password": password,
            "role": role,
            "tenant_id": tenant_id,
        }
    return users


def verify_credentials(user_id: str, password: str) -> Optional[dict]:
    """Return user dict if credentials valid, else None."""
    users = _load_users()
    u = users.get(user_id)
    if u is None:
        return None
    if u["password"] != password:
        return None
    return {
        "user_id": user_id,
        "role": u["role"],
        "tenant_id": u["tenant_id"],
        "clearance": ROLE_CLEARANCE[u["role"]],
    }


def set_session_cookie(response, user_id: str, role: str, tenant_id: str) -> None:
    token = issue_token(user_id, role, tenant_id)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,   # dev only; set True behind HTTPS in prod
        max_age=60 * 60,
        path="/",
    )


def clear_session_cookie(response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/")


def require_dashboard_user(request: Request) -> dict:
    """
    FastAPI dependency for HTML dashboard routes.

    Reads the session cookie, decodes the JWT, checks role == admin.
    On any failure, redirects to /dashboard/login (302) — this is an
    HTML surface, so a redirect is friendlier than a 401 JSON blob.
    """
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise _redirect_to_login()
    try:
        payload = decode_token(token)
    except Exception:
        raise _redirect_to_login()

    role = payload.get("role")
    if role != "admin":
        raise _redirect_to_login()

    return {
        "user_id": payload["sub"],
        "role": role,
        "tenant_id": payload["tenant_id"],
        "clearance": ROLE_CLEARANCE.get(role, "PUBLIC"),
    }


def _redirect_to_login() -> Exception:
    # FastAPI will treat a raised HTTPException; but we want a real
    # 302 with Location. Return a special sentinel the route wrapper
    # catches. Simpler: raise HTTPException with a custom status.
    from fastapi import HTTPException, status
    return HTTPException(
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        detail="Login required",
        headers={"Location": "/dashboard/login"},
    )
