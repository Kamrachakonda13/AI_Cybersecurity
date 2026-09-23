import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-this-in-production-min-32-chars")
JWT_ALGORITHM = "HS256"
JWT_EXP_MINUTES = 60

ROLE_CLEARANCE = {
    "junior": "PUBLIC",
    "manager": "INTERNAL",
    "csuite": "CONFIDENTIAL",
    "admin": "RESTRICTED",
}

bearer_scheme = HTTPBearer(auto_error=False)


def issue_token(user_id: str, role: str, tenant_id: str) -> str:
    if role not in ROLE_CLEARANCE:
        raise ValueError(f"Unknown role: {role}")

    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "tenant_id": tenant_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXP_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
        )


def current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )
    payload = decode_token(credentials.credentials)
    role = payload.get("role")
    if role not in ROLE_CLEARANCE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Unknown role: {role}",
        )
    return {
        "user_id": payload["sub"],
        "role": role,
        "tenant_id": payload["tenant_id"],
        "clearance": ROLE_CLEARANCE[role],
    }


if __name__ == "__main__":
    t = issue_token("alice", "manager", "acme")
    print("Token issued, length:", len(t))
    print("Payload:", decode_token(t))