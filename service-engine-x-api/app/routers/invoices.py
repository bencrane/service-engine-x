"""Invoices API router."""

import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response

from app.auth.dependencies import AuthContext, get_current_org
from app.database import get_supabase
from app.utils import format_currency, format_currency_optional
from app.models.invoices import (
    INVOICE_STATUS_MAP,
    INVOICE_STATUS_TRANSITIONS,
    VALID_INVOICE_STATUSES,
    ChargeInvoiceRequest,
    CreateInvoiceRequest,
    InvoiceClientResponse,
    InvoiceItemResponse,
    InvoiceListItem,
    InvoiceListLinks,
    InvoiceListMeta,
    InvoiceListResponse,
    InvoiceResponse,
    UpdateInvoiceRequest,
)

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])


def serialize_invoice_item(item: dict[str, Any]) -> InvoiceItemResponse:
    """Serialize an invoice item."""
    return InvoiceItemResponse(
        id=item["id"],
        invoice_id=item["invoice_id"],
        name=item["name"],
        description=item.get("description"),
        quantity=item["quantity"],
        amount=format_currency(item.get("amount")),
        discount=format_currency(item.get("discount")),
        discount2=format_currency_optional(item.get("discount2")),
        total=format_currency(item.get("total")),
        service_id=item.get("service_id"),
        order_id=item.get("order_id"),
        options=item.get("options"),
        created_at=item.get("created_at"),
        updated_at=item.get("updated_at"),
    )


def serialize_invoice_client(client: dict[str, Any]) -> InvoiceClientResponse:
    """Serialize a client for invoice response."""
    # Handle Supabase join returning array for addresses
    addresses = client.get("addresses")
    if isinstance(addresses, list) and len(addresses) > 0:
        address = addresses[0]
    elif isinstance(addresses, dict):
        address = addresses
    else:
        address = None

    # Handle Supabase join returning array for roles
    roles = client.get("roles")
    if isinstance(roles, list) and len(roles) > 0:
        role = roles[0]
    elif isinstance(roles, dict):
        role = roles
    else:
        role = None

    return InvoiceClientResponse(
        id=client["id"],
        name=f"{client.get('name_f', '') or ''} {client.get('name_l', '') or ''}".strip(),
        name_f=client.get("name_f"),
        name_l=client.get("name_l"),
        email=client.get("email"),
        company=client.get("company"),
        phone=client.get("phone"),
        tax_id=client.get("tax_id"),
        aff_id=client.get("aff_id"),
        stripe_id=client.get("stripe_id"),
        balance=format_currency_optional(client.get("balance")),
        custom_fields=client.get("custom_fields"),
        status=client.get("status"),
        address=address,
        role=role,
    )


def serialize_invoice(invoice: dict[str, Any]) -> InvoiceResponse:
    """Serialize an invoice with client and items."""
    status_id = invoice.get("status", 0)

    # Handle client
    client_data = invoice.get("users")
    client = serialize_invoice_client(client_data) if client_data else None

    # Handle items
    items_data = invoice.get("invoice_items") or []
    items = [serialize_invoice_item(item) for item in items_data]

    # Handle recurring
    recurring = invoice.get("recurring")

    return InvoiceResponse(
        id=invoice["id"],
        number=invoice["number"],
        number_prefix=invoice.get("number_prefix"),
        client=client,
        items=items,
        billing_address=invoice.get("billing_address"),
        status=INVOICE_STATUS_MAP.get(status_id, "Unknown"),
        status_id=status_id,
        created_at=invoice["created_at"],
        date_due=invoice.get("date_due"),
        date_paid=invoice.get("date_paid"),
        credit=format_currency_optional(invoice.get("credit")),
        tax=format_currency_optional(invoice.get("tax")),
        tax_name=invoice.get("tax_name"),
        tax_percent=format_currency_optional(invoice.get("tax_percent")),
        currency=invoice.get("currency", "USD"),
        reason=invoice.get("reason"),
        note=invoice.get("note"),
        ip_address=invoice.get("ip_address"),
        loc_confirm=invoice.get("loc_confirm"),
        recurring=recurring,
        coupon_id=invoice.get("coupon_id"),
        transaction_id=invoice.get("transaction_id"),
        paysys=invoice.get("paysys"),
        subtotal=format_currency(invoice.get("subtotal")),
        total=format_currency(invoice.get("total")),
        employee_id=invoice.get("employee_id"),
        view_link=invoice.get("view_link"),
        download_link=invoice.get("download_link"),
        thanks_link=invoice.get("thanks_link"),
    )


