"""Tests for proposals API endpoints."""

from fastapi.testclient import TestClient


def test_list_proposals_unauthorized(client: TestClient) -> None:
    """Test that list proposals requires authentication."""
    response = client.get("/api/proposals")
    assert response.status_code == 401


def test_create_proposal_unauthorized(client: TestClient) -> None:
    """Test that create proposal requires authentication."""
    response = client.post(
        "/api/proposals",
        json={
            "client_email": "test@example.com",
            "client_name_f": "John",
            "client_name_l": "Doe",
            "items": [
                {"service_id": "123e4567-e89b-12d3-a456-426614174000", "price": 100}
            ],
        },
    )
    assert response.status_code == 401


def test_retrieve_proposal_unauthorized(client: TestClient) -> None:
    """Test that retrieve proposal requires authentication."""
    response = client.get("/api/proposals/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401


def test_send_proposal_unauthorized(client: TestClient) -> None:
    """Test that send proposal requires authentication."""
    response = client.post("/api/proposals/123e4567-e89b-12d3-a456-426614174000/send")
    assert response.status_code == 401


def test_sign_proposal_unauthorized(client: TestClient) -> None:
    """Test that sign proposal requires authentication."""
    response = client.post("/api/proposals/123e4567-e89b-12d3-a456-426614174000/sign")
    assert response.status_code == 401
