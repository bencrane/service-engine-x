"""Engagement model schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# Status constants
ENGAGEMENT_STATUS_ACTIVE = 1
ENGAGEMENT_STATUS_PAUSED = 2
ENGAGEMENT_STATUS_CLOSED = 3

ENGAGEMENT_STATUS_MAP = {
    ENGAGEMENT_STATUS_ACTIVE: "Active",
    ENGAGEMENT_STATUS_PAUSED: "Paused",
    ENGAGEMENT_STATUS_CLOSED: "Closed",
}


class AccountSummary(BaseModel):
    """Minimal account info for engagement responses."""

    id: str
    name: str
    lifecycle: str


class EngagementCreate(BaseModel):
    """Schema for creating an engagement."""

    client_id: str | None = Field(None, description="UUID of the client (legacy)")
    account_id: str | None = Field(None, description="UUID of the account")
    name: str | None = Field(None, description="Optional display name")
    proposal_id: str | None = Field(None, description="Originating proposal UUID")


class EngagementUpdate(BaseModel):
    """Schema for updating an engagement."""

    name: str | None = None
    status: int | None = Field(None, ge=1, le=3, description="1=Active, 2=Paused, 3=Closed")


class ClientSummary(BaseModel):
    """Minimal client info for engagement responses."""

    id: str
    name: str
    email: str


class ProjectSummary(BaseModel):
    """Minimal project info for engagement responses."""

    id: str
    name: str
    status: str
    status_id: int
    phase: str
    phase_id: int


class ConversationSummary(BaseModel):
    """Minimal conversation info for engagement responses."""

    id: str
    subject: str | None
    status: str
    status_id: int
    last_message_at: datetime | None


class EngagementResponse(BaseModel):
    """Schema for engagement response."""

    id: str
    org_id: str
    client_id: str | None
    client: ClientSummary | None = None
    account_id: str | None = None
    account: AccountSummary | None = None

    name: str | None
    status: str
    status_id: int

    proposal_id: str | None

    # Nested resources (on retrieve only)
    projects: list[ProjectSummary] | None = None
    conversations: list[ConversationSummary] | None = None

    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None


class EngagementListResponse(BaseModel):
    """Schema for engagement in list responses (without nested resources)."""

    id: str
    org_id: str
    client_id: str | None
    client: ClientSummary | None = None
    account_id: str | None = None
    account: AccountSummary | None = None

    name: str | None
    status: str
    status_id: int

    proposal_id: str | None

    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
