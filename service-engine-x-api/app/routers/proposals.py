"""Proposals API router."""

import secrets
import string
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.auth.dependencies import AuthContext, get_current_org
from app.database import get_supabase
from app.models.proposals import (
    PROPOSAL_STATUS_MAP,
    CreateProposalRequest,
    ProposalItemResponse,
    ProposalListItem,
    ProposalListLinks,
    ProposalListMeta,
    ProposalListMetaLink,
    ProposalListResponse,
    ProposalResponse,
)

router = APIRouter(prefix="/api/proposals", tags=["Proposals"])


# Order status map for sign endpoint
ORDER_STATUS_MAP: dict[int, str] = {
    0: "Unpaid",
    1: "In Progress",
    2: "Completed",
    3: "Cancelled",
    4: "On Hold",
}


def generate_order_number() -> str:
    """Generate an 8-character alphanumeric order number."""
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(8))


def serialize_proposal_list_item(proposal: dict[str, Any]) -> ProposalListItem:
    """Serialize a proposal for list response (without items)."""
    status_id = proposal.get("status", 0)
    return ProposalListItem(
        id=proposal["id"],
        client_email=proposal["client_email"],
        client_name=f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip(),
        client_name_f=proposal.get("client_name_f", ""),
        client_name_l=proposal.get("client_name_l", ""),
        client_company=proposal.get("client_company"),
        status=PROPOSAL_STATUS_MAP.get(status_id, "Unknown"),
        status_id=status_id,
        total=str(proposal.get("total", "0.00")),
        notes=proposal.get("notes"),
        created_at=proposal["created_at"],
        updated_at=proposal["updated_at"],
        sent_at=proposal.get("sent_at"),
        signed_at=proposal.get("signed_at"),
        converted_order_id=proposal.get("converted_order_id"),
    )


def serialize_proposal_item(item: dict[str, Any]) -> ProposalItemResponse:
    """Serialize a proposal item."""
    # Handle Supabase join returning array
    services = item.get("services")
    if isinstance(services, list) and len(services) > 0:
        service = services[0]
    elif isinstance(services, dict):
        service = services
    else:
        service = None

    return ProposalItemResponse(
        id=item["id"],
        service_id=item["service_id"],
        service_name=service.get("name") if service else None,
        service_description=service.get("description") if service else None,
        quantity=item.get("quantity", 1),
        price=str(item.get("price", "0.00")),
        created_at=item["created_at"],
    )


def serialize_proposal(proposal: dict[str, Any], items: list[dict[str, Any]]) -> ProposalResponse:
    """Serialize a proposal with items."""
    status_id = proposal.get("status", 0)
    return ProposalResponse(
        id=proposal["id"],
        client_email=proposal["client_email"],
        client_name=f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip(),
        client_name_f=proposal.get("client_name_f", ""),
        client_name_l=proposal.get("client_name_l", ""),
        client_company=proposal.get("client_company"),
        status=PROPOSAL_STATUS_MAP.get(status_id, "Unknown"),
        status_id=status_id,
        total=str(proposal.get("total", "0.00")),
        notes=proposal.get("notes"),
        created_at=proposal["created_at"],
        updated_at=proposal["updated_at"],
        sent_at=proposal.get("sent_at"),
        signed_at=proposal.get("signed_at"),
        converted_order_id=proposal.get("converted_order_id"),
        items=[serialize_proposal_item(item) for item in items],
    )


def build_pagination_links(
    current_page: int, last_page: int, base_url: str, limit: int
) -> list[ProposalListMetaLink]:
    """Build pagination links for meta."""
    links: list[ProposalListMetaLink] = []

    # Previous link
    links.append(
        ProposalListMetaLink(
            url=f"{base_url}?page={current_page - 1}&limit={limit}" if current_page > 1 else None,
            label="Previous",
            active=False,
        )
    )

    # Page number links (up to 10)
    for i in range(1, min(last_page + 1, 11)):
        links.append(
            ProposalListMetaLink(
                url=f"{base_url}?page={i}&limit={limit}",
                label=str(i),
                active=i == current_page,
            )
        )

    # Next link
    links.append(
        ProposalListMetaLink(
            url=f"{base_url}?page={current_page + 1}&limit={limit}" if current_page < last_page else None,
            label="Next",
            active=False,
        )
    )

    return links