def serialize_invoice_list_item(invoice: dict[str, Any]) -> InvoiceListItem:
    """Serialize an invoice for list response."""
    status_id = invoice.get("status", 0)

    # Handle client
    client_data = invoice.get("users")
    client = serialize_invoice_client(client_data) if client_data else None

    # Handle items
    items_data = invoice.get("invoice_items") or []
    items = [serialize_invoice_item(item) for item in items_data]

    recurring = invoice.get("recurring")

    return InvoiceListItem(
        id=invoice["id"],
        number=invoice["number"],
        number_prefix=invoice.get("number_prefix"),
        client=client,
        items=items,
        billing_address=invoice.get("billing_address"),
        status=INVOICE_STATUS_MAP.get(status_id, "Unknown"),
        status_id=status_id,
        created_at=invoice["created_at"],
        date_due=invoice.get("date_due"),
        date_paid=invoice.get("date_paid"),
        credit=format_currency_optional(invoice.get("credit")),
        tax=format_currency_optional(invoice.get("tax")),
        tax_name=invoice.get("tax_name"),
        tax_percent=format_currency_optional(invoice.get("tax_percent")),
        currency=invoice.get("currency", "USD"),
        reason=invoice.get("reason"),
        note=invoice.get("note"),
        ip_address=invoice.get("ip_address"),
        loc_confirm=invoice.get("loc_confirm"),
        recurring=recurring,
        coupon_id=invoice.get("coupon_id"),
        transaction_id=invoice.get("transaction_id"),
        paysys=invoice.get("paysys"),
        subtotal=format_currency(invoice.get("subtotal")),
        total=format_currency(invoice.get("total")),
        employee_id=invoice.get("employee_id"),
        view_link=invoice.get("view_link"),
        download_link=invoice.get("download_link"),
        thanks_link=invoice.get("thanks_link"),
    )


async def generate_invoice_number(supabase: Any) -> str:
    """Generate a unique invoice number."""
    count_result = await supabase.table("invoices").select(
        "*", count="exact", head=True
    ).execute()
    count = count_result.count or 0
    return f"INV-{str(count + 1).zfill(5)}"


