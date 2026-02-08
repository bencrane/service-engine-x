"""Tests for clients API endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


def test_list_clients_unauthorized(client: TestClient) -> None:
    """Test that list clients requires authentication."""
    response = client.get("/api/clients")
    assert response.status_code == 401


def test_create_client_unauthorized(client: TestClient) -> None:
    """Test that create client requires authentication."""
    response = client.post(
        "/api/clients",
        json={"name_f": "John", "name_l": "Doe", "email": "john@example.com"},
    )
    assert response.status_code == 401


def test_retrieve_client_unauthorized(client: TestClient) -> None:
    """Test that retrieve client requires authentication."""
    response = client.get("/api/clients/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401


def test_update_client_unauthorized(client: TestClient) -> None:
    """Test that update client requires authentication."""
    response = client.put(
        "/api/clients/123e4567-e89b-12d3-a456-426614174000",
        json={"name_f": "Jane"},
    )
    assert response.status_code == 401


def test_delete_client_unauthorized(client: TestClient) -> None:
    """Test that delete client requires authentication."""
    response = client.delete("/api/clients/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401


def test_retrieve_client_invalid_uuid(client: TestClient) -> None:
    """Test that invalid UUID returns 401 (auth checked first)."""
    response = client.get("/api/clients/invalid-uuid")
    assert response.status_code == 401
