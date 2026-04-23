"""Authentication dependencies for FastAPI."""

import secrets
from dataclasses import dataclass

from fastapi import Header, HTTPException, Query, status

from app.config import settings


@dataclass
class AuthContext:
    """Authentication context containing org and user info."""

    org_id: str
    user_id: str


def _check_token(authorization: str | None) -> None:
    """
    Validate the bearer token. Returns distinct 401 details so the caller
    can tell the difference between a missing header, a malformed header,
    a missing server secret, and a token mismatch.
    """
    if not settings.SERX_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="server_misconfigured: SERX_AUTH_TOKEN not set on API",
        )

    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_authorization_header",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="malformed_authorization_header: expected 'Bearer <token>'",
        )

    token = authorization[7:]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="empty_bearer_token",
        )

    if not secrets.compare_digest(token, settings.SERX_AUTH_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token_mismatch: Bearer value does not match SERX_AUTH_TOKEN",
        )


async def verify_token(
    authorization: str | None = Header(None, alias="Authorization"),
) -> None:
    """Validate the shared API token. Token-only, no org/user scoping."""
    _check_token(authorization)


async def get_current_org(
    authorization: str | None = Header(None, alias="Authorization"),
    org_id: str = Query(..., description="Target organization UUID"),
    user_id: str = Query(..., description="Acting user UUID"),
) -> AuthContext:
    """
    Validate the shared API token and return caller-supplied org/user context.

    Token proves the caller is trusted; org_id and user_id say which slice
    of data to operate on. Caller is responsible for those IDs being valid.
    """
    _check_token(authorization)
    return AuthContext(org_id=org_id, user_id=user_id)


get_current_auth = get_current_org