@router.get("", response_model=InvoiceListResponse)
async def list_invoices(
    request: Request,
    auth: AuthContext = Depends(get_current_org),
    limit: int = Query(default=20, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    sort: str = Query(default="created_at:desc"),
) -> InvoiceListResponse:
    """List invoices with pagination."""
    supabase = get_supabase()
    offset = (page - 1) * limit

    # Parse sort parameter
    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if sort_parts else "created_at"
    sort_dir = sort_parts[1] if len(sort_parts) > 1 else "desc"
    ascending = sort_dir == "asc"

    # Get count
    count_result = await supabase.table("invoices").select(
        "*", count="exact", head=True
    ).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    total = count_result.count or 0

    # Get data with relations
    query = supabase.table("invoices").select(
        "*, users:user_id (id, name_f, name_l, email, company, phone, tax_id, addresses:address_id (*), roles:role_id (*)), invoice_items (*)"
    ).eq("org_id", auth.org_id).is_("deleted_at", "null").order(
        sort_field, desc=not ascending
    ).range(offset, offset + limit - 1)

    # Apply filters from query params
    params = dict(request.query_params)
    filterable_fields = ["id", "status", "user_id", "created_at", "date_due"]

    for key, value in params.items():
        if key.startswith("filters["):
            import re
            match = re.match(r"filters\[(\w+)\]\[(\$\w+)\]", key)
            if match:
                field, operator = match.groups()
                if field not in filterable_fields:
                    continue

                if operator == "$eq":
                    query = query.eq(field, value)
                elif operator == "$lt":
                    query = query.lt(field, value)
                elif operator == "$gt":
                    query = query.gt(field, value)

    result = await query.execute()
    invoices = result.data or []

    # Build response
    last_page = max(1, (total + limit - 1) // limit)
    base_url = str(request.url).split("?")[0]

    return InvoiceListResponse(
        data=[serialize_invoice_list_item(inv) for inv in invoices],
        links=InvoiceListLinks(
            first=f"{base_url}?page=1&limit={limit}",
            last=f"{base_url}?page={last_page}&limit={limit}",
            prev=f"{base_url}?page={page - 1}&limit={limit}" if page > 1 else None,
            next=f"{base_url}?page={page + 1}&limit={limit}" if page < last_page else None,
        ),
        meta=InvoiceListMeta(
            current_page=page,
            from_=offset + 1 if total > 0 else 0,
            to=min(offset + limit, total),
            last_page=last_page,
            per_page=limit,
            total=total,
            path=base_url,
        ),
    )


@router.post("", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    body: CreateInvoiceRequest,
    auth: AuthContext = Depends(get_current_org),
) -> InvoiceResponse:
    """Create a new invoice."""
    supabase = get_supabase()

    # Validate user_id or email required
    if not body.user_id and not body.email:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "The given data was invalid.",
                "errors": {"user_id": ["Either user_id or email is required."]},
            },
        )

    # Validate status
    if body.status is not None and body.status not in VALID_INVOICE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "The given data was invalid.",
                "errors": {"status": ["The selected status is invalid."]},
            },
        )

    # Resolve client
    client_id = body.user_id
    if not client_id and body.email:
        # Check if user exists
        existing_user = await supabase.table("users").select("id").eq(
            "email", body.email
        ).eq("org_id", auth.org_id).execute()

        if existing_user.data:
            client_id = existing_user.data[0]["id"]
        else:
            # Create new client
            user_data = body.user_data or {}
            new_user_result = await supabase.table("users").insert({
                "org_id": auth.org_id,
                "email": body.email,
                "name_f": user_data.get("name_f", ""),
                "name_l": user_data.get("name_l", ""),
                **{k: v for k, v in user_data.items() if k not in ["name_f", "name_l", "email"]},
            }).select("id").execute()

            if not new_user_result.data:
                raise HTTPException(status_code=500, detail="Failed to create client.")
            client_id = new_user_result.data[0]["id"]

    # Validate client exists
    client_result = await supabase.table("users").select(
        "id, name_f, name_l, company, address_id, addresses:address_id (*)"
    ).eq("id", client_id).eq("org_id", auth.org_id).execute()

    if not client_result.data:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "The given data was invalid.",
                "errors": {"user_id": ["The specified client does not exist."]},
            },
        )

    client = client_result.data[0]

    # Validate coupon if provided
    if body.coupon_id:
        coupon_result = await supabase.table("coupons").select("id").eq(
            "id", body.coupon_id
        ).execute()

        if not coupon_result.data:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "The given data was invalid.",
                    "errors": {"coupon_id": ["The specified coupon does not exist."]},
                },
            )

    # Calculate totals
    subtotal = 0.0
    for item in body.items:
        item_total = item.quantity * item.amount - item.discount
        subtotal += item_total

    tax = body.tax or 0
    total = subtotal + tax

    # Generate invoice number
    invoice_number = await generate_invoice_number(supabase)

    # Snapshot billing address
    addresses = client.get("addresses")
    if isinstance(addresses, list) and len(addresses) > 0:
        client_address = addresses[0]
    elif isinstance(addresses, dict):
        client_address = addresses
    else:
        client_address = None

    billing_address = None
    if client_address:
        billing_address = {
            "line_1": client_address.get("line_1"),
            "line_2": client_address.get("line_2"),
            "city": client_address.get("city"),
            "state": client_address.get("state"),
            "postcode": client_address.get("postcode"),
            "country": client_address.get("country"),
            "name_f": client.get("name_f"),
            "name_l": client.get("name_l"),
            "company_name": client.get("company"),
            "company_vat": None,
            "tax_id": None,
        }

    # Calculate due date (14 days default)
    now = datetime.now(timezone.utc)
    due_date = now + timedelta(days=14)

    # Create invoice
    invoice_data = {
        "org_id": auth.org_id,
        "number": invoice_number,
        "number_prefix": "INV-",
        "user_id": client_id,
        "billing_address": billing_address,
        "status": body.status if body.status is not None else 1,
        "created_at": now.isoformat(),
        "date_due": due_date.isoformat(),
        "date_paid": None,
        "credit": 0,
        "tax": tax,
        "tax_name": "Tax" if body.tax_type else None,
        "tax_percent": body.tax if body.tax_type == 2 else 0,
        "currency": "USD",
        "reason": None,
        "note": body.note,
        "ip_address": None,
        "loc_confirm": False,
        "recurring": body.recurring.model_dump() if body.recurring else None,
        "coupon_id": body.coupon_id,
        "transaction_id": None,
        "paysys": None,
        "subtotal": subtotal,
        "total": total,
        "employee_id": None,
    }

    invoice_result = await supabase.table("invoices").insert(invoice_data).select().execute()

    if not invoice_result.data:
        raise HTTPException(status_code=500, detail="Failed to create invoice")

    invoice = invoice_result.data[0]

    # Create invoice items
    item_rows = [
        {
            "invoice_id": invoice["id"],
            "name": item.name,
            "description": item.description,
            "quantity": item.quantity,
            "amount": item.amount,
            "discount": item.discount,
            "discount2": 0,
            "total": item.quantity * item.amount - item.discount,
            "service_id": item.service_id,
            "order_id": None,
            "options": item.options or {},
        }
        for item in body.items
    ]

    items_result = await supabase.table("invoice_items").insert(item_rows).select().execute()

    # Fetch full invoice with relations
    full_invoice = await supabase.table("invoices").select(
        "*, users:user_id (id, name_f, name_l, email, company, phone, tax_id, addresses:address_id (*), roles:role_id (*)), invoice_items (*)"
    ).eq("id", invoice["id"]).execute()

    if not full_invoice.data:
        raise HTTPException(status_code=500, detail="Failed to fetch created invoice")

    return serialize_invoice(full_invoice.data[0])


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def retrieve_invoice(
    invoice_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> InvoiceResponse:
    """Retrieve an invoice by ID."""
    supabase = get_supabase()

    result = await supabase.table("invoices").select(
        "*, users:user_id (id, name_f, name_l, email, company, phone, tax_id, aff_id, stripe_id, balance, custom_fields, status, addresses:address_id (*), roles:role_id (*)), invoice_items (*)"
    ).eq("id", invoice_id).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    return serialize_invoice(result.data[0])


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    body: UpdateInvoiceRequest,
    auth: AuthContext = Depends(get_current_org),
) -> InvoiceResponse:
    """Update an invoice."""
    supabase = get_supabase()

    # Fetch existing invoice
    existing_result = await supabase.table("invoices").select(
        "*, users:user_id (*)"
    ).eq("id", invoice_id).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not existing_result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    existing = existing_result.data[0]

    # Validate status transition
    if body.status is not None:
        if body.status not in VALID_INVOICE_STATUSES:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "The given data was invalid.",
                    "errors": {"status": ["The selected status is invalid."]},
                },
            )

        current_status = existing["status"]
        if body.status != current_status:
            allowed = INVOICE_STATUS_TRANSITIONS.get(current_status, [])
            if body.status not in allowed:
                current_name = INVOICE_STATUS_MAP.get(current_status, "Unknown")
                new_name = INVOICE_STATUS_MAP.get(body.status, "Unknown")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "The given data was invalid.",
                        "errors": {"status": [f"Cannot transition from {current_name} to {new_name}."]},
                    },
                )

    # Validate user_id if changing
    client_id = existing["user_id"]
    if body.user_id and body.user_id != existing["user_id"]:
        client_result = await supabase.table("users").select("id").eq(
            "id", body.user_id
        ).eq("org_id", auth.org_id).execute()

        if not client_result.data:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "The given data was invalid.",
                    "errors": {"user_id": ["The specified client does not exist."]},
                },
            )
        client_id = body.user_id

    # Validate coupon if provided
    if body.coupon_id:
        coupon_result = await supabase.table("coupons").select("id").eq(
            "id", body.coupon_id
        ).execute()

        if not coupon_result.data:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "The given data was invalid.",
                    "errors": {"coupon_id": ["The specified coupon does not exist."]},
                },
            )

    # Calculate new totals
    subtotal = 0.0
    for item in body.items:
        item_total = item.quantity * item.amount - item.discount
        subtotal += item_total

    tax = body.tax if body.tax is not None else existing["tax"]
    total = subtotal + tax

    # Update invoice
    now = datetime.now(timezone.utc).isoformat()
    update_data: dict[str, Any] = {
        "user_id": client_id,
        "subtotal": subtotal,
        "total": total,
        "updated_at": now,
    }

    if body.status is not None:
        update_data["status"] = body.status
    if body.tax is not None:
        update_data["tax"] = body.tax
    if body.tax_type is not None:
        update_data["tax_type"] = body.tax_type
    if body.recurring is not None:
        update_data["recurring"] = body.recurring.model_dump()
    elif body.recurring is None and "recurring" in body.model_fields_set:
        update_data["recurring"] = None
    if body.coupon_id is not None:
        update_data["coupon_id"] = body.coupon_id
    if body.note is not None:
        update_data["note"] = body.note

    await supabase.table("invoices").update(update_data).eq("id", invoice_id).execute()

    # Full replacement of items - delete old, insert new
    await supabase.table("invoice_items").delete().eq("invoice_id", invoice_id).execute()

    item_rows = [
        {
            "invoice_id": invoice_id,
            "name": item.name,
            "description": item.description,
            "quantity": item.quantity,
            "amount": item.amount,
            "discount": item.discount,
            "discount2": 0,
            "total": item.quantity * item.amount - item.discount,
            "service_id": item.service_id,
            "order_id": None,
            "options": item.options or {},
        }
        for item in body.items
    ]

    await supabase.table("invoice_items").insert(item_rows).select().execute()

    # Fetch updated invoice
    updated_result = await supabase.table("invoices").select(
        "*, users:user_id (id, name_f, name_l, email, company, phone, tax_id, addresses:address_id (*), roles:role_id (*)), invoice_items (*)"
    ).eq("id", invoice_id).execute()

    if not updated_result.data:
        raise HTTPException(status_code=500, detail="Failed to fetch updated invoice")

    return serialize_invoice(updated_result.data[0])


