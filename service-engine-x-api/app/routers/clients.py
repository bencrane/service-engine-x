"""Clients API router."""

import random
import string
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse, Response

from app.auth import AuthContext, get_current_org
from app.config import get_settings
from app.database import get_supabase
from app.models.clients import (
    AddressResponse,
    ClientCreate,
    ClientResponse,
    ClientUpdate,
    RoleResponse,
)
from app.utils import build_pagination_response, format_currency, is_valid_uuid

router = APIRouter(prefix="/api/clients", tags=["Clients"])


def serialize_address(address: dict[str, Any] | None) -> AddressResponse | None:
    """Serialize address data to response model."""
    if not address:
        return None
    return AddressResponse(
        line_1=address.get("line_1"),
        line_2=address.get("line_2"),
        city=address.get("city"),
        state=address.get("state"),
        country=address.get("country"),
        postcode=address.get("postcode"),
        name_f=address.get("name_f"),
        name_l=address.get("name_l"),
        tax_id=address.get("tax_id"),
        company_name=address.get("company_name"),
        company_vat=address.get("company_vat"),
    )


def serialize_role(role: dict[str, Any]) -> RoleResponse:
    """Serialize role data to response model."""
    return RoleResponse(
        id=role["id"],
        name=role["name"],
        dashboard_access=role["dashboard_access"],
        order_access=role["order_access"],
        order_management=role["order_management"],
        ticket_access=role["ticket_access"],
        ticket_management=role["ticket_management"],
        invoice_access=role["invoice_access"],
        invoice_management=role["invoice_management"],
        clients=role["clients"],
        services=role["services"],
        coupons=role["coupons"],
        forms=role["forms"],
        messaging=role["messaging"],
        affiliates=role["affiliates"],
        settings_company=role["settings_company"],
        settings_payments=role["settings_payments"],
        settings_team=role["settings_team"],
        settings_modules=role["settings_modules"],
        settings_integrations=role["settings_integrations"],
        settings_orders=role["settings_orders"],
        settings_tickets=role["settings_tickets"],
        settings_accounts=role["settings_accounts"],
        settings_messages=role["settings_messages"],
        settings_tags=role["settings_tags"],
        settings_sidebar=role["settings_sidebar"],
        settings_dashboard=role["settings_dashboard"],
        settings_templates=role["settings_templates"],
        settings_emails=role["settings_emails"],
        settings_language=role["settings_language"],
        settings_logs=role["settings_logs"],
        created_at=role["created_at"],
        updated_at=role["updated_at"],
    )


def serialize_client(
    client: dict[str, Any],
    address: dict[str, Any] | None,
    role: dict[str, Any],
    spent: str | None = None,
) -> ClientResponse:
    """Serialize client data to response model."""
    return ClientResponse(
        id=client["id"],
        name=f"{client['name_f']} {client['name_l']}".strip(),
        name_f=client["name_f"],
        name_l=client["name_l"],
        email=client["email"],
        company=client.get("company"),
        phone=client.get("phone"),
        tax_id=client.get("tax_id"),
        address=serialize_address(address),
        note=client.get("note"),
        balance=format_currency(client.get("balance")),
        spent=spent,
        optin=client.get("optin"),
        stripe_id=client.get("stripe_id"),
        custom_fields=client.get("custom_fields", {}),
        status=client.get("status", 1),
        aff_id=client.get("aff_id"),
        aff_link=client.get("aff_link"),
        role_id=client["role_id"],
        role=serialize_role(role),
        ga_cid=client.get("ga_cid"),
        created_at=client["created_at"],
    )


def get_client_role(supabase) -> dict[str, Any]:
    """Get the client role (dashboard_access = 0)."""
    result = (
        supabase.table("roles")
        .select("*")
        .eq("dashboard_access", 0)
        .execute()
    )
    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Client role not configured",
        )
    return result.data[0]


def generate_affiliate_id() -> int:
    """Generate a random 6-digit affiliate ID."""
    return random.randint(100000, 999999)


