"""Conversation model schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# Status constants
CONVERSATION_STATUS_OPEN = 1
CONVERSATION_STATUS_CLOSED = 2

CONVERSATION_STATUS_MAP = {
    CONVERSATION_STATUS_OPEN: "Open",
    CONVERSATION_STATUS_CLOSED: "Closed",
}


class Attachment(BaseModel):
    """File attachment metadata."""

    name: str
    url: str
    size: int | None = None


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""

    subject: str | None = Field(None, max_length=255)


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""

    subject: str | None = Field(None, max_length=255)
    status: int | None = Field(None, ge=1, le=2, description="1=Open, 2=Closed")


class MessageCreate(BaseModel):
    """Schema for creating a message."""

    content: str = Field(..., min_length=1)
    is_internal: bool = Field(False, description="Staff-only message not visible to client")
    attachments: list[Attachment] | None = None


class SenderSummary(BaseModel):
    """Minimal sender info for message responses."""

    id: str
    name: str
    email: str


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: str
    conversation_id: str
    sender_id: str
    sender: SenderSummary | None = None

    content: str
    is_internal: bool
    attachments: list[Attachment]

    created_at: datetime
    updated_at: datetime


class ProjectBrief(BaseModel):
    """Brief project info for conversation responses."""

    id: str
    name: str | None
    engagement_id: str


class ConversationResponse(BaseModel):
    """Schema for conversation response."""

    id: str
    project_id: str
    org_id: str

    subject: str | None
    status: str
    status_id: int

    project: ProjectBrief | None = None
    messages: list[MessageResponse] | None = None
    message_count: int | None = None

    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None


class ConversationListResponse(BaseModel):
    """Schema for conversation in list responses."""

    id: str
    project_id: str
    org_id: str

    subject: str | None
    status: str
    status_id: int

    message_count: int = 0

    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None
