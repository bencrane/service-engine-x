"""Ticket models for request/response schemas."""

from typing import Any

from pydantic import BaseModel, Field


# Status mapping: 1=Open, 2=Pending, 3=Closed
TICKET_STATUS_MAP: dict[int, str] = {
    1: "Open",
    2: "Pending",
    3: "Closed",
}

VALID_TICKET_STATUSES = [1, 2, 3]


class TicketEmployeeResponse(BaseModel):
    """Employee assigned to a ticket."""

    id: str
    name_f: str | None
    name_l: str | None
    role_id: str | None


class TicketClientResponse(BaseModel):
    """Client associated with a ticket."""

    id: str
    name: str
    name_f: str | None
    name_l: str | None
    email: str | None
    company: str | None
    phone: str | None
    balance: str | None = None
    address: dict[str, Any] | None
    role: dict[str, Any] | None


class TicketMessageResponse(BaseModel):
    """Message on a ticket."""

    id: str
    user_id: str
    message: str
    staff_only: bool
    files: list[Any]
    created_at: str


class TicketOrderResponse(BaseModel):
    """Order linked to a ticket."""

    id: str
    status: str
    service: str | None
    price: float
    quantity: int
    created_at: str


class TicketCreate(BaseModel):
    """Request body for creating a ticket."""

    user_id: str
    subject: str = Field(min_length=1)
    status: int | None = Field(default=1, ge=1, le=3)
    order_id: str | None = None
    employees: list[str] | None = None
    tags: list[str] | None = None
    note: str | None = None
    metadata: dict[str, Any] | None = None


class TicketUpdate(BaseModel):
    """Request body for updating a ticket."""

    subject: str | None = Field(default=None, min_length=1)
    status: int | None = Field(default=None, ge=1, le=3)
    order_id: str | None = None
    employees: list[str] | None = None
    tags: list[str] | None = None
    note: str | None = None
    metadata: dict[str, Any] | None = None


class TicketResponse(BaseModel):
    """Response schema for a single ticket (with messages)."""

    id: str
    subject: str
    user_id: str
    order_id: str | None
    status: str
    status_id: int
    source: str
    note: str | None
    form_data: dict[str, Any]
    metadata: dict[str, Any]
    tags: list[str]
    employees: list[TicketEmployeeResponse]
    client: TicketClientResponse | None
    order: TicketOrderResponse | None = None
    messages: list[TicketMessageResponse] = []
    created_at: str
    updated_at: str
    last_message_at: str | None
    date_closed: str | None


class TicketListItem(BaseModel):
    """Response schema for ticket in list (without messages)."""

    id: str
    subject: str
    user_id: str
    order_id: str | None
    status: str
    status_id: int
    source: str
    note: str | None
    form_data: dict[str, Any]
    metadata: dict[str, Any]
    tags: list[str]
    employees: list[TicketEmployeeResponse]
    client: TicketClientResponse | None
    created_at: str
    updated_at: str
    last_message_at: str | None
    date_closed: str | None


class TicketListLinks(BaseModel):
    """Pagination links for ticket list."""

    first: str
    last: str
    prev: str | None
    next: str | None


class TicketListMeta(BaseModel):
    """Pagination metadata for ticket list."""

    current_page: int
    from_: int = Field(alias="from")
    to: int
    last_page: int
    per_page: int
    total: int
    path: str

    model_config = {"populate_by_name": True}


class TicketListResponse(BaseModel):
    """Response schema for paginated ticket list."""

    data: list[TicketListItem]
    links: TicketListLinks
    meta: TicketListMeta
