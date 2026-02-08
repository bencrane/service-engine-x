"""Project model schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# Status constants
PROJECT_STATUS_ACTIVE = 1
PROJECT_STATUS_PAUSED = 2
PROJECT_STATUS_COMPLETED = 3
PROJECT_STATUS_CANCELLED = 4

PROJECT_STATUS_MAP = {
    PROJECT_STATUS_ACTIVE: "Active",
    PROJECT_STATUS_PAUSED: "Paused",
    PROJECT_STATUS_COMPLETED: "Completed",
    PROJECT_STATUS_CANCELLED: "Cancelled",
}

# Phase constants
PROJECT_PHASE_KICKOFF = 1
PROJECT_PHASE_SETUP = 2
PROJECT_PHASE_BUILD = 3
PROJECT_PHASE_TESTING = 4
PROJECT_PHASE_DEPLOYMENT = 5
PROJECT_PHASE_HANDOFF = 6

PROJECT_PHASE_MAP = {
    PROJECT_PHASE_KICKOFF: "Kickoff",
    PROJECT_PHASE_SETUP: "Setup",
    PROJECT_PHASE_BUILD: "Build",
    PROJECT_PHASE_TESTING: "Testing",
    PROJECT_PHASE_DEPLOYMENT: "Deployment",
    PROJECT_PHASE_HANDOFF: "Handoff",
}

# Valid phase transitions (can only move forward or stay)
VALID_PHASE_TRANSITIONS = {
    PROJECT_PHASE_KICKOFF: [PROJECT_PHASE_KICKOFF, PROJECT_PHASE_SETUP],
    PROJECT_PHASE_SETUP: [PROJECT_PHASE_SETUP, PROJECT_PHASE_BUILD],
    PROJECT_PHASE_BUILD: [PROJECT_PHASE_BUILD, PROJECT_PHASE_TESTING],
    PROJECT_PHASE_TESTING: [PROJECT_PHASE_TESTING, PROJECT_PHASE_DEPLOYMENT, PROJECT_PHASE_BUILD],  # Can go back to build
    PROJECT_PHASE_DEPLOYMENT: [PROJECT_PHASE_DEPLOYMENT, PROJECT_PHASE_HANDOFF],
    PROJECT_PHASE_HANDOFF: [PROJECT_PHASE_HANDOFF],
}


class ProjectCreate(BaseModel):
    """Schema for creating a project."""

    engagement_id: str = Field(..., description="UUID of the parent engagement")
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    service_id: str | None = Field(None, description="Optional service template UUID")


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: int | None = Field(None, ge=1, le=4, description="1=Active, 2=Paused, 3=Completed, 4=Cancelled")
    phase: int | None = Field(None, ge=1, le=6, description="1=Kickoff through 6=Handoff")


class EngagementSummary(BaseModel):
    """Minimal engagement info for project responses."""

    id: str
    name: str | None
    client_id: str


class ServiceSummary(BaseModel):
    """Minimal service info for project responses."""

    id: str
    name: str


class ProjectResponse(BaseModel):
    """Schema for project response."""

    id: str
    engagement_id: str
    org_id: str

    name: str
    description: str | None

    status: str
    status_id: int
    phase: str
    phase_id: int

    service_id: str | None
    service: ServiceSummary | None = None

    engagement: EngagementSummary | None = None

    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class ProjectListResponse(BaseModel):
    """Schema for project in list responses."""

    id: str
    engagement_id: str
    org_id: str

    name: str
    description: str | None

    status: str
    status_id: int
    phase: str
    phase_id: int

    service_id: str | None

    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
