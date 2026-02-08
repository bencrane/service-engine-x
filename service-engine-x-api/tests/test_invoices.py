"""Tests for invoices API endpoints."""

from fastapi.testclient import TestClient


def test_list_invoices_unauthorized(client: TestClient) -> None:
    """Test that list invoices requires authentication."""
    response = client.get("/api/invoices")
    assert response.status_code == 401


def test_create_invoice_unauthorized(client: TestClient) -> None:
    """Test that create invoice requires authentication."""
    response = client.post(
        "/api/invoices",
        json={
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "items": [
                {"name": "Test Item", "quantity": 1, "amount": 100}
            ],
        },
    )
    assert response.status_code == 401


def test_retrieve_invoice_unauthorized(client: TestClient) -> None:
    """Test that retrieve invoice requires authentication."""
    response = client.get("/api/invoices/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401


def test_update_invoice_unauthorized(client: TestClient) -> None:
    """Test that update invoice requires authentication."""
    response = client.put(
        "/api/invoices/123e4567-e89b-12d3-a456-426614174000",
        json={
            "items": [
                {"name": "Updated Item", "quantity": 2, "amount": 150}
            ],
        },
    )
    assert response.status_code == 401


def test_delete_invoice_unauthorized(client: TestClient) -> None:
    """Test that delete invoice requires authentication."""
    response = client.delete("/api/invoices/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401


def test_charge_invoice_unauthorized(client: TestClient) -> None:
    """Test that charge invoice requires authentication."""
    response = client.post(
        "/api/invoices/123e4567-e89b-12d3-a456-426614174000/charge",
        json={"payment_method_id": "pm_test_123"},
    )
    assert response.status_code == 401


def test_mark_paid_invoice_unauthorized(client: TestClient) -> None:
    """Test that mark invoice paid requires authentication."""
    response = client.post("/api/invoices/123e4567-e89b-12d3-a456-426614174000/mark_paid")
    assert response.status_code == 401