def generate_affiliate_link() -> str:
    """Generate a random affiliate link."""
    chars = string.ascii_uppercase + string.digits
    code = "".join(random.choice(chars) for _ in range(6))
    return f"https://example.com/r/{code}"


@router.get("")
async def list_clients(
    request: Request,
    auth: AuthContext = Depends(get_current_org),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    sort: str = Query("created_at:desc"),
) -> dict[str, Any]:
    """
    List all clients for the authenticated organization.

    Supports pagination, sorting, and filtering.
    """
    supabase = get_supabase()
    settings = get_settings()

    # Get client role
    client_role = get_client_role(supabase)

    # Parse sort parameter
    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if sort_parts else "created_at"
    sort_dir = sort_parts[1] if len(sort_parts) > 1 else "desc"

    valid_sort_fields = ["id", "email", "name_f", "name_l", "status", "balance", "created_at"]
    if sort_field not in valid_sort_fields:
        sort_field = "created_at"
    ascending = sort_dir == "asc"

    # Build base query
    query = (
        supabase.table("users")
        .select("*, address:addresses(*), role:roles(*)", count="exact")
        .eq("org_id", auth.org_id)
        .eq("role_id", client_role["id"])
    )

    # Apply filters from query params
    for key, value in request.query_params.items():
        if key.startswith("filters["):
            # Parse filter format: filters[field][$op]
            import re
            match = re.match(r"filters\[(\w+)\]\[(\$\w+)\]", key)
            if match:
                field, op = match.groups()
                filterable = ["id", "email", "status", "balance", "created_at"]
                if field not in filterable:
                    continue
                if op == "$eq":
                    query = query.eq(field, value)
                elif op == "$lt":
                    query = query.lt(field, value)
                elif op == "$gt":
                    query = query.gt(field, value)
                elif op == "$in":
                    values = request.query_params.getlist(f"filters[{field}][$in][]")
                    if values:
                        query = query.in_(field, values)

    # Apply sorting
    query = query.order(sort_field, desc=not ascending)

    # Get total count first
    count_result = query.execute()
    total = count_result.count or 0

    # Apply pagination
    offset = (page - 1) * limit
    query = (
        supabase.table("users")
        .select("*, address:addresses(*), role:roles(*)")
        .eq("org_id", auth.org_id)
        .eq("role_id", client_role["id"])
        .order(sort_field, desc=not ascending)
        .range(offset, offset + limit - 1)
    )

    result = query.execute()
    clients = result.data or []

    # Serialize clients
    serialized = []
    for c in clients:
        # Handle array returns from Supabase joins
        addr_data = c.get("address")
        if isinstance(addr_data, list):
            addr_data = addr_data[0] if addr_data else None

        role_data = c.get("role")
        if isinstance(role_data, list):
            role_data = role_data[0] if role_data else client_role

        serialized.append(
            serialize_client(c, addr_data, role_data or client_role).model_dump()
        )

    # Build pagination response
    path = f"{settings.api_base_url}/api/clients"
    return build_pagination_response(serialized, total, page, limit, path)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_client(
    body: ClientCreate,
    auth: AuthContext = Depends(get_current_org),
) -> ClientResponse:
    """Create a new client."""
    supabase = get_supabase()

    # Get client role
    client_role = get_client_role(supabase)

    # Check for duplicate email
    existing = (
        supabase.table("users")
        .select("id")
        .eq("email", body.email.lower().strip())
        .execute()
    )
    if existing.data and len(existing.data) > 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "The given data was invalid.",
                "errors": {"email": ["The email has already been taken."]},
            },
        )

    # Create address if provided
    address_id = None
    address_data = None
    if body.address:
        addr_result = (
            supabase.table("addresses")
            .insert({
                "org_id": auth.org_id,
                "line_1": body.address.line_1,
                "line_2": body.address.line_2,
                "city": body.address.city,
                "state": body.address.state,
                "country": body.address.country,
                "postcode": body.address.postcode,
                "name_f": body.name_f,
                "name_l": body.name_l,
                "tax_id": body.tax_id,
                "company_name": body.company,
                "company_vat": None,
            })
            .execute()
        )
        if addr_result.data:
            address_id = addr_result.data[0]["id"]
            address_data = addr_result.data[0]

    # Create client
    aff_id = generate_affiliate_id()
    aff_link = generate_affiliate_link()

    user_data = {
        "org_id": auth.org_id,
        "email": body.email.lower().strip(),
        "name_f": body.name_f.strip(),
        "name_l": body.name_l.strip(),
        "company": body.company,
        "phone": body.phone,
        "tax_id": body.tax_id,
        "note": body.note,
        "role_id": client_role["id"],
        "status": body.status_id if body.status_id is not None else 1,
        "balance": "0.00",
        "spent": "0.00",
        "optin": body.optin,
        "stripe_id": body.stripe_id,
        "custom_fields": body.custom_fields or {},
        "aff_id": aff_id,
        "aff_link": aff_link,
        "ga_cid": None,
        "address_id": address_id,
        "created_at": body.created_at or datetime.now(timezone.utc).isoformat(),
    }

    result = supabase.table("users").insert(user_data).execute()

    if not result.data:
        # Cleanup address if user creation failed
        if address_id:
            supabase.table("addresses").delete().eq("id", address_id).execute()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create client",
        )

    new_user = result.data[0]
    return serialize_client(new_user, address_data, client_role, spent=None)


