"""AegisX identity, session and per-tool authorization helpers.

POC uses PBKDF2-HMAC-SHA256 for password storage and opaque bearer sessions.
Production should use an enterprise IdP (OIDC/SAML), MFA/WebAuthn and PAM.
"""
import base64, hashlib, hmac, os, secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from ..models import UserAccount, UserToolPermission, UserSession

SESSION_HOURS = int(os.getenv("VEYRA_SESSION_HOURS", "8"))
PBKDF2_ROUNDS = 310_000

def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${PBKDF2_ROUNDS}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, rounds, salt_b64, digest_b64 = encoded.split("$", 3)
        if scheme != "pbkdf2_sha256": return False
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(rounds))
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False

def issue_session(db: Session, user: UserAccount) -> str:
    raw = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    db.add(UserSession(token_hash=token_hash, user_id=user.id,
                       expires_at=datetime.now(timezone.utc)+timedelta(hours=SESSION_HOURS)))
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return raw

def current_user(request: Request, db: Session) -> UserAccount:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Login required")
    raw = auth[7:].strip()
    if not raw: raise HTTPException(401, "Login required")
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    session = db.query(UserSession).filter(UserSession.token_hash == token_hash).first()
    now = datetime.now(timezone.utc)
    if not session or session.revoked_at is not None:
        raise HTTPException(401, "Session expired or revoked")
    expiry = session.expires_at
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if expiry < now:
        raise HTTPException(401, "Session expired or revoked")
    user = db.get(UserAccount, session.user_id)
    if not user or user.status != "active": raise HTTPException(403, "User disabled")
    return user

def require_sudo(request: Request, db: Session) -> UserAccount:
    user = current_user(request, db)
    if user.role != "sudo": raise HTTPException(403, "Sudo administrator authorization required")
    return user

def require_role(request: Request, db: Session, roles: set[str]) -> UserAccount:
    user = current_user(request, db)
    if user.role not in roles: raise HTTPException(403, "Insufficient role privileges")
    return user

def _expiry_active(expires_at) -> bool:
    if expires_at is None:
        return True
    exp = expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return exp > datetime.now(timezone.utc)

def get_tool_level(db: Session, user_id: int, tool_id: str) -> str:
    row = db.query(UserToolPermission).filter(UserToolPermission.user_id==user_id, UserToolPermission.tool_id==tool_id).first()
    if not row or row.level in (None, "", "none"):
        return "none"
    if not _expiry_active(row.expires_at):
        return "none"
    return row.level

def effective_tool_level(db: Session, user: UserAccount, tool_id: str) -> str:
    """Sudo holds every tool at execute_request with no expiry; everyone else
    is bound to their explicit (possibly time-boxed) grant. No grant = none."""
    if user.role == "sudo":
        return "execute_request"
    return get_tool_level(db, user.id, tool_id)

def grant_expiry(hours: float | None) -> datetime | None:
    if hours is None:
        return None
    return datetime.now(timezone.utc) + timedelta(hours=max(float(hours), 0.05))
