"""Tests for Engagements API endpoints."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_engagements_unauthorized() -> None:
    """Test that list engagements requires authentication."""
    response = client.get("/api/engagements")
    assert response.status_code == 401


def test_create_engagement_unauthorized() -> None:
    """Test that create engagement requires authentication."""
    response = client.post("/api/engagements", json={
        "client_id": "00000000-0000-0000-0000-000000000000",
    })
    assert response.status_code == 401


def test_retrieve_engagement_unauthorized() -> None:
    """Test that retrieve engagement requires authentication."""
    response = client.get("/api/engagements/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 401


def test_update_engagement_unauthorized() -> None:
    """Test that update engagement requires authentication."""
    response = client.put(
        "/api/engagements/00000000-0000-0000-0000-000000000000",
        json={"name": "Test"},
    )
    assert response.status_code == 401


def test_delete_engagement_unauthorized() -> None:
    """Test that delete engagement requires authentication."""
    response = client.delete("/api/engagements/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 401