@router.get("/{client_id}")
async def retrieve_client(
    client_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> ClientResponse:
    """Retrieve a single client by ID."""
    if not is_valid_uuid(client_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()
    client_role = get_client_role(supabase)

    result = (
        supabase.table("users")
        .select("*, address:addresses(*), role:roles(*)")
        .eq("id", client_id)
        .eq("org_id", auth.org_id)
        .eq("role_id", client_role["id"])
        .execute()
    )

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    client = result.data[0]

    # Handle array returns from Supabase joins
    addr_data = client.get("address")
    if isinstance(addr_data, list):
        addr_data = addr_data[0] if addr_data else None

    role_data = client.get("role")
    if isinstance(role_data, list):
        role_data = role_data[0] if role_data else client_role

    # Calculate spent from paid invoices
    spent_result = (
        supabase.table("invoices")
        .select("total")
        .eq("user_id", client_id)
        .not_.is_("date_paid", "null")
        .execute()
    )

    spent = None
    if spent_result.data:
        total_spent = sum(float(inv.get("total", 0) or 0) for inv in spent_result.data)
        spent = f"{total_spent:.2f}"

    return serialize_client(client, addr_data, role_data or client_role, spent)


@router.put("/{client_id}")
async def update_client(
    client_id: str,
    body: ClientUpdate,
    auth: AuthContext = Depends(get_current_org),
) -> ClientResponse:
    """Update an existing client."""
    if not is_valid_uuid(client_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()
    client_role = get_client_role(supabase)

    # Get existing client
    existing_result = (
        supabase.table("users")
        .select("*")
        .eq("id", client_id)
        .eq("org_id", auth.org_id)
        .eq("role_id", client_role["id"])
        .execute()
    )

    if not existing_result.data or len(existing_result.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    existing = existing_result.data[0]

    # Check for duplicate email if changing
    if body.email is not None:
        email_check = (
            supabase.table("users")
            .select("id")
            .eq("email", body.email.lower().strip())
            .neq("id", client_id)
            .execute()
        )
        if email_check.data and len(email_check.data) > 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"email": ["The email has already been taken."]},
                },
            )

    # Handle address update
    address_id = existing.get("address_id")
    address_data = None

    if body.address is not None:
        addr_payload = {
            "line_1": body.address.line_1,
            "line_2": body.address.line_2,
            "city": body.address.city,
            "state": body.address.state,
            "country": body.address.country,
            "postcode": body.address.postcode,
            "name_f": body.name_f or existing["name_f"],
            "name_l": body.name_l or existing["name_l"],
            "tax_id": body.tax_id or existing.get("tax_id"),
            "company_name": body.company or existing.get("company"),
            "company_vat": None,
        }

        if existing.get("address_id"):
            # Update existing address
            addr_result = (
                supabase.table("addresses")
                .update(addr_payload)
                .eq("id", existing["address_id"])
                .execute()
            )
            if addr_result.data:
                address_data = addr_result.data[0]
        else:
            # Create new address
            addr_payload["org_id"] = auth.org_id
            addr_result = supabase.table("addresses").insert(addr_payload).execute()
            if addr_result.data:
                address_id = addr_result.data[0]["id"]
                address_data = addr_result.data[0]
    elif existing.get("address_id"):
        # Fetch existing address
        addr_result = (
            supabase.table("addresses")
            .select("*")
            .eq("id", existing["address_id"])
            .execute()
        )
        if addr_result.data:
            address_data = addr_result.data[0]

    # Build update payload
    update_payload: dict[str, Any] = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    if body.name_f is not None:
        update_payload["name_f"] = body.name_f.strip()
    if body.name_l is not None:
        update_payload["name_l"] = body.name_l.strip()
    if body.email is not None:
        update_payload["email"] = body.email.lower().strip()
    if body.company is not None:
        update_payload["company"] = body.company
    if body.phone is not None:
        update_payload["phone"] = body.phone
    if body.tax_id is not None:
        update_payload["tax_id"] = body.tax_id
    if body.note is not None:
        update_payload["note"] = body.note
    if body.optin is not None:
        update_payload["optin"] = body.optin
    if body.stripe_id is not None:
        update_payload["stripe_id"] = body.stripe_id
    if body.custom_fields is not None:
        update_payload["custom_fields"] = body.custom_fields
    if body.status_id is not None:
        update_payload["status"] = body.status_id
    if body.created_at is not None:
        update_payload["created_at"] = body.created_at
    if body.address is not None:
        update_payload["address_id"] = address_id

    # Update client
    result = (
        supabase.table("users")
        .update(update_payload)
        .eq("id", client_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update client",
        )

    updated_user = result.data[0]

    # Calculate spent
    spent_result = (
        supabase.table("invoices")
        .select("total")
        .eq("user_id", client_id)
        .not_.is_("date_paid", "null")
        .execute()
    )

    spent = None
    if spent_result.data:
        total_spent = sum(float(inv.get("total", 0) or 0) for inv in spent_result.data)
        spent = f"{total_spent:.2f}"

    return serialize_client(updated_user, address_data, client_role, spent)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> Response:
    """Delete a client (hard delete with FK guard)."""
    if not is_valid_uuid(client_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()
    client_role = get_client_role(supabase)

    # Verify client exists and belongs to org
    existing = (
        supabase.table("users")
        .select("id")
        .eq("id", client_id)
        .eq("org_id", auth.org_id)
        .eq("role_id", client_role["id"])
        .execute()
    )

    if not existing.data or len(existing.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # FK guard: check for dependent records
    orders = supabase.table("orders").select("id").eq("user_id", client_id).limit(1).execute()
    if orders.data and len(orders.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete client with existing orders",
        )

    invoices = supabase.table("invoices").select("id").eq("user_id", client_id).limit(1).execute()
    if invoices.data and len(invoices.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete client with existing invoices",
        )

    tickets = supabase.table("tickets").select("id").eq("user_id", client_id).limit(1).execute()
    if tickets.data and len(tickets.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete client with existing tickets",
        )

    subscriptions = (
        supabase.table("subscriptions").select("id").eq("user_id", client_id).limit(1).execute()
    )
    if subscriptions.data and len(subscriptions.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete client with existing subscriptions",
        )

    # Hard delete
    supabase.table("users").delete().eq("id", client_id).execute()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
