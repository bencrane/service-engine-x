"""Order models for request/response schemas."""

from typing import Any

from pydantic import BaseModel, Field

from app.models.services import MetadataItem


class OrderEmployeeResponse(BaseModel):
    """Employee assigned to an order."""

    id: str
    name_f: str | None
    name_l: str | None
    role_id: str | None


class OrderClientResponse(BaseModel):
    """Client associated with an order."""

    id: str
    name: str
    name_f: str
    name_l: str
    email: str
    company: str | None
    phone: str | None
    address: dict[str, Any] | None
    role: dict[str, Any] | None


class OrderCreate(BaseModel):
    """Request body for creating an order."""

    user_id: str
    service_id: str | None = None
    service: str | None = None
    status: int | None = Field(None, ge=0, le=4)
    employees: list[str] | None = None
    tags: list[str] | None = None
    note: str | None = None
    number: str | None = None
    metadata: list[MetadataItem] | None = None
    created_at: str | None = None
    date_started: str | None = None
    date_completed: str | None = None
    date_due: str | None = None


class OrderUpdate(BaseModel):
    """Request body for updating an order."""

    service_id: str | None = None
    service: str | None = None
    status: int | None = Field(None, ge=0, le=4)
    employees: list[str] | None = None
    tags: list[str] | None = None
    note: str | None = None
    metadata: list[MetadataItem] | None = None
    date_started: str | None = None
    date_completed: str | None = None
    date_due: str | None = None


class OrderResponse(BaseModel):
    """Order response schema."""

    id: str
    number: str
    created_at: str
    updated_at: str
    last_message_at: str | None
    date_started: str | None
    date_completed: str | None
    date_due: str | None
    client: OrderClientResponse | None
    tags: list[str]
    status: str
    status_id: int
    price: str
    quantity: int
    invoice_id: str | None
    service: str
    service_id: str | None
    user_id: str
    employees: list[OrderEmployeeResponse]
    note: str | None
    form_data: dict[str, Any]
    paysys: str | None
