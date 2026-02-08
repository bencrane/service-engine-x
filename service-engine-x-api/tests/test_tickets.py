"""Tests for tickets API endpoints."""

from fastapi.testclient import TestClient


def test_list_tickets_unauthorized(client: TestClient) -> None:
    """Test that list tickets requires authentication."""
    response = client.get("/api/tickets")
    assert response.status_code == 401


def test_create_ticket_unauthorized(client: TestClient) -> None:
    """Test that create ticket requires authentication."""
    response = client.post(
        "/api/tickets",
        json={
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "subject": "Test Ticket",
        },
    )
    assert response.status_code == 401


def test_retrieve_ticket_unauthorized(client: TestClient) -> None:
    """Test that retrieve ticket requires authentication."""
    response = client.get("/api/tickets/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401


def test_update_ticket_unauthorized(client: TestClient) -> None:
    """Test that update ticket requires authentication."""
    response = client.put(
        "/api/tickets/123e4567-e89b-12d3-a456-426614174000",
        json={"subject": "Updated Subject"},
    )
    assert response.status_code == 401


def test_delete_ticket_unauthorized(client: TestClient) -> None:
    """Test that delete ticket requires authentication."""
    response = client.delete("/api/tickets/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401
