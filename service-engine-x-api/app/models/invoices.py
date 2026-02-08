"""Invoice models for request/response schemas."""

from typing import Any

from pydantic import BaseModel, EmailStr, Field


# Status mapping: 0=Draft, 1=Unpaid, 3=Paid, 4=Refunded, 5=Cancelled, 7=Partially Paid
INVOICE_STATUS_MAP: dict[int, str] = {
    0: "Draft",
    1: "Unpaid",
    3: "Paid",
    4: "Refunded",
    5: "Cancelled",
    7: "Partially Paid",
}

# Valid statuses for creation/update
VALID_INVOICE_STATUSES = [0, 1, 3, 4, 5, 7]

# Valid status transitions
INVOICE_STATUS_TRANSITIONS: dict[int, list[int]] = {
    0: [1, 5],        # Draft -> Unpaid, Cancelled
    1: [0, 5],        # Unpaid -> Draft, Cancelled
    3: [4],           # Paid -> Refunded only
    4: [],            # Refunded -> terminal
    5: [0, 1],        # Cancelled -> Draft, Unpaid
    7: [3, 4, 5],     # Partially Paid -> Paid, Refunded, Cancelled
}


class RecurringConfig(BaseModel):
    """Recurring invoice configuration."""

    r_period_l: int = Field(ge=1, description="Recurring period length")
    r_period_t: str = Field(pattern="^[MWD]$", description="Period type: M=Month, W=Week, D=Day")


class InvoiceItemInput(BaseModel):
    """Input schema for invoice item."""

    name: str = Field(min_length=1)
    description: str | None = None
    quantity: int = Field(ge=1)
    amount: float
    discount: float = 0
    service_id: str | None = None
    options: dict[str, Any] | None = None


class CreateInvoiceRequest(BaseModel):
    """Request body for creating an invoice."""

    user_id: str | None = None
    email: EmailStr | None = None
    items: list[InvoiceItemInput] = Field(min_length=1)
    status: int | None = Field(default=1, ge=0)
    tax: float = 0
    tax_type: int | None = None  # 1=fixed, 2=percentage
    recurring: RecurringConfig | None = None
    coupon_id: str | None = None
    note: str | None = None
    user_data: dict[str, Any] | None = None  # For creating new client


class UpdateInvoiceRequest(BaseModel):
    """Request body for updating an invoice."""

    user_id: str | None = None
    items: list[InvoiceItemInput] = Field(min_length=1)
    status: int | None = None
    tax: float | None = None
    tax_type: int | None = None
    recurring: RecurringConfig | None = None
    coupon_id: str | None = None
    note: str | None = None


class ChargeInvoiceRequest(BaseModel):
    """Request body for charging an invoice."""

    payment_method_id: str = Field(min_length=1)


class InvoiceItemResponse(BaseModel):
    """Response schema for invoice item."""

    id: str
    invoice_id: str
    name: str
    description: str | None
    quantity: int
    amount: str
    discount: str
    discount2: str | None = None
    total: str
    service_id: str | None
    order_id: str | None
    options: dict[str, Any] | None
    created_at: str | None = None
    updated_at: str | None = None


class InvoiceAddressResponse(BaseModel):
    """Billing address response schema."""

    line_1: str | None
    line_2: str | None
    city: str | None
    state: str | None
    postcode: str | None
    country: str | None
    name_f: str | None
    name_l: str | None
    company_name: str | None
    company_vat: str | None
    tax_id: str | None


class InvoiceClientResponse(BaseModel):
    """Client response schema for invoice."""

    id: str
    name: str
    name_f: str | None
    name_l: str | None
    email: str | None
    company: str | None
    phone: str | None
    tax_id: str | None
    aff_id: str | None = None
    stripe_id: str | None = None
    balance: str | None = None
    custom_fields: dict[str, Any] | None = None
    status: int | None = None
    address: dict[str, Any] | None = None
    role: dict[str, Any] | None = None


class InvoiceResponse(BaseModel):
    """Response schema for a single invoice."""

    id: str
    number: str
    number_prefix: str | None
    client: InvoiceClientResponse | None
    items: list[InvoiceItemResponse]
    billing_address: dict[str, Any] | None
    status: str
    status_id: int
    created_at: str
    date_due: str | None
    date_paid: str | None
    credit: str | None
    tax: str | None
    tax_name: str | None
    tax_percent: str | None
    currency: str
    reason: str | None = None
    note: str | None
    ip_address: str | None = None
    loc_confirm: bool | None = None
    recurring: RecurringConfig | None = None
    coupon_id: str | None
    transaction_id: str | None
    paysys: str | None
    subtotal: str
    total: str
    employee_id: str | None = None
    view_link: str | None = None
    download_link: str | None = None
    thanks_link: str | None = None


class InvoiceListItem(BaseModel):
    """Response schema for invoice in list."""

    id: str
    number: str
    number_prefix: str | None
    client: InvoiceClientResponse | None
    items: list[InvoiceItemResponse]
    billing_address: dict[str, Any] | None
    status: str
    status_id: int
    created_at: str
    date_due: str | None
    date_paid: str | None
    credit: str | None
    tax: str | None
    tax_name: str | None
    tax_percent: str | None
    currency: str
    reason: str | None = None
    note: str | None
    ip_address: str | None = None
    loc_confirm: bool | None = None
    recurring: RecurringConfig | None = None
    coupon_id: str | None
    transaction_id: str | None
    paysys: str | None
    subtotal: str
    total: str
    employee_id: str | None = None
    view_link: str | None = None
    download_link: str | None = None
    thanks_link: str | None = None


class InvoiceListLinks(BaseModel):
    """Pagination links for invoice list."""

    first: str
    last: str
    prev: str | None
    next: str | None


class InvoiceListMeta(BaseModel):
    """Pagination metadata for invoice list."""

    current_page: int
    from_: int = Field(alias="from")
    to: int
    last_page: int
    per_page: int
    total: int
    path: str

    model_config = {"populate_by_name": True}


class InvoiceListResponse(BaseModel):
    """Response schema for paginated invoice list."""

    data: list[InvoiceListItem]
    links: InvoiceListLinks
    meta: InvoiceListMeta