@router.get("", response_model=ProposalListResponse)
async def list_proposals(
    request: Request,
    auth: AuthContext = Depends(get_current_org),
    limit: int = Query(default=20, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    sort: str = Query(default="created_at:desc"),
) -> ProposalListResponse:
    """List proposals with pagination."""
    supabase = get_supabase()
    offset = (page - 1) * limit

    # Parse sort parameter
    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if sort_parts else "created_at"
    sort_dir = sort_parts[1] if len(sort_parts) > 1 else "desc"

    valid_sort_fields = ["id", "client_email", "status", "total", "created_at", "sent_at", "signed_at"]
    if sort_field not in valid_sort_fields:
        sort_field = "created_at"
    ascending = sort_dir == "asc"

    # Get count
    count_result = await supabase.table("proposals").select(
        "*", count="exact", head=True
    ).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    total = count_result.count or 0

    # Get data
    query = supabase.table("proposals").select("*").eq(
        "org_id", auth.org_id
    ).is_("deleted_at", "null").order(
        sort_field, desc=not ascending
    ).range(offset, offset + limit - 1)

    # Apply filters from query params
    params = dict(request.query_params)
    filterable_fields = ["id", "status", "client_email", "created_at"]

    for key, value in params.items():
        # Parse filter format: filters[field][$op]
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
    proposals = result.data or []

    # Build response
    last_page = max(1, (total + limit - 1) // limit)
    base_url = str(request.url).split("?")[0]

    return ProposalListResponse(
        data=[serialize_proposal_list_item(p) for p in proposals],
        links=ProposalListLinks(
            first=f"{base_url}?page=1&limit={limit}",
            last=f"{base_url}?page={last_page}&limit={limit}",
            prev=f"{base_url}?page={page - 1}&limit={limit}" if page > 1 else None,
            next=f"{base_url}?page={page + 1}&limit={limit}" if page < last_page else None,
        ),
        meta=ProposalListMeta(
            current_page=page,
            from_=offset + 1 if total > 0 else 0,
            to=min(offset + limit, total),
            last_page=last_page,
            per_page=limit,
            total=total,
            path=base_url,
            links=build_pagination_links(page, last_page, base_url, limit),
        ),
    )


@router.post("", response_model=ProposalResponse, status_code=201)
async def create_proposal(
    body: CreateProposalRequest,
    auth: AuthContext = Depends(get_current_org),
) -> ProposalResponse:
    """Create a new proposal."""
    supabase = get_supabase()

    # Validate all service_ids exist and belong to org
    service_ids = [item.service_id for item in body.items]
    services_result = await supabase.table("services").select("id").eq(
        "org_id", auth.org_id
    ).is_("deleted_at", "null").in_("id", service_ids).execute()

    found_service_ids = {s["id"] for s in (services_result.data or [])}
    missing_services = [sid for sid in service_ids if sid not in found_service_ids]

    if missing_services:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "The given data was invalid.",
                "errors": {"items": [f"Service with ID {missing_services[0]} does not exist."]},
            },
        )

    # Calculate total from items
    total = sum(item.quantity * item.price for item in body.items)

    # Create proposal
    proposal_data = {
        "org_id": auth.org_id,
        "client_email": body.client_email.lower().strip(),
        "client_name_f": body.client_name_f.strip(),
        "client_name_l": body.client_name_l.strip(),
        "client_company": body.client_company,
        "status": 0,  # Draft
        "total": total,
        "notes": body.notes,
    }

    proposal_result = await supabase.table("proposals").insert(proposal_data).select().execute()

    if not proposal_result.data:
        raise HTTPException(status_code=500, detail="Failed to create proposal")

    proposal = proposal_result.data[0]

    # Create proposal items
    item_rows = [
        {
            "proposal_id": proposal["id"],
            "service_id": item.service_id,
            "quantity": item.quantity,
            "price": item.price,
        }
        for item in body.items
    ]

    items_result = await supabase.table("proposal_items").insert(item_rows).select(
        "*, services:service_id (id, name, description)"
    ).execute()

    if not items_result.data:
        # Clean up proposal if items failed
        await supabase.table("proposals").delete().eq("id", proposal["id"]).execute()
        raise HTTPException(status_code=500, detail="Failed to create proposal items")

    return serialize_proposal(proposal, items_result.data)


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def retrieve_proposal(
    proposal_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> ProposalResponse:
    """Retrieve a proposal by ID."""
    supabase = get_supabase()

    # Fetch proposal with items
    result = await supabase.table("proposals").select(
        "*, proposal_items (*, services:service_id (id, name, description))"
    ).eq("id", proposal_id).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    proposal = result.data[0]
    items = proposal.get("proposal_items") or []

    return serialize_proposal(proposal, items)


@router.post("/{proposal_id}/send", response_model=ProposalResponse)
async def send_proposal(
    proposal_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> ProposalResponse:
    """Send a proposal (Draft -> Sent)."""
    supabase = get_supabase()

    # Fetch proposal with items
    result = await supabase.table("proposals").select(
        "*, proposal_items (*, services:service_id (id, name))"
    ).eq("id", proposal_id).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    proposal = result.data[0]

    # Check if proposal can be sent (must be Draft)
    if proposal["status"] != 0:
        status_name = PROPOSAL_STATUS_MAP.get(proposal["status"], "Unknown")
        raise HTTPException(
            status_code=400,
            detail=f"Cannot send proposal with status {status_name}",
        )

    # Update proposal
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()

    await supabase.table("proposals").update({
        "status": 1,
        "sent_at": now,
        "updated_at": now,
    }).eq("id", proposal_id).execute()

    # Update local proposal dict for response
    proposal["status"] = 1
    proposal["sent_at"] = now
    proposal["updated_at"] = now

    items = proposal.get("proposal_items") or []
    return serialize_proposal(proposal, items)


@router.post("/{proposal_id}/sign")
async def sign_proposal(
    proposal_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> dict[str, Any]:
    """Sign a proposal (Sent -> Signed), creates an order."""
    supabase = get_supabase()

    # Fetch proposal with items
    result = await supabase.table("proposals").select(
        "*, proposal_items (*, services:service_id (id, name, price, currency))"
    ).eq("id", proposal_id).eq("org_id", auth.org_id).is_("deleted_at", "null").execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    proposal = result.data[0]

    # Check if proposal can be signed (must be Sent)
    if proposal["status"] != 1:
        status_name = PROPOSAL_STATUS_MAP.get(proposal["status"], "Unknown")
        raise HTTPException(
            status_code=400,
            detail=f"Cannot sign proposal with status {status_name}",
        )

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    items = proposal.get("proposal_items") or []

    # Find or create client user
    client_id: str | None = None

    existing_user_result = await supabase.table("users").select("id").eq(
        "email", proposal["client_email"]
    ).eq("org_id", auth.org_id).execute()

    if existing_user_result.data:
        client_id = existing_user_result.data[0]["id"]
    else:
        # Get client role (dashboard_access = 0)
        role_result = await supabase.table("roles").select("id").eq(
            "dashboard_access", 0
        ).execute()

        if role_result.data:
            # Create new user
            new_user_result = await supabase.table("users").insert({
                "org_id": auth.org_id,
                "email": proposal["client_email"],
                "name_f": proposal["client_name_f"],
                "name_l": proposal["client_name_l"],
                "company": proposal.get("client_company"),
                "role_id": role_result.data[0]["id"],
                "status": 1,
                "balance": "0.00",
                "spent": "0.00",
                "custom_fields": {},
            }).select("id").execute()

            if new_user_result.data:
                client_id = new_user_result.data[0]["id"]

    # Get primary item details for order
    primary_item = items[0] if items else None

    # Handle Supabase join returning array for services
    primary_service = None
    if primary_item:
        services = primary_item.get("services")
        if isinstance(services, list) and len(services) > 0:
            primary_service = services[0]
        elif isinstance(services, dict):
            primary_service = services

    service_name = primary_service.get("name") if primary_service else "Proposal Order"
    currency = primary_service.get("currency") if primary_service else "USD"

    # Create order
    order_data = {
        "org_id": auth.org_id,
        "number": generate_order_number(),
        "user_id": client_id,
        "service_id": primary_item["service_id"] if primary_item else None,
        "service_name": service_name,
        "price": proposal["total"],
        "currency": currency,
        "quantity": 1,
        "status": 0,  # Unpaid
        "note": f"Created from proposal. {proposal.get('notes') or ''}".strip(),
        "form_data": {},
        "metadata": {
            "proposal_id": proposal["id"],
            "proposal_items": [
                {
                    "service_id": item["service_id"],
                    "service_name": (
                        item["services"][0]["name"]
                        if isinstance(item.get("services"), list) and item["services"]
                        else item.get("services", {}).get("name")
                        if isinstance(item.get("services"), dict)
                        else None
                    ),
                    "quantity": item["quantity"],
                    "price": str(item["price"]),
                }
                for item in items
            ],
        },
    }

    order_result = await supabase.table("orders").insert(order_data).select().execute()

    if not order_result.data:
        raise HTTPException(status_code=500, detail="Failed to create order")

    order = order_result.data[0]

    # Update proposal
    await supabase.table("proposals").update({
        "status": 2,
        "signed_at": now,
        "updated_at": now,
        "converted_order_id": order["id"],
    }).eq("id", proposal_id).execute()

    # Update local proposal dict
    proposal["status"] = 2
    proposal["signed_at"] = now
    proposal["updated_at"] = now
    proposal["converted_order_id"] = order["id"]

    # Build response
    proposal_response = serialize_proposal(proposal, items)

    order_response = {
        "id": order["id"],
        "number": order["number"],
        "user_id": order["user_id"],
        "service_id": order["service_id"],
        "service": order["service_name"],
        "price": str(order["price"]),
        "currency": order["currency"],
        "quantity": order["quantity"],
        "status": ORDER_STATUS_MAP.get(order["status"], "Unknown"),
        "status_id": order["status"],
        "note": order["note"],
        "created_at": order["created_at"],
    }

    return {
        "proposal": proposal_response.model_dump(),
        "order": order_response,
    }
