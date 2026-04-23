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


def _extract_bearer(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization[7:]


def _check_token(authorization: str | None) -> None:
    token = _extract_bearer(authorization)
    expected = settings.SERX_AUTH_TOKEN
    if not token or not expected or not secrets.compare_digest(token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )


async def verify_token(
    authorization: str | None = Header(None, alias="Authorization"),
) -> None:
    """
    Validate the shared API token. Token-only, no org/user scoping.

    Use this for endpoints that don't operate on a specific org
    (listing all orgs/users, scheduler dispatch, webhook receivers, etc.).
    """
    _check_token(authorization)


async def get_current_org(
    authorization: str | None = Header(None, alias="Authorization"),
    org_id: str = Query(..., description="Target organization UUID"),
    user_id: str = Query(..., description="Acting user UUID"),
) -> AuthContext:
    """
    Validate the shared API token and return caller-supplied org/user context.

    The caller is trusted (single-consumer deployment). Token proves the caller
    is hq-ops-internal-app; org_id and user_id say which slice of data to operate on.
    """
    _check_token(authorization)
    return AuthContext(org_id=org_id, user_id=user_id)


get_current_auth = get_current_org
