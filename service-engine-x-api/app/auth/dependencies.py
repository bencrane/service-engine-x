"""Authentication dependencies for FastAPI."""

from dataclasses import dataclass
from datetime import datetime, timezone

import jwt as pyjwt
from fastapi import Header, HTTPException, status

from app.auth.jwt import decode_access_token
from app.auth.utils import extract_bearer_token, hash_token
from app.database import get_supabase


@dataclass
class AuthContext:
    """Authentication context containing org and user info."""

    org_id: str
    user_id: str
    token_id: str | None = None
    auth_method: str = "api_token"  # "api_token" or "session"


def _validate_api_token(token: str) -> AuthContext | None:
    """
    Validate an API token (SHA-256 hashed bearer token).

    Returns AuthContext on success, None if token not found or expired.
    """
    token_hash = hash_token(token)
    supabase = get_supabase()

    result = (
        supabase.table("api_tokens")
        .select("id, user_id, org_id, expires_at")
        .eq("token_hash", token_hash)
        .execute()
    )

    if not result.data or len(result.data) == 0:
        return None

    token_data = result.data[0]

    # Check expiration
    if token_data.get("expires_at"):
        expires_at = datetime.fromisoformat(token_data["expires_at"].replace("Z", "+00:00"))
        if expires_at < datetime.now(timezone.utc):
            return None

    # Update last_used_at
    supabase.table("api_tokens").update(
        {"last_used_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", token_data["id"]).execute()

    return AuthContext(
        org_id=token_data["org_id"],
        user_id=token_data["user_id"],
        token_id=token_data["id"],
        auth_method="api_token",
    )


def _validate_jwt(token: str) -> AuthContext | None:
    """
    Validate a JWT session token.

    Returns AuthContext on success, None if token is invalid or expired.
    """
    try:
        payload = decode_access_token(token)
    except (pyjwt.ExpiredSignatureError, pyjwt.InvalidTokenError):
        return None

    # Ensure this is a session token, not something else
    if payload.get("type") != "session":
        return None

    user_id = payload.get("sub")
    org_id = payload.get("org_id")

    if not user_id or not org_id:
        return None

    return AuthContext(
        org_id=org_id,
        user_id=user_id,
        token_id=None,
        auth_method="session",
    )


async def get_current_org(
    authorization: str | None = Header(None, alias="Authorization"),
) -> AuthContext:
    """
    Validate API token and return authentication context.

    This is the original auth dependency — API tokens only.
    Kept for backwards compatibility with machine-to-machine integrations.
    """
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    auth = _validate_api_token(token)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    return auth


async def get_current_user(
    authorization: str | None = Header(None, alias="Authorization"),
) -> AuthContext:
    """
    Validate JWT session token and return authentication context.

    Use this for endpoints that require a logged-in user session (customer portal).
    """
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    auth = _validate_jwt(token)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    return auth


async def get_current_auth(
    authorization: str | None = Header(None, alias="Authorization"),
) -> AuthContext:
    """
    Dual auth: accepts either a JWT session token or an API token.

    Tries JWT first (cheap — no DB call), falls back to API token lookup.
    Use this on any endpoint that should accept both auth methods.
    """
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    # Try JWT first (no DB call — fast path)
    auth = _validate_jwt(token)
    if auth:
        return auth

    # Fall back to API token
    auth = _validate_api_token(token)
    if auth:
        return auth

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
    )
