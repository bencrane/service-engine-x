"""Tests for order-messages API endpoints."""

from fastapi.testclient import TestClient


def test_delete_order_message_unauthorized(client: TestClient) -> None:
    """Test that delete order message requires authentication."""
    response = client.delete("/api/order-messages/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401
