"""Focused tests for the Phase 1 auth additions.

Covers:
- ``require_internal_bearer`` static-bearer dependency.
- ``get_current_auth_jwt`` JWT dependency: missing/invalid/expired tokens.

JWKS verification itself is covered by patching ``decode_access_token`` and
``decode_m2m_token`` so tests do not depend on a live JWKS endpoint.
"""

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.dependencies import (
    AuthContext,
    InternalCallerContext,
    get_current_auth_jwt,
    require_internal_bearer,
)
from app.config import settings


@pytest.fixture
def internal_app() -> FastAPI:
    """Tiny app exposing the two new deps for direct HTTP testing."""
    app = FastAPI()

    @app.get("/internal-only")
    def internal_only(
        ctx: InternalCallerContext = __import__("fastapi").Depends(require_internal_bearer),
    ) -> dict:
        return {"caller": ctx.caller}

    @app.get("/jwt-only")
    def jwt_only(
        auth: AuthContext = __import__("fastapi").Depends(get_current_auth_jwt),
    ) -> dict:
        return {
            "org_id": auth.org_id,
            "user_id": auth.user_id,
            "auth_method": auth.auth_method,
            "role": auth.role,
        }

    return app


def test_settings_require_internal_bearer_token_at_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    """``SERX_INTERNAL_BEARER_TOKEN`` is required: ``Settings()`` must raise
    when the env var is unset, so the app fails to boot rather than serving
    traffic with a missing secret.
    """
    from pydantic import ValidationError

    from app.config import Settings

    monkeypatch.delenv("SERX_INTERNAL_BEARER_TOKEN", raising=False)
    with pytest.raises(ValidationError) as exc_info:
        Settings()  # type: ignore[call-arg]
    assert "SERX_INTERNAL_BEARER_TOKEN" in str(exc_info.value)


def test_internal_bearer_missing_header_returns_401(internal_app: FastAPI) -> None:
    with patch.object(settings, "SERX_INTERNAL_BEARER_TOKEN", "secret-value"):
        client = TestClient(internal_app)
        r = client.get("/internal-only")
        assert r.status_code == 401


def test_internal_bearer_wrong_token_returns_401(internal_app: FastAPI) -> None:
    with patch.object(settings, "SERX_INTERNAL_BEARER_TOKEN", "secret-value"):
        client = TestClient(internal_app)
        r = client.get("/internal-only", headers={"Authorization": "Bearer wrong"})
        assert r.status_code == 401
        assert r.json()["detail"] == "invalid_internal_bearer"


def test_internal_bearer_correct_token_returns_200(internal_app: FastAPI) -> None:
    with patch.object(settings, "SERX_INTERNAL_BEARER_TOKEN", "secret-value"):
        client = TestClient(internal_app)
        r = client.get("/internal-only", headers={"Authorization": "Bearer secret-value"})
        assert r.status_code == 200
        assert r.json() == {"caller": "internal"}


def test_jwt_dep_missing_header_returns_401(internal_app: FastAPI) -> None:
    client = TestClient(internal_app)
    r = client.get("/jwt-only", params={"org_id": "o", "user_id": "u"})
    assert r.status_code == 401


def test_jwt_dep_invalid_token_returns_401(internal_app: FastAPI) -> None:
    with (
        patch("app.auth.dependencies.decode_access_token", return_value=None),
        patch("app.auth.dependencies.decode_m2m_token", return_value=None),
    ):
        client = TestClient(internal_app)
        r = client.get(
            "/jwt-only",
            headers={"Authorization": "Bearer broken"},
            params={"org_id": "o", "user_id": "u"},
        )
        assert r.status_code == 401
        assert r.json()["detail"] == "invalid_or_expired_token"


def test_jwt_dep_session_token_happy_path(internal_app: FastAPI) -> None:
    payload = {"sub": "user-1", "org_id": "org-1", "role": "admin", "type": "session"}
    with (
        patch("app.auth.dependencies.decode_access_token", return_value=payload),
        patch("app.auth.dependencies.decode_m2m_token", return_value=None),
    ):
        client = TestClient(internal_app)
        r = client.get(
            "/jwt-only",
            headers={"Authorization": "Bearer session-jwt"},
            params={"org_id": "org-1", "user_id": "user-1"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["org_id"] == "org-1"
        assert body["user_id"] == "user-1"
        assert body["auth_method"] == "session"
        assert body["role"] == "admin"


def test_jwt_dep_session_user_id_mismatch_returns_403(internal_app: FastAPI) -> None:
    payload = {"sub": "user-1", "org_id": "org-1", "type": "session"}
    with (
        patch("app.auth.dependencies.decode_access_token", return_value=payload),
        patch("app.auth.dependencies.decode_m2m_token", return_value=None),
    ):
        client = TestClient(internal_app)
        r = client.get(
            "/jwt-only",
            headers={"Authorization": "Bearer session-jwt"},
            params={"org_id": "org-1", "user_id": "someone-else"},
        )
        assert r.status_code == 403
        assert r.json()["detail"] == "user_id_mismatch_with_token"


def test_jwt_dep_m2m_token_org_mismatch_returns_403(internal_app: FastAPI) -> None:
    payload = {"sub": "service:scheduler", "org_id": "org-A", "type": "m2m"}
    with (
        patch("app.auth.dependencies.decode_access_token", return_value=None),
        patch("app.auth.dependencies.decode_m2m_token", return_value=payload),
    ):
        client = TestClient(internal_app)
        r = client.get(
            "/jwt-only",
            headers={"Authorization": "Bearer m2m-jwt"},
            params={"org_id": "org-B", "user_id": "ignored"},
        )
        assert r.status_code == 403
        assert r.json()["detail"] == "org_id_mismatch_with_token"


def test_jwt_dep_m2m_token_happy_path(internal_app: FastAPI) -> None:
    payload = {"sub": "service:scheduler", "org_id": "org-1", "type": "m2m"}
    with (
        patch("app.auth.dependencies.decode_access_token", return_value=None),
        patch("app.auth.dependencies.decode_m2m_token", return_value=payload),
    ):
        client = TestClient(internal_app)
        r = client.get(
            "/jwt-only",
            headers={"Authorization": "Bearer m2m-jwt"},
            params={"org_id": "org-1", "user_id": "any"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["auth_method"] == "m2m"
