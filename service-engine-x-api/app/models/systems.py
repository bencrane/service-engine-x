"""System models for request/response schemas."""

from pydantic import BaseModel, Field


class SystemCreate(BaseModel):
    """Request body for creating a system."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class SystemUpdate(BaseModel):
    """Request body for updating a system."""

    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class SystemResponse(BaseModel):
    """System response schema."""

    id: str
    org_id: str
    name: str
    slug: str | None
    description: str | None
    created_at: str
    updated_at: str


class SystemAccessCreate(BaseModel):
    """Request body for granting system access."""

    system_id: str
    client_id: str
    engagement_id: str | None = None
    expires_at: str | None = None


class SystemAccessUpdate(BaseModel):
    """Request body for updating system access."""

    status: int | None = Field(None, ge=1, le=3)  # 1=active, 2=suspended, 3=revoked
    expires_at: str | None = None


class SystemAccessResponse(BaseModel):
    """System access response schema."""

    id: str
    org_id: str
    system_id: str
    client_id: str
    engagement_id: str | None
    status: int
    granted_at: str
    expires_at: str | None
    created_at: str
    updated_at: str
    system: SystemResponse | None = None
