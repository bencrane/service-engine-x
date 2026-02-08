"""Client models for request/response schemas."""

from typing import Any

from pydantic import BaseModel, EmailStr, Field


class AddressInput(BaseModel):
    """Address input for create/update."""

    line_1: str | None = None
    line_2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postcode: str | None = None


class AddressResponse(BaseModel):
    """Address response schema."""

    line_1: str | None
    line_2: str | None
    city: str | None
    state: str | None
    country: str | None
    postcode: str | None
    name_f: str | None
    name_l: str | None
    tax_id: str | None
    company_name: str | None
    company_vat: str | None


class RoleResponse(BaseModel):
    """Role response schema."""

    id: str
    name: str
    dashboard_access: int
    order_access: int
    order_management: int
    ticket_access: int
    ticket_management: int
    invoice_access: int
    invoice_management: int
    clients: int
    services: int
    coupons: int
    forms: int
    messaging: int
    affiliates: int
    settings_company: bool
    settings_payments: bool
    settings_team: bool
    settings_modules: bool
    settings_integrations: bool
    settings_orders: bool
    settings_tickets: bool
    settings_accounts: bool
    settings_messages: bool
    settings_tags: bool
    settings_sidebar: bool
    settings_dashboard: bool
    settings_templates: bool
    settings_emails: bool
    settings_language: bool
    settings_logs: bool
    created_at: str
    updated_at: str


class ClientCreate(BaseModel):
    """Request body for creating a client."""

    name_f: str = Field(..., min_length=1)
    name_l: str = Field(..., min_length=1)
    email: EmailStr
    company: str | None = None
    phone: str | None = None
    tax_id: str | None = None
    address: AddressInput | None = None
    note: str | None = None
    optin: str | None = None
    stripe_id: str | None = None
    custom_fields: dict[str, Any] | None = None
    status_id: int | None = None
    created_at: str | None = None


class ClientUpdate(BaseModel):
    """Request body for updating a client."""

    name_f: str | None = None
    name_l: str | None = None
    email: EmailStr | None = None
    company: str | None = None
    phone: str | None = None
    tax_id: str | None = None
    address: AddressInput | None = None
    note: str | None = None
    optin: str | None = None
    stripe_id: str | None = None
    custom_fields: dict[str, Any] | None = None
    status_id: int | None = None
    created_at: str | None = None


class ClientResponse(BaseModel):
    """Client response schema."""

    id: str
    name: str
    name_f: str
    name_l: str
    email: str
    company: str | None
    phone: str | None
    tax_id: str | None
    address: AddressResponse | None
    note: str | None
    balance: str
    spent: str | None
    optin: str | None
    stripe_id: str | None
    custom_fields: dict[str, Any]
    status: int
    aff_id: int | None
    aff_link: str | None
    role_id: str
    role: RoleResponse
    ga_cid: str | None = None
    created_at: str
