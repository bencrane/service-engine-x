"""Phase 2 tests: transitional auth dependencies that accept either the legacy
``SERX_AUTH_TOKEN`` or the new ``SERX_INTERNAL_BEARER_TOKEN``.

These cover the two helpers that internal routes and tenant CRUD routes are
swapped onto during the rollout:

- ``verify_token_or_internal_bearer`` (drop-in for ``verify_token``)
- ``get_current_org_or_internal_bearer`` (drop-in for ``get_current_org``)
"""

from unittest.mock import patch

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth.dependencies import (
    AuthContext,
    get_current_org_or_internal_bearer,
    verify_token_or_internal_bearer,
)
from app.config import settings


@pytest.fixture
def transitional_app() -> FastAPI:
    app = FastAPI()

    @app.get("/internal-only")
    def internal_only(_: None = Depends(verify_token_or_internal_bearer)) -> dict:
        return {"ok": True}

    @app.get("/tenant")
    def tenant(auth: AuthContext = Depends(get_current_org_or_internal_bearer)) -> dict:
        return {
            "org_id": auth.org_id,
            "user_id": auth.user_id,
            "auth_method": auth.auth_method,
        }

    return app


def test_verify_or_internal_no_secrets_returns_503(transitional_app: FastAPI) -> None:
    with (
        patch.object(settings, "SERX_AUTH_TOKEN", ""),
        patch.object(settings, "SERX_INTERNAL_BEARER_TOKEN", ""),
    ):
        client = TestClient(transitional_app)
        r = client.get("/internal-only", headers={"Authorization": "Bearer x"})
        assert r.status_code == 503


def test_verify_or_internal_accepts_legacy_token(transitional_app: FastAPI) -> None:
    with (
        patch.object(settings, "SERX_AUTH_TOKEN", "legacy-token"),
        patch.object(settings, "SERX_INTERNAL_BEARER_TOKEN", "new-token"),
    ):
        client = TestClient(transitional_app)
        r = client.get("/internal-only", headers={"Authorization": "Bearer legacy-token"})
        assert r.status_code == 200


def test_verify_or_internal_accepts_new_token(transitional_app: FastAPI) -> None:
    with (
        patch.object(settings, "SERX_AUTH_TOKEN", "legacy-token"),
        patch.object(settings, "SERX_INTERNAL_BEARER_TOKEN", "new-token"),
    ):
        client = TestClient(transitional_app)
        r = client.get("/internal-only", headers={"Authorization": "Bearer new-token"})
        assert r.status_code == 200


def test_verify_or_internal_rejects_unknown(transitional_app: FastAPI) -> None:
    with (
        patch.object(settings, "SERX_AUTH_TOKEN", "legacy-token"),
        patch.object(settings, "SERX_INTERNAL_BEARER_TOKEN", "new-token"),
    ):
        client = TestClient(transitional_app)
        r = client.get("/internal-only", headers={"Authorization": "Bearer wrong"})
        assert r.status_code == 401


def test_verify_or_internal_works_when_only_legacy_set(transitional_app: FastAPI) -> None:
    with (
        patch.object(settings, "SERX_AUTH_TOKEN", "legacy-token"),
        patch.object(settings, "SERX_INTERNAL_BEARER_TOKEN", ""),
    ):
        client = TestClient(transitional_app)
        r = client.get("/internal-only", headers={"Authorization": "Bearer legacy-token"})
        assert r.status_code == 200
        r2 = client.get("/internal-only", headers={"Authorization": "Bearer wrong"})
        assert r2.status_code == 401


def test_verify_or_internal_works_when_only_new_set(transitional_app: FastAPI) -> None:
    with (
        patch.object(settings, "SERX_AUTH_TOKEN", ""),
        patch.object(settings, "SERX_INTERNAL_BEARER_TOKEN", "new-token"),
    ):
        client = TestClient(transitional_app)
        r = client.get("/internal-only", headers={"Authorization": "Bearer new-token"})
        assert r.status_code == 200


def test_get_current_org_or_internal_legacy_path(transitional_app: FastAPI) -> None:
    with (
        patch.object(settings, "SERX_AUTH_TOKEN", "legacy-token"),
        patch.object(settings, "SERX_INTERNAL_BEARER_TOKEN", "new-token"),
    ):
        client = TestClient(transitional_app)
        r = client.get(
            "/tenant",
            headers={"Authorization": "Bearer legacy-token"},
            params={"org_id": "o1", "user_id": "u1"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body == {"org_id": "o1", "user_id": "u1", "auth_method": "shared_token"}


def test_get_current_org_or_internal_new_path(transitional_app: FastAPI) -> None:
    with (
        patch.object(settings, "SERX_AUTH_TOKEN", "legacy-token"),
        patch.object(settings, "SERX_INTERNAL_BEARER_TOKEN", "new-token"),
    ):
        client = TestClient(transitional_app)
        r = client.get(
            "/tenant",
            headers={"Authorization": "Bearer new-token"},
            params={"org_id": "o1", "user_id": "u1"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body == {"org_id": "o1", "user_id": "u1", "auth_method": "internal_bearer"}


def test_get_current_org_or_internal_rejects_unknown(transitional_app: FastAPI) -> None:
    with (
        patch.object(settings, "SERX_AUTH_TOKEN", "legacy-token"),
        patch.object(settings, "SERX_INTERNAL_BEARER_TOKEN", "new-token"),
    ):
        client = TestClient(transitional_app)
        r = client.get(
            "/tenant",
            headers={"Authorization": "Bearer wrong"},
            params={"org_id": "o1", "user_id": "u1"},
        )
        assert r.status_code == 401


def test_get_current_org_or_internal_requires_org_user(transitional_app: FastAPI) -> None:
    with (
        patch.object(settings, "SERX_AUTH_TOKEN", "legacy-token"),
        patch.object(settings, "SERX_INTERNAL_BEARER_TOKEN", "new-token"),
    ):
        client = TestClient(transitional_app)
        # Missing query params -> FastAPI 422
        r = client.get("/tenant", headers={"Authorization": "Bearer new-token"})
        assert r.status_code in (400, 422)
