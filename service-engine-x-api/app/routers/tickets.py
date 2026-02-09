"""Tickets API router."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response

from app.auth.dependencies import AuthContext, get_current_org
from app.database import get_supabase
from app.utils import format_currency, format_currency_optional
from app.models.tickets import (
    TICKET_STATUS_MAP,
    VALID_TICKET_STATUSES,
    TicketClientResponse,
    TicketCreate,
    TicketEmployeeResponse,
    TicketListItem,
    TicketListLinks,
    TicketListMeta,
    TicketListResponse,
    TicketMessageResponse,
    TicketOrderResponse,
    TicketResponse,
    TicketUpdate,
)

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

ORDER_STATUS_MAP: dict[int, str] = {
    0: "Unpaid",
    1: "In Progress",
    2: "Completed",
    3: "Cancelled",
    4: "On Hold",
}


async def fetch_client(supabase: Any, user_id: str, org_id: str) -> TicketClientResponse | None:
    """Fetch client with address and role."""
    result = await supabase.table("users").select(
        "id, name_f, name_l, email, company, phone, balance, addresses:address_id (*), roles:role_id (*)"
    ).eq("id", user_id).eq("org_id", org_id).execute()

    if not result.data:
        return None

    user = result.data[0]

    # Handle Supabase join returning array
    addresses = user.get("addresses")
    if isinstance(addresses, list) and len(addresses) > 0:
        address = addresses[0]
    elif isinstance(addresses, dict):
        address = addresses
    else:
        address = None

    roles = user.get("roles")
    if isinstance(roles, list) and len(roles) > 0:
        role = roles[0]
    elif isinstance(roles, dict):
        role = roles
    else:
        role = None

    return TicketClientResponse(
        id=user["id"],
        name=f"{user.get('name_f', '') or ''} {user.get('name_l', '') or ''}".strip(),
        name_f=user.get("name_f"),
        name_l=user.get("name_l"),
        email=user.get("email"),
        company=user.get("company"),
        phone=user.get("phone"),
        balance=format_currency_optional(user.get("balance")),
        address=address,
        role=role,
    )


async def fetch_ticket_employees(supabase: Any, ticket_id: str) -> list[TicketEmployeeResponse]:
    """Fetch employees assigned to a ticket."""
    assignments_result = await supabase.table("ticket_employees").select(
        "employee_id"
    ).eq("ticket_id", ticket_id).execute()

    if not assignments_result.data:
        return []

    employee_ids = [a["employee_id"] for a in assignments_result.data]

    employees_result = await supabase.table("users").select(
        "id, name_f, name_l, role_id"
    ).in_("id", employee_ids).execute()

    return [
        TicketEmployeeResponse(
            id=emp["id"],
            name_f=emp.get("name_f"),
            name_l=emp.get("name_l"),
            role_id=emp.get("role_id"),
        )
        for emp in (employees_result.data or [])
    ]


async def fetch_ticket_tags(supabase: Any, ticket_id: str) -> list[str]:
    """Fetch tags for a ticket."""
    tag_links_result = await supabase.table("ticket_tags").select(
        "tag_id"
    ).eq("ticket_id", ticket_id).execute()

    if not tag_links_result.data:
        return []

    tag_ids = [t["tag_id"] for t in tag_links_result.data]

    tags_result = await supabase.table("tags").select("name").in_("id", tag_ids).execute()

    return [t["name"] for t in (tags_result.data or [])]


async def fetch_ticket_messages(supabase: Any, ticket_id: str) -> list[TicketMessageResponse]:
    """Fetch messages for a ticket."""
    result = await supabase.table("ticket_messages").select(
        "id, user_id, message, staff_only, files, created_at"
    ).eq("ticket_id", ticket_id).order("created_at", desc=False).execute()

    return [
        TicketMessageResponse(
            id=msg["id"],
            user_id=msg["user_id"],
            message=msg["message"],
            staff_only=msg.get("staff_only", False),
            files=msg.get("files") or [],
            created_at=msg["created_at"],
        )
        for msg in (result.data or [])
    ]


async def fetch_ticket_order(supabase: Any, order_id: str | None, org_id: str) -> TicketOrderResponse | None:
    """Fetch linked order summary."""
    if not order_id:
        return None

    result = await supabase.table("orders").select(
        "id, status, service_name, price, quantity, created_at"
    ).eq("id", order_id).eq("org_id", org_id).is_("deleted_at", "null").execute()

    if not result.data:
        return None

    order = result.data[0]
    return TicketOrderResponse(
        id=order["id"],
        status=ORDER_STATUS_MAP.get(order["status"], "Unknown"),
        service=order.get("service_name"),
        price=float(format_currency(order.get("price"))),
        quantity=order.get("quantity", 1),
        created_at=order["created_at"],
    )


async def serialize_ticket_list_item(
    supabase: Any, ticket: dict[str, Any], org_id: str
) -> TicketListItem:
    """Serialize a ticket for list response (without messages)."""
    client, employees, tags = await fetch_client(supabase, ticket["user_id"], org_id), \
        await fetch_ticket_employees(supabase, ticket["id"]), \
        await fetch_ticket_tags(supabase, ticket["id"])

    status_id = ticket.get("status", 1)
    return TicketListItem(
        id=ticket["id"],
        subject=ticket["subject"],
        user_id=ticket["user_id"],
        order_id=ticket.get("order_id"),
        status=TICKET_STATUS_MAP.get(status_id, "Unknown"),
        status_id=status_id,
        source=ticket.get("source", "API"),
        note=ticket.get("note"),
        form_data=ticket.get("form_data") or {},
        metadata=ticket.get("metadata") or {},
        tags=tags,
        employees=employees,
        client=client,
        created_at=ticket["created_at"],
        updated_at=ticket["updated_at"],
        last_message_at=ticket.get("last_message_at"),
        date_closed=ticket.get("date_closed"),
    )


async def serialize_ticket_full(
    supabase: Any, ticket: dict[str, Any], org_id: str
) -> TicketResponse:
    """Serialize a ticket with all relations including messages."""
    client = await fetch_client(supabase, ticket["user_id"], org_id)
    employees = await fetch_ticket_employees(supabase, ticket["id"])
    tags = await fetch_ticket_tags(supabase, ticket["id"])
    messages = await fetch_ticket_messages(supabase, ticket["id"])
    order = await fetch_ticket_order(supabase, ticket.get("order_id"), org_id)

    status_id = ticket.get("status", 1)
    return TicketResponse(
        id=ticket["id"],
        subject=ticket["subject"],
        user_id=ticket["user_id"],
        order_id=ticket.get("order_id"),
        status=TICKET_STATUS_MAP.get(status_id, "Unknown"),
        status_id=status_id,
        source=ticket.get("source", "API"),
        note=ticket.get("note"),
        form_data=ticket.get("form_data") or {},
        metadata=ticket.get("metadata") or {},
        tags=tags,
        employees=employees,
        client=client,
        order=order,
        messages=messages,
        created_at=ticket["created_at"],
        updated_at=ticket["updated_at"],
        last_message_at=ticket.get("last_message_at"),
        date_closed=ticket.get("date_closed"),
    )


async def validate_employees(supabase: Any, employee_ids: list[str], org_id: str) -> str | None:
    """Validate employee IDs. Returns error message if invalid."""
    for emp_id in employee_ids:
        result = await supabase.table("users").select(
            "id, roles:role_id (dashboard_access)"
        ).eq("id", emp_id).eq("org_id", org_id).execute()

        if not result.data:
            return "The specified employee does not exist."

        user = result.data[0]
        roles = user.get("roles")

        # Handle Supabase join returning array
        if isinstance(roles, list) and len(roles) > 0:
            dashboard_access = roles[0].get("dashboard_access", 0)
        elif isinstance(roles, dict):
            dashboard_access = roles.get("dashboard_access", 0)
        else:
            dashboard_access = 0

        if dashboard_access == 0:
            return "The specified employee does not exist."

    return None


async def assign_tags(supabase: Any, ticket_id: str, tag_names: list[str]) -> None:
    """Assign tags to a ticket (find-or-create)."""
    for tag_name in tag_names:
        # Find existing tag
        tag_result = await supabase.table("tags").select("id").eq("name", tag_name).execute()

        if tag_result.data:
            tag_id = tag_result.data[0]["id"]
        else:
            # Create new tag
            new_tag_result = await supabase.table("tags").insert({"name": tag_name}).select("id").execute()
            if new_tag_result.data:
                tag_id = new_tag_result.data[0]["id"]
            else:
                continue

        # Link tag to ticket
        await supabase.table("ticket_tags").insert({
            "ticket_id": ticket_id,
            "tag_id": tag_id,
        }).execute()


@router.get("", response_model=TicketListResponse)
async def list_tickets(
    request: Request,
    auth: AuthContext = Depends(get_current_org),
    limit: int = Query(default=20, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    sort: str = Query(default="created_at:desc"),
) -> TicketListResponse:
    """List tickets with pagination."""
    supabase = get_supabase()
    offset = (page - 1) * limit

    # Parse sort parameter
    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if sort_parts else "created_at"
    sort_dir = sort_parts[1] if len(sort_parts) > 1 else "desc"

    valid_sort_fields = ["id", "subject", "status", "user_id", "order_id", "created_at", "last_message_at"]
    if sort_field not in valid_sort_fields:
        sort_field = "created_at"
    ascending = sort_dir == "asc"

    # Get count
    count_result = await supabase.table("tickets").select(
        "*", count="exact", head=True
    ).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    total = count_result.count or 0

    # Get data
    query = supabase.table("tickets").select("*").eq(
        "org_id", auth.org_id
    ).is_("deleted_at", "null").order(
        sort_field, desc=not ascending
    ).range(offset, offset + limit - 1)

    # Apply filters from query params
    params = dict(request.query_params)
    filterable_fields = ["user_id", "status", "order_id", "created_at", "last_message_at"]

    for key, value in params.items():
        if key.startswith("filters["):
            import re
            match = re.match(r"filters\[(\w+)\]\[(\$\w+)\]", key)
            if match:
                field, operator = match.groups()
                if field not in filterable_fields:
                    continue

                if operator == "$eq":
                    if value == "null":
                        query = query.is_(field, "null")
                    else:
                        query = query.eq(field, value)
                elif operator == "$lt":
                    query = query.lt(field, value)
                elif operator == "$gt":
                    query = query.gt(field, value)

    result = await query.execute()
    tickets = result.data or []

    # Serialize tickets
    serialized_tickets = []
    for ticket in tickets:
        serialized = await serialize_ticket_list_item(supabase, ticket, auth.org_id)
        serialized_tickets.append(serialized)

    # Build response
    last_page = max(1, (total + limit - 1) // limit)
    base_url = str(request.url).split("?")[0]

    return TicketListResponse(
        data=serialized_tickets,
        links=TicketListLinks(
            first=f"{base_url}?page=1&limit={limit}",
            last=f"{base_url}?page={last_page}&limit={limit}",
            prev=f"{base_url}?page={page - 1}&limit={limit}" if page > 1 else None,
            next=f"{base_url}?page={page + 1}&limit={limit}" if page < last_page else None,
        ),
        meta=TicketListMeta(
            current_page=page,
            from_=offset + 1 if total > 0 else 0,
            to=min(offset + limit, total),
            last_page=last_page,
            per_page=limit,
            total=total,
            path=base_url,
        ),
    )


@router.post("", response_model=TicketResponse, status_code=201)
async def create_ticket(
    body: TicketCreate,
    auth: AuthContext = Depends(get_current_org),
) -> TicketResponse:
    """Create a new ticket."""
    supabase = get_supabase()

    # Validate client exists in org
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

    # Validate status
    if body.status is not None and body.status not in VALID_TICKET_STATUSES:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "The given data was invalid.",
                "errors": {"status": ["The selected status is invalid."]},
            },
        )

    # Validate order_id if provided
    if body.order_id:
        order_result = await supabase.table("orders").select("id").eq(
            "id", body.order_id
        ).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

        if not order_result.data:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "The given data was invalid.",
                    "errors": {"order_id": ["The specified order does not exist."]},
                },
            )

    # Validate employees
    if body.employees:
        error = await validate_employees(supabase, body.employees, auth.org_id)
        if error:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "The given data was invalid.",
                    "errors": {"employees": [error]},
                },
            )

    # Create ticket
    ticket_data = {
        "org_id": auth.org_id,
        "user_id": body.user_id,
        "subject": body.subject.strip(),
        "status": body.status if body.status is not None else 1,
        "order_id": body.order_id,
        "note": body.note,
        "metadata": body.metadata or {},
        "form_data": {},
        "source": "API",
    }

    ticket_result = await supabase.table("tickets").insert(ticket_data).select().execute()

    if not ticket_result.data:
        raise HTTPException(status_code=500, detail="Failed to create ticket")

    ticket = ticket_result.data[0]

    # Assign employees
    if body.employees:
        employee_rows = [
            {"ticket_id": ticket["id"], "employee_id": emp_id}
            for emp_id in body.employees
        ]
        await supabase.table("ticket_employees").insert(employee_rows).execute()

    # Assign tags
    if body.tags:
        await assign_tags(supabase, ticket["id"], body.tags)

    return await serialize_ticket_full(supabase, ticket, auth.org_id)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def retrieve_ticket(
    ticket_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> TicketResponse:
    """Retrieve a ticket by ID."""
    supabase = get_supabase()

    result = await supabase.table("tickets").select("*").eq(
        "id", ticket_id
    ).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    return await serialize_ticket_full(supabase, result.data[0], auth.org_id)


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    body: TicketUpdate,
    auth: AuthContext = Depends(get_current_org),
) -> TicketResponse:
    """Update a ticket."""
    supabase = get_supabase()

    # Check ticket exists
    existing_result = await supabase.table("tickets").select("*").eq(
        "id", ticket_id
    ).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not existing_result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    existing = existing_result.data[0]

    # Validate status
    if body.status is not None and body.status not in VALID_TICKET_STATUSES:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "The given data was invalid.",
                "errors": {"status": ["The selected status is invalid."]},
            },
        )

    # Validate order_id if provided
    if body.order_id is not None and body.order_id != "":
        order_result = await supabase.table("orders").select("id").eq(
            "id", body.order_id
        ).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

        if not order_result.data:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "The given data was invalid.",
                    "errors": {"order_id": ["The specified order does not exist."]},
                },
            )

    # Validate employees
    if body.employees is not None:
        error = await validate_employees(supabase, body.employees, auth.org_id)
        if error:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "The given data was invalid.",
                    "errors": {"employees": [error]},
                },
            )

    # Build update payload
    now = datetime.now(timezone.utc).isoformat()
    update_data: dict[str, Any] = {"updated_at": now}

    if body.subject is not None:
        update_data["subject"] = body.subject.strip()
    if body.note is not None:
        update_data["note"] = body.note
    if body.order_id is not None:
        update_data["order_id"] = body.order_id if body.order_id != "" else None
    if body.metadata is not None:
        update_data["metadata"] = body.metadata

    # Handle status change
    if body.status is not None:
        update_data["status"] = body.status

        # Set date_closed when status changes to Closed (3)
        if body.status == 3 and existing["status"] != 3:
            update_data["date_closed"] = now
        # Clear date_closed when status changes from Closed to other
        elif body.status != 3 and existing["status"] == 3:
            update_data["date_closed"] = None

    # Update ticket
    await supabase.table("tickets").update(update_data).eq("id", ticket_id).execute()

    # Replace employees if provided
    if body.employees is not None:
        await supabase.table("ticket_employees").delete().eq("ticket_id", ticket_id).execute()

        if body.employees:
            employee_rows = [
                {"ticket_id": ticket_id, "employee_id": emp_id}
                for emp_id in body.employees
            ]
            await supabase.table("ticket_employees").insert(employee_rows).execute()

    # Replace tags if provided
    if body.tags is not None:
        await supabase.table("ticket_tags").delete().eq("ticket_id", ticket_id).execute()

        if body.tags:
            await assign_tags(supabase, ticket_id, body.tags)

    # Fetch updated ticket
    updated_result = await supabase.table("tickets").select("*").eq("id", ticket_id).execute()

    if not updated_result.data:
        raise HTTPException(status_code=500, detail="Failed to fetch updated ticket")

    return await serialize_ticket_full(supabase, updated_result.data[0], auth.org_id)


@router.delete("/{ticket_id}", status_code=204)
async def delete_ticket(
    ticket_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> Response:
    """Soft delete a ticket."""
    supabase = get_supabase()

    # Check ticket exists
    existing_result = await supabase.table("tickets").select("id").eq(
        "id", ticket_id
    ).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not existing_result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    # Soft delete
    now = datetime.now(timezone.utc).isoformat()
    await supabase.table("tickets").update({
        "deleted_at": now,
        "updated_at": now,
    }).eq("id", ticket_id).execute()

    return Response(status_code=204)
