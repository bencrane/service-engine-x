"""Authentication dependencies for FastAPI."""

import hmac
import secrets
from dataclasses import dataclass

from fastapi import Header, HTTPException, Query, status

from app.auth.jwt import decode_access_token, decode_m2m_token
from app.config import settings


@dataclass
class AuthContext:
    """Authentication context containing org and user info."""

    org_id: str
    user_id: str
    role: str = ""
    auth_method: str = "shared_token"


@dataclass
class InternalCallerContext:
    """Identity context for non-interactive backend callers authenticated via
    the static internal bearer (serx-mcp, Trigger.dev cron). No user, no org —
    this caller is the platform itself.
    """

    caller: str = "internal"


def _extract_bearer_token(authorization: str | None) -> str | None:
    """Extract token from ``Authorization: Bearer <token>``."""
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def _check_token(authorization: str | None) -> None:
    """
    Validate the legacy shared bearer token. Returns distinct 401 details so
    the caller can tell missing-header from malformed-header from mismatch.
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


async def require_internal_bearer(
    authorization: str | None = Header(None, alias="Authorization"),
) -> InternalCallerContext:
    """Static-bearer auth for non-interactive backend callers.

    Validates ``Authorization: Bearer <token>`` against
    ``settings.SERX_INTERNAL_BEARER_TOKEN`` via constant-time comparison.
    No DB lookup. No JWT verification. No user/org context.
    """
    expected = settings.SERX_INTERNAL_BEARER_TOKEN
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="server_misconfigured: SERX_INTERNAL_BEARER_TOKEN not set on API",
        )

    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_or_malformed_authorization_header",
        )

    if not hmac.compare_digest(token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_internal_bearer",
        )

    return InternalCallerContext()


async def get_current_auth_jwt(
    authorization: str | None = Header(None, alias="Authorization"),
    org_id: str = Query(..., description="Target organization UUID"),
    user_id: str = Query(..., description="Acting user UUID"),
) -> AuthContext:
    """JWT-verified auth for authenticated CRUD routes.

    Validates a bearer JWT issued by auth-engine-x (EdDSA, JWKS-verified) and
    returns an :class:`AuthContext` shaped like :func:`get_current_org` so
    routers can keep reading ``auth.org_id`` / ``auth.user_id`` / ``auth.role``
    during the migration.

    Wiring is deferred to Phase 2/3; this dependency is exported but not yet
    attached to routes. Existing query-layer ``org_id`` filters keep working.

    Both session JWTs (``type=session``) and M2M JWTs (``type=m2m``) are
    accepted. ``org_id`` and ``user_id`` are still passed as query params for
    Phase 1 backward compatibility — when the token carries an ``org_id``
    claim it must agree with the query, and session tokens must agree on
    ``user_id``.
    """
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_or_malformed_authorization_header",
        )

    payload = decode_access_token(token)
    auth_method = "session"
    if payload is None:
        payload = decode_m2m_token(token)
        auth_method = "m2m"

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_or_expired_token",
        )

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_sub_claim",
        )

    claim_org_id = payload.get("org_id")
    if claim_org_id and claim_org_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="org_id_mismatch_with_token",
        )

    if auth_method == "session" and sub != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id_mismatch_with_token",
        )

    return AuthContext(
        org_id=org_id,
        user_id=user_id,
        role=payload.get("role", ""),
        auth_method=auth_method,
    )


def _matches_legacy_token(token: str) -> bool:
    """Constant-time check against ``SERX_AUTH_TOKEN``. Returns False when the
    secret is unset (so missing-config never silently authorizes anyone).
    """
    expected = settings.SERX_AUTH_TOKEN
    if not expected:
        return False
    return secrets.compare_digest(token, expected)


def _matches_internal_bearer(token: str) -> bool:
    """Constant-time check against ``SERX_INTERNAL_BEARER_TOKEN``. Returns
    False when the secret is unset.
    """
    expected = settings.SERX_INTERNAL_BEARER_TOKEN
    if not expected:
        return False
    return hmac.compare_digest(token, expected)


async def verify_token_or_internal_bearer(
    authorization: str | None = Header(None, alias="Authorization"),
) -> None:
    """Transitional auth dep for internal routes during the SERX_AUTH_TOKEN →
    SERX_INTERNAL_BEARER_TOKEN cutover.

    Accepts either token (constant-time comparison). Once all callers have
    moved to ``SERX_INTERNAL_BEARER_TOKEN`` (Phase 3), routes swap to
    :func:`require_internal_bearer` and the legacy path is removed.

    Returns ``None`` to keep the call shape identical to ``verify_token``.
    """
    if not settings.SERX_AUTH_TOKEN and not settings.SERX_INTERNAL_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "server_misconfigured: neither SERX_AUTH_TOKEN nor "
                "SERX_INTERNAL_BEARER_TOKEN is set on API"
            ),
        )

    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_or_malformed_authorization_header",
        )

    if _matches_internal_bearer(token) or _matches_legacy_token(token):
        return None

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token_mismatch",
    )


async def get_current_org_or_internal_bearer(
    authorization: str | None = Header(None, alias="Authorization"),
    org_id: str = Query(..., description="Target organization UUID"),
    user_id: str = Query(..., description="Acting user UUID"),
) -> AuthContext:
    """Transitional auth dep for tenant CRUD routes during cutover.

    Accepts either ``SERX_AUTH_TOKEN`` (legacy) or ``SERX_INTERNAL_BEARER_TOKEN``
    (new). In both cases the caller-supplied ``org_id`` / ``user_id`` query
    params drive the returned :class:`AuthContext`, matching the existing
    :func:`get_current_org` behavior so routers can swap deps without changing
    function bodies. ``auth_method`` records which bearer authorized the call,
    which is useful for migration telemetry.

    Removed in Phase 3 once callers have moved off ``SERX_AUTH_TOKEN``.
    """
    if not settings.SERX_AUTH_TOKEN and not settings.SERX_INTERNAL_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "server_misconfigured: neither SERX_AUTH_TOKEN nor "
                "SERX_INTERNAL_BEARER_TOKEN is set on API"
            ),
        )

    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_or_malformed_authorization_header",
        )

    if _matches_internal_bearer(token):
        return AuthContext(
            org_id=org_id,
            user_id=user_id,
            auth_method="internal_bearer",
        )

    if _matches_legacy_token(token):
        return AuthContext(
            org_id=org_id,
            user_id=user_id,
            auth_method="shared_token",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token_mismatch",
    )


# Legacy alias retained so existing routers keep their current behavior during
# Phase 1. Routes are migrated to ``get_current_auth_jwt`` in Phase 2/3.
get_current_auth = get_current_org