@router.delete("/{invoice_id}", status_code=204)
async def delete_invoice(
    invoice_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> Response:
    """Soft delete an invoice."""
    supabase = get_supabase()

    # Check if invoice exists
    existing_result = await supabase.table("invoices").select("id, deleted_at").eq(
        "id", invoice_id
    ).eq("org_id", auth.org_id).execute()

    if not existing_result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    if existing_result.data[0].get("deleted_at"):
        raise HTTPException(status_code=404, detail="Not Found")

    # Soft delete
    now = datetime.now(timezone.utc).isoformat()
    await supabase.table("invoices").update({"deleted_at": now}).eq("id", invoice_id).execute()

    return Response(status_code=204)


@router.post("/{invoice_id}/charge", response_model=InvoiceResponse)
async def charge_invoice(
    invoice_id: str,
    body: ChargeInvoiceRequest,
    request: Request,
    auth: AuthContext = Depends(get_current_org),
) -> InvoiceResponse:
    """Charge an invoice via payment processor."""
    supabase = get_supabase()

    # Fetch invoice
    result = await supabase.table("invoices").select(
        "*, users:user_id (*), invoice_items (*)"
    ).eq("id", invoice_id).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    invoice = result.data[0]

    # Check if already paid
    if invoice["status"] == 3:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "The given data was invalid.",
                "errors": {"payment_method_id": ["Invoice is already paid."]},
            },
        )

    # Check if invoice has client
    if not invoice["user_id"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "The given data was invalid.",
                "errors": {"payment_method_id": ["Invoice has no client assigned."]},
            },
        )

    # TODO: Integrate with Stripe to process payment
    # For now, simulate successful payment
    now = datetime.now(timezone.utc)
    transaction_id = f"txn_{int(now.timestamp())}_{secrets.token_hex(4)}"

    # Get client IP
    client_ip = request.client.host if request.client else None

    # Update invoice as paid
    await supabase.table("invoices").update({
        "status": 3,
        "date_paid": now.isoformat(),
        "transaction_id": transaction_id,
        "paysys": "Stripe",
        "ip_address": client_ip,
        "updated_at": now.isoformat(),
    }).eq("id", invoice_id).execute()

    # Create orders for items with service_id
    items = invoice.get("invoice_items") or []
    for item in items:
        if item.get("service_id"):
            order_result = await supabase.table("orders").insert({
                "org_id": auth.org_id,
                "user_id": invoice["user_id"],
                "service_id": item["service_id"],
                "invoice_id": invoice["id"],
                "status": 0,
                "quantity": item["quantity"],
                "price": item["amount"],
                "currency": invoice["currency"],
            }).select("id").execute()

            if order_result.data:
                # Link item to order
                await supabase.table("invoice_items").update({
                    "order_id": order_result.data[0]["id"]
                }).eq("id", item["id"]).execute()

    # Fetch updated invoice
    updated_result = await supabase.table("invoices").select(
        "*, users:user_id (id, name_f, name_l, email, company, phone, tax_id, addresses:address_id (*), roles:role_id (*)), invoice_items (*)"
    ).eq("id", invoice_id).execute()

    if not updated_result.data:
        raise HTTPException(status_code=500, detail="Failed to fetch updated invoice")

    return serialize_invoice(updated_result.data[0])


