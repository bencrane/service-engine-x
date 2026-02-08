"""Tests for services API endpoints."""

from fastapi.testclient import TestClient


def test_list_services_unauthorized(client: TestClient) -> None:
    """Test that list services requires authentication."""
    response = client.get("/api/services")
    assert response.status_code == 401


def test_create_service_unauthorized(client: TestClient) -> None:
    """Test that create service requires authentication."""
    response = client.post(
        "/api/services",
        json={"name": "Test Service", "recurring": 0, "currency": "USD"},
    )
    assert response.status_code == 401


def test_retrieve_service_unauthorized(client: TestClient) -> None:
    """Test that retrieve service requires authentication."""
    response = client.get("/api/services/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401


def test_update_service_unauthorized(client: TestClient) -> None:
    """Test that update service requires authentication."""
    response = client.put(
        "/api/services/123e4567-e89b-12d3-a456-426614174000",
        json={"name": "Updated Service"},
    )
    assert response.status_code == 401


def test_delete_service_unauthorized(client: TestClient) -> None:
    """Test that delete service requires authentication."""
    response = client.delete("/api/services/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401


def test_retrieve_service_invalid_uuid(client: TestClient) -> None:
    """Test that invalid UUID returns 401 (auth checked first)."""
    response = client.get("/api/services/invalid-uuid")
    assert response.status_code == 401
