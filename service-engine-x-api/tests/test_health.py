"""Tests for the library-provided health endpoints.

SERX uses ``aux_m2m_server.build_health_router`` which exposes:

    GET /api/health       — liveness (always 200, no checks)
    GET /api/health/deep  — depth check (200 healthy / 503 unhealthy)
"""

from fastapi.testclient import TestClient


def test_health_liveness(client: TestClient) -> None:
    """Liveness endpoint always returns 200 with the standard schema."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["ok"] is True
    assert data["service"] == "serx"
    assert "version" in data


def test_api_index(client: TestClient) -> None:
    """API index returns available endpoints."""
    response = client.get("/api")
    assert response.status_code == 200

    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "endpoints" in data
    assert "health" in data["endpoints"]
