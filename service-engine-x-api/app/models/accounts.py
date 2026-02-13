"""Account models for request/response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


# Lifecycle status constants
ACCOUNT_LIFECYCLE_LEAD = "lead"
ACCOUNT_LIFECYCLE_ACTIVE = "active"
ACCOUNT_LIFECYCLE_INACTIVE = "inactive"
ACCOUNT_LIFECYCLE_CHURNED = "churned"

VALID_LIFECYCLES = [
    ACCOUNT_LIFECYCLE_LEAD,
    ACCOUNT_LIFECYCLE_ACTIVE,
    ACCOUNT_LIFECYCLE_INACTIVE,
    ACCOUNT_LIFECYCLE_CHURNED,
]


class AddressBrief(BaseModel):
    """Brief address info for account responses."""

    line_1: str | None
    line_2: str | None
    city: str | None
    state: str | None
    country: str | None
    postcode: str | None


class AccountCreate(BaseModel):
    """Request body for creating an account."""

    name: str = Field(..., min_length=1, description="Company name")
    domain: str | None = Field(None, description="Website domain")
    lifecycle: str = Field(
        default=ACCOUNT_LIFECYCLE_LEAD,
        description="Lifecycle status: lead, active, inactive, churned",
    )
    tax_id: str | None = None
    source: str | None = Field(None, description="Lead source")
    ga_cid: str | None = Field(None, description="Google Analytics client ID")
    note: str | None = None
    custom_fields: dict[str, Any] | None = None


class AccountUpdate(BaseModel):
    """Request body for updating an account."""

    name: str | None = None
    domain: str | None = None
    lifecycle: str | None = None
    balance: str | None = None
    total_spent: str | None = None
    stripe_customer_id: str | None = None
    tax_id: str | None = None
    aff_id: int | None = None
    aff_link: str | None = None
    source: str | None = None
    ga_cid: str | None = None
    note: str | None = None
    custom_fields: dict[str, Any] | None = None


class ContactBrief(BaseModel):
    """Brief contact info for account responses."""

    id: str
    name: str
    email: str
    is_primary: bool
    is_billing: bool


class AccountResponse(BaseModel):
    """Account response schema."""

    id: str
    org_id: str
    name: str
    domain: str | None
    lifecycle: str

    balance: str
    total_spent: str
    stripe_customer_id: str | None
    tax_id: str | None

    aff_id: int | None
    aff_link: str | None

    source: str | None
    ga_cid: str | None
    custom_fields: dict[str, Any]
    note: str | None
    billing_address: AddressBrief | None = None

    created_at: datetime
    updated_at: datetime


class AccountListResponse(BaseModel):
    """Account response for list endpoints (without nested resources)."""

    id: str
    org_id: str
    name: str
    domain: str | None
    lifecycle: str
    balance: str
    total_spent: str
    created_at: datetime
    updated_at: datetime


class AccountWithContacts(AccountResponse):
    """Account response with contacts included."""

    contacts: list[ContactBrief] = []
