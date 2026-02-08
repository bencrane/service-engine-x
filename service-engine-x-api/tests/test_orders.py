"""Tests for orders API endpoints."""

from fastapi.testclient import TestClient


def test_list_orders_unauthorized(client: TestClient) -> None:
    """Test that list orders requires authentication."""
    response = client.get("/api/orders")
    assert response.status_code == 401


def test_create_order_unauthorized(client: TestClient) -> None:
    """Test that create order requires authentication."""
    response = client.post(
        "/api/orders",
        json={"user_id": "123e4567-e89b-12d3-a456-426614174000", "service": "Test"},
    )
    assert response.status_code == 401


def test_retrieve_order_unauthorized(client: TestClient) -> None:
    """Test that retrieve order requires authentication."""
    response = client.get("/api/orders/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401


def test_update_order_unauthorized(client: TestClient) -> None:
    """Test that update order requires authentication."""
    response = client.put(
        "/api/orders/123e4567-e89b-12d3-a456-426614174000",
        json={"status": 1},
    )
    assert response.status_code == 401


def test_delete_order_unauthorized(client: TestClient) -> None:
    """Test that delete order requires authentication."""
    response = client.delete("/api/orders/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401


def test_list_order_tasks_unauthorized(client: TestClient) -> None:
    """Test that list order tasks requires authentication."""
    response = client.get("/api/orders/123e4567-e89b-12d3-a456-426614174000/tasks")
    assert response.status_code == 401


def test_create_order_task_unauthorized(client: TestClient) -> None:
    """Test that create order task requires authentication."""
    response = client.post(
        "/api/orders/123e4567-e89b-12d3-a456-426614174000/tasks",
        json={"name": "Test Task"},
    )
    assert response.status_code == 401


def test_list_order_messages_unauthorized(client: TestClient) -> None:
    """Test that list order messages requires authentication."""
    response = client.get("/api/orders/123e4567-e89b-12d3-a456-426614174000/messages")
    assert response.status_code == 401


def test_create_order_message_unauthorized(client: TestClient) -> None:
    """Test that create order message requires authentication."""
    response = client.post(
        "/api/orders/123e4567-e89b-12d3-a456-426614174000/messages",
        json={"message": "Test message"},
    )
    assert response.status_code == 401
