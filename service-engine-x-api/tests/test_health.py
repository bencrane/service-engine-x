"""Tests for health endpoint."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test that health endpoint returns healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_api_index(client: TestClient) -> None:
    """Test that API index returns available endpoints."""
    response = client.get("/api")
    assert response.status_code == 200

    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "endpoints" in data
    assert "health" in data["endpoints"]