@router.post("/{invoice_id}/mark_paid", response_model=InvoiceResponse)
async def mark_invoice_paid(
    invoice_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> InvoiceResponse:
    """Mark an invoice as manually paid."""
    supabase = get_supabase()

    # Fetch invoice
    result = await supabase.table("invoices").select(
        "*, users:user_id (*), invoice_items (*)"
    ).eq("id", invoice_id).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    invoice = result.data[0]

    # Idempotent: if already paid, return current state
    if invoice["status"] == 3:
        full_result = await supabase.table("invoices").select(
            "*, users:user_id (id, name_f, name_l, email, company, phone, tax_id, addresses:address_id (*), roles:role_id (*)), invoice_items (*)"
        ).eq("id", invoice_id).execute()
        return serialize_invoice(full_result.data[0])

    # Check if invoice has client
    if not invoice["user_id"]:
        raise HTTPException(status_code=400, detail="Invoice has no client assigned.")

    # Check if invoice is in valid state
    if invoice["status"] in [4, 5]:  # Refunded or Cancelled
        status_name = INVOICE_STATUS_MAP.get(invoice["status"], "Unknown")
        raise HTTPException(
            status_code=400,
            detail=f"Cannot mark {status_name} invoice as paid.",
        )

    now = datetime.now(timezone.utc)

    # Update invoice as paid (manual)
    await supabase.table("invoices").update({
        "status": 3,
        "date_paid": now.isoformat(),
        "paysys": "Manual",
        "updated_at": now.isoformat(),
    }).eq("id", invoice_id).execute()

    # Create orders for items with service_id
    items = invoice.get("invoice_items") or []
    for item in items:
        if item.get("service_id"):
            order_result = await supabase.table("orders").insert({
                "org_id": auth.org_id,
                "user_id": invoice["user_id"],
                "service_id": item["service_id"],
                "invoice_id": invoice["id"],
                "status": 0,
                "quantity": item["quantity"],
                "price": item["amount"],
                "currency": invoice["currency"],
            }).select("id").execute()

            if order_result.data:
                await supabase.table("invoice_items").update({
                    "order_id": order_result.data[0]["id"]
                }).eq("id", item["id"]).execute()

    # Create subscription if recurring
    recurring = invoice.get("recurring")
    if recurring:
        await supabase.table("subscriptions").insert({
            "org_id": auth.org_id,
            "user_id": invoice["user_id"],
            "invoice_id": invoice["id"],
            "status": 1,
            "r_period_l": recurring.get("r_period_l"),
            "r_period_t": recurring.get("r_period_t"),
        }).execute()

    # Fetch updated invoice
    updated_result = await supabase.table("invoices").select(
        "*, users:user_id (id, name_f, name_l, email, company, phone, tax_id, addresses:address_id (*), roles:role_id (*)), invoice_items (*)"
    ).eq("id", invoice_id).execute()

    if not updated_result.data:
        raise HTTPException(status_code=500, detail="Failed to fetch updated invoice")

    return serialize_invoice(updated_result.data[0])
