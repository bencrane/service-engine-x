"""Tests for SERX auth dependencies after the AUX M2M cutover.

Verification is delegated to ``aux_m2m_server`` — these tests patch
``app.auth.dependencies._verify`` so they don't need a live JWKS endpoint.

Two deps are exercised:

* ``verify_token`` — no-org dep used by ``/api/internal/**``,
  ``/api/orgs``, ``/api/users``.
* ``get_current_org`` (alias ``get_current_auth``) — tenant-CRUD dep that
  also reads ``org_id`` / ``user_id`` from query params.

Both accept a session JWT or a system-actor M2M JWT; both reject anything
else with 401. Org-scoped M2M is rejected because SERX has no org-scoped
machine callers today.
"""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.auth.dependencies import (
    AuthContext,
    INTERNAL_CALLER_USER_ID,
    get_current_org,
    verify_token,
)


def _run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


def _session_claims(*, sub: str = "user-1", org_id: str = "org-1") -> dict:
    return {"type": "session", "sub": sub, "org_id": org_id, "role": "admin"}


def _system_m2m_claims() -> dict:
    return {"type": "m2m", "actor_type": "system_service", "sub": "service:serx-mcp"}


def _org_m2m_claims() -> dict:
    return {"type": "m2m", "actor_type": "org_service", "sub": "service:partner",
            "org_id": "org-1"}


# ── verify_token (no-org dep) ───────────────────────────────────────────


def test_verify_token_session_jwt_passes() -> None:
    with patch("app.auth.dependencies._verify", return_value=_session_claims()):
        result = _run(verify_token(authorization="Bearer abc"))
    assert result is None


def test_verify_token_system_m2m_passes() -> None:
    with patch("app.auth.dependencies._verify", return_value=_system_m2m_claims()):
        result = _run(verify_token(authorization="Bearer abc"))
    assert result is None


def test_verify_token_org_scoped_m2m_rejected() -> None:
    with patch("app.auth.dependencies._verify", return_value=_org_m2m_claims()):
        with pytest.raises(HTTPException) as exc:
            _run(verify_token(authorization="Bearer abc"))
    assert exc.value.status_code == 401


def test_verify_token_invalid_token_returns_401() -> None:
    with patch("app.auth.dependencies._verify", return_value=None):
        with pytest.raises(HTTPException) as exc:
            _run(verify_token(authorization="Bearer wrong"))
    assert exc.value.status_code == 401


def test_verify_token_missing_header_returns_401() -> None:
    with pytest.raises(HTTPException) as exc:
        _run(verify_token(authorization=None))
    assert exc.value.status_code == 401


def test_verify_token_malformed_header_returns_401() -> None:
    with pytest.raises(HTTPException) as exc:
        _run(verify_token(authorization="Token abc"))
    assert exc.value.status_code == 401


# ── get_current_org (tenant-CRUD dep) ───────────────────────────────────


def test_get_current_org_session_happy_path() -> None:
    with patch(
        "app.auth.dependencies._verify",
        return_value=_session_claims(sub="user-1", org_id="org-1"),
    ):
        ctx = _run(get_current_org(
            authorization="Bearer abc", org_id="org-1", user_id="user-1",
        ))
    assert isinstance(ctx, AuthContext)
    assert ctx.org_id == "org-1"
    assert ctx.user_id == "user-1"
    assert ctx.auth_method == "session"
    assert ctx.role == "admin"


def test_get_current_org_session_org_id_mismatch_returns_403() -> None:
    with patch(
        "app.auth.dependencies._verify",
        return_value=_session_claims(org_id="org-A"),
    ):
        with pytest.raises(HTTPException) as exc:
            _run(get_current_org(
                authorization="Bearer abc", org_id="org-B", user_id="user-1",
            ))
    assert exc.value.status_code == 403
    assert exc.value.detail == "org_id_mismatch_with_token"


def test_get_current_org_session_user_id_mismatch_returns_403() -> None:
    with patch(
        "app.auth.dependencies._verify",
        return_value=_session_claims(sub="user-1"),
    ):
        with pytest.raises(HTTPException) as exc:
            _run(get_current_org(
                authorization="Bearer abc", org_id="org-1", user_id="someone-else",
            ))
    assert exc.value.status_code == 403
    assert exc.value.detail == "user_id_mismatch_with_token"


def test_get_current_org_system_m2m_trusts_query_params() -> None:
    """System-actor M2M is org-agnostic — the caller-supplied org_id /
    user_id are accepted as request scope without cross-checking the token."""
    with patch("app.auth.dependencies._verify", return_value=_system_m2m_claims()):
        ctx = _run(get_current_org(
            authorization="Bearer abc",
            org_id="any-org",
            user_id="any-user",
        ))
    assert ctx.org_id == "any-org"
    assert ctx.user_id == "any-user"
    assert ctx.auth_method == "system_m2m"
    assert ctx.role == "org_admin"


def test_get_current_org_org_scoped_m2m_rejected() -> None:
    with patch("app.auth.dependencies._verify", return_value=_org_m2m_claims()):
        with pytest.raises(HTTPException) as exc:
            _run(get_current_org(
                authorization="Bearer abc", org_id="org-1", user_id="user-1",
            ))
    assert exc.value.status_code == 401


def test_get_current_org_invalid_token_returns_401() -> None:
    with patch("app.auth.dependencies._verify", return_value=None):
        with pytest.raises(HTTPException) as exc:
            _run(get_current_org(
                authorization="Bearer wrong", org_id="org-1", user_id="user-1",
            ))
    assert exc.value.status_code == 401


def test_get_current_org_missing_header_returns_401() -> None:
    with pytest.raises(HTTPException) as exc:
        _run(get_current_org(
            authorization=None, org_id="org-1", user_id="user-1",
        ))
    assert exc.value.status_code == 401


# ── INTERNAL_CALLER_USER_ID is exported (smoke) ─────────────────────────


def test_internal_caller_user_id_constant_is_a_uuid_string() -> None:
    """Sentinel UUID kept stable across the cutover so any historical
    consumers comparing against it keep working."""
    assert INTERNAL_CALLER_USER_ID == "00000000-0000-0000-0000-000000000000"
