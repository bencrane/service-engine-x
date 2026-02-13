"""Contact models for request/response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class AccountBrief(BaseModel):
    """Brief account info for contact responses."""

    id: str
    name: str
    lifecycle: str


class UserBrief(BaseModel):
    """Brief user info for contact responses."""

    id: str
    email: str


class ContactCreate(BaseModel):
    """Request body for creating a contact."""

    account_id: str | None = Field(None, description="UUID of the account")
    name_f: str = Field(..., min_length=1, description="First name")
    name_l: str = Field(..., min_length=1, description="Last name")
    email: EmailStr
    phone: str | None = None
    title: str | None = Field(None, description="Job title")
    is_primary: bool = Field(default=False, description="Primary contact for account")
    is_billing: bool = Field(default=False, description="Billing contact for account")
    optin: str | None = None
    custom_fields: dict[str, Any] | None = None


class ContactUpdate(BaseModel):
    """Request body for updating a contact."""

    account_id: str | None = None
    name_f: str | None = None
    name_l: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    title: str | None = None
    is_primary: bool | None = None
    is_billing: bool | None = None
    optin: str | None = None
    custom_fields: dict[str, Any] | None = None


class ContactResponse(BaseModel):
    """Contact response schema."""

    id: str
    org_id: str
    account_id: str | None
    account: AccountBrief | None = None

    name: str
    name_f: str
    name_l: str
    email: str
    phone: str | None
    title: str | None

    user_id: str | None
    user: UserBrief | None = None
    has_portal_access: bool

    is_primary: bool
    is_billing: bool
    optin: str | None
    custom_fields: dict[str, Any]

    created_at: datetime
    updated_at: datetime


class ContactListResponse(BaseModel):
    """Contact response for list endpoints (without nested account details)."""

    id: str
    org_id: str
    account_id: str | None
    name: str
    name_f: str
    name_l: str
    email: str
    phone: str | None
    title: str | None
    has_portal_access: bool
    is_primary: bool
    is_billing: bool
    created_at: datetime
    updated_at: datetime


class GrantPortalAccessRequest(BaseModel):
    """Request body for granting portal access to a contact."""

    send_welcome_email: bool = Field(
        default=True,
        description="Whether to send a welcome email with login instructions",
    )
