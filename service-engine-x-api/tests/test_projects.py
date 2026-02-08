"""Tests for Projects API endpoints."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_projects_unauthorized() -> None:
    """Test that list projects requires authentication."""
    response = client.get("/api/projects")
    assert response.status_code == 401


def test_create_project_unauthorized() -> None:
    """Test that create project requires authentication."""
    response = client.post("/api/projects", json={
        "engagement_id": "00000000-0000-0000-0000-000000000000",
        "name": "Test Project",
    })
    assert response.status_code == 401


def test_retrieve_project_unauthorized() -> None:
    """Test that retrieve project requires authentication."""
    response = client.get("/api/projects/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 401


def test_update_project_unauthorized() -> None:
    """Test that update project requires authentication."""
    response = client.put(
        "/api/projects/00000000-0000-0000-0000-000000000000",
        json={"name": "Updated"},
    )
    assert response.status_code == 401


def test_delete_project_unauthorized() -> None:
    """Test that delete project requires authentication."""
    response = client.delete("/api/projects/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 401


def test_advance_project_unauthorized() -> None:
    """Test that advance project phase requires authentication."""
    response = client.post("/api/projects/00000000-0000-0000-0000-000000000000/advance")
    assert response.status_code == 401
