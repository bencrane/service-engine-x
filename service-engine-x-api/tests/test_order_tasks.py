"""Tests for order-tasks API endpoints."""

from fastapi.testclient import TestClient


def test_update_order_task_unauthorized(client: TestClient) -> None:
    """Test that update order task requires authentication."""
    response = client.put(
        "/api/order-tasks/123e4567-e89b-12d3-a456-426614174000",
        json={"name": "Updated Task"},
    )
    assert response.status_code == 401


def test_delete_order_task_unauthorized(client: TestClient) -> None:
    """Test that delete order task requires authentication."""
    response = client.delete("/api/order-tasks/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401


def test_mark_task_complete_unauthorized(client: TestClient) -> None:
    """Test that mark task complete requires authentication."""
    response = client.post("/api/order-tasks/123e4567-e89b-12d3-a456-426614174000/complete")
    assert response.status_code == 401


def test_mark_task_incomplete_unauthorized(client: TestClient) -> None:
    """Test that mark task incomplete requires authentication."""
    response = client.delete("/api/order-tasks/123e4567-e89b-12d3-a456-426614174000/complete")
    assert response.status_code == 401
