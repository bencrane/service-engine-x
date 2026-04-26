"""Authentication dependencies for FastAPI.

Verification is delegated to ``aux_m2m_server`` (single canonical JWKS
verifier shared across every AUX backend). All authenticated routes accept
either:

* a session JWT issued by auth-engine-x (HQ-frontend operator), or
* a system-actor M2M JWT (``type=m2m`` / ``actor_type=system_service``)
  minted by a sibling backend or MCP via ``aux_m2m_client.AsyncM2MAuth``.

Org-scoped M2M tokens are not used to call SERX today — every machine caller
is a system actor (serx-mcp, OPEX scheduler, etc.). Per-tenant request scope
is supplied by the caller as ``org_id`` / ``user_id`` query params on tenant
CRUD routes; the bearer is fully trusted there.

The legacy ``SERX_AUTH_TOKEN`` and ``SERX_INTERNAL_BEARER_TOKEN`` static
bearers were removed in this cutover.

Symbol shape:

* ``AuthContext`` — caller identity for every authenticated route.
* ``verify_token`` — no-org dep used by ``/api/internal/**``, ``/api/orgs``,
  ``/api/users``. Returns ``None``; routes that just need to gate access
  without consuming caller identity use it as ``Depends(verify_token)``.
* ``get_current_auth`` / ``get_current_org`` — tenant-CRUD dep that also
  reads ``org_id`` and ``user_id`` from query params. Both names are kept
  as aliases of the same function so existing routers don't have to be
  rewritten.
"""

from dataclasses import dataclass
from typing import Any

from aux_m2m_server import get_verifier, is_m2m, is_session
from aux_m2m_server.errors import TokenVerificationError
from fastapi import Header, HTTPException, Query, status


# ── identity contexts ───────────────────────────────────────────────────


INTERNAL_CALLER_USER_ID = "00000000-0000-0000-0000-000000000000"


@dataclass
class AuthContext:
    """Authentication context returned by SERX auth deps.

    ``org_id`` and ``user_id`` are populated for tenant-CRUD routes (read
    from query params on ``get_current_org``). ``role`` is the role claim
    on session tokens, ``"org_admin"`` for synthesized system-M2M callers.
    """

    org_id: str | None
    user_id: str | None
    role: str = ""
    auth_method: str = "session"  # session | system_m2m


# ── helpers ─────────────────────────────────────────────────────────────


def _extract_bearer_token(authorization: str | None) -> str | None:
    """Extract token from ``Authorization: Bearer <token>``."""
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def _verify(token: str) -> dict[str, Any] | None:
    """Verify a JWT via the shared JWKS verifier. Returns claims or ``None``."""
    try:
        return get_verifier().verify(token)
    except TokenVerificationError:
        return None


def _verify_session_or_system_m2m(authorization: str | None) -> dict[str, Any]:
    """Return verified claims for a session OR ``system_service`` M2M JWT.

    Raises ``HTTPException(401)`` for any other state — missing header,
    malformed header, invalid token, expired token, or org-scoped M2M
    (which SERX does not accept).
    """
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_or_malformed_authorization_header",
        )
    claims = _verify(token)
    if claims is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_or_expired_token",
        )
    if is_session(claims):
        return claims
    if is_m2m(claims) and str(claims.get("actor_type", "")) == "system_service":
        return claims
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="session_or_system_m2m_token_required",
    )


# ── deps ────────────────────────────────────────────────────────────────


async def verify_token(
    authorization: str | None = Header(None, alias="Authorization"),
) -> None:
    """No-org auth dep for routes that don't take request-scope query params.

    Used by ``/api/internal/**``, ``/api/orgs``, ``/api/users`` —
    backend-callable surfaces where org/user is either irrelevant (admin
    listing) or supplied separately via path/body.

    Accepts a session JWT (HQ frontend) or a ``system_service`` M2M JWT
    (serx-mcp / OPEX scheduler). Any other token shape is 401.
    """
    _verify_session_or_system_m2m(authorization)


async def get_current_org(
    authorization: str | None = Header(None, alias="Authorization"),
    org_id: str = Query(..., description="Target organization UUID"),
    user_id: str = Query(..., description="Acting user UUID"),
) -> AuthContext:
    """Tenant-CRUD auth dep.

    Verifies a session or system-M2M JWT and reads caller-supplied
    ``org_id`` / ``user_id`` query params. When the token carries an
    ``org_id`` claim it must match the query; session tokens must agree on
    ``user_id`` (``sub``). System-M2M tokens are org-agnostic — the query
    params are accepted as caller-supplied scope.
    """
    claims = _verify_session_or_system_m2m(authorization)
    if is_session(claims):
        claim_org = claims.get("org_id")
        if claim_org and claim_org != org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="org_id_mismatch_with_token",
            )
        sub = claims.get("sub")
        if sub and sub != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="user_id_mismatch_with_token",
            )
        return AuthContext(
            org_id=org_id,
            user_id=user_id,
            role=str(claims.get("role", "")),
            auth_method="session",
        )

    # system_service M2M
    return AuthContext(
        org_id=org_id,
        user_id=user_id,
        role="org_admin",
        auth_method="system_m2m",
    )


# Routers historically import ``get_current_auth``; keep it as an alias of
# ``get_current_org`` so we don't have to touch every router file just to
# rename the symbol.
get_current_auth = get_current_org
