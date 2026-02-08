"""Tests for Conversations API endpoints."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

# Test UUIDs
PROJECT_ID = "00000000-0000-0000-0000-000000000001"
CONVERSATION_ID = "00000000-0000-0000-0000-000000000002"
MESSAGE_ID = "00000000-0000-0000-0000-000000000003"


def test_list_conversations_unauthorized() -> None:
    """Test that list conversations requires authentication."""
    response = client.get(f"/api/projects/{PROJECT_ID}/conversations")
    assert response.status_code == 401


def test_create_conversation_unauthorized() -> None:
    """Test that create conversation requires authentication."""
    response = client.post(f"/api/projects/{PROJECT_ID}/conversations", json={})
    assert response.status_code == 401


def test_retrieve_conversation_unauthorized() -> None:
    """Test that retrieve conversation requires authentication."""
    response = client.get(f"/api/projects/{PROJECT_ID}/conversations/{CONVERSATION_ID}")
    assert response.status_code == 401


def test_update_conversation_unauthorized() -> None:
    """Test that update conversation requires authentication."""
    response = client.put(
        f"/api/projects/{PROJECT_ID}/conversations/{CONVERSATION_ID}",
        json={"subject": "Updated"},
    )
    assert response.status_code == 401


def test_delete_conversation_unauthorized() -> None:
    """Test that delete conversation requires authentication."""
    response = client.delete(f"/api/projects/{PROJECT_ID}/conversations/{CONVERSATION_ID}")
    assert response.status_code == 401


def test_list_messages_unauthorized() -> None:
    """Test that list messages requires authentication."""
    response = client.get(f"/api/projects/{PROJECT_ID}/conversations/{CONVERSATION_ID}/messages")
    assert response.status_code == 401


def test_create_message_unauthorized() -> None:
    """Test that create message requires authentication."""
    response = client.post(
        f"/api/projects/{PROJECT_ID}/conversations/{CONVERSATION_ID}/messages",
        json={"content": "Test message"},
    )
    assert response.status_code == 401


def test_delete_message_unauthorized() -> None:
    """Test that delete message requires authentication."""
    response = client.delete(
        f"/api/projects/{PROJECT_ID}/conversations/{CONVERSATION_ID}/messages/{MESSAGE_ID}"
    )
    assert response.status_code == 401
