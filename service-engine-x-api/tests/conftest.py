"""Pytest fixtures for testing."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """
    Create mock auth headers for testing.

    Note: In real tests, you'd want to create a test token in the database.
    """
    return {"Authorization": "Bearer test-token"}
