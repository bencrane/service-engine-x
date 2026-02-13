"""Accounts API router."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse, Response

from app.auth import AuthContext, get_current_auth
from app.config import get_settings
from app.database import get_supabase
from app.models.accounts import (
    VALID_LIFECYCLES,
    ACCOUNT_LIFECYCLE_LEAD,
    AccountCreate,
    AccountListResponse,
    AccountResponse,
    AccountUpdate,
    AccountWithContacts,
    AddressBrief,
    ContactBrief,
)
from app.utils import build_pagination_response, format_currency, is_valid_uuid

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


def serialize_address(address: dict[str, Any] | None) -> AddressBrief | None:
    """Serialize address to brief model."""
    if not address:
        return None
    return AddressBrief(
        line_1=address.get("line_1"),
        line_2=address.get("line_2"),
        city=address.get("city"),
        state=address.get("state"),
        country=address.get("country"),
        postcode=address.get("postcode"),
    )


def serialize_account(
    account: dict[str, Any],
    address: dict[str, Any] | None = None,
) -> AccountResponse:
    """Serialize account data to response model."""
    return AccountResponse(
        id=account["id"],
        org_id=account["org_id"],
        name=account["name"],
        domain=account.get("domain"),
        lifecycle=account.get("lifecycle", ACCOUNT_LIFECYCLE_LEAD),
        balance=format_currency(account.get("balance")),
        total_spent=format_currency(account.get("total_spent")),
        stripe_customer_id=account.get("stripe_customer_id"),
        tax_id=account.get("tax_id"),
        aff_id=account.get("aff_id"),
        aff_link=account.get("aff_link"),
        source=account.get("source"),
        ga_cid=account.get("ga_cid"),
        custom_fields=account.get("custom_fields", {}),
        note=account.get("note"),
        billing_address=serialize_address(address),
        created_at=account["created_at"],
        updated_at=account["updated_at"],
    )


def serialize_account_list(account: dict[str, Any]) -> AccountListResponse:
    """Serialize account for list response."""
    return AccountListResponse(
        id=account["id"],
        org_id=account["org_id"],
        name=account["name"],
        domain=account.get("domain"),
        lifecycle=account.get("lifecycle", ACCOUNT_LIFECYCLE_LEAD),
        balance=format_currency(account.get("balance")),
        total_spent=format_currency(account.get("total_spent")),
        created_at=account["created_at"],
        updated_at=account["updated_at"],
    )


def serialize_contact_brief(contact: dict[str, Any]) -> ContactBrief:
    """Serialize contact to brief model."""
    return ContactBrief(
        id=contact["id"],
        name=f"{contact.get('name_f', '')} {contact.get('name_l', '')}".strip(),
        email=contact.get("email", ""),
        is_primary=contact.get("is_primary", False),
        is_billing=contact.get("is_billing", False),
    )


@router.get("")
async def list_accounts(
    request: Request,
    auth: AuthContext = Depends(get_current_auth),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    sort: str = Query("created_at:desc"),
    lifecycle: str | None = Query(None, description="Filter by lifecycle status"),
) -> dict[str, Any]:
    """List all accounts for the authenticated organization."""
    supabase = get_supabase()
    settings = get_settings()

    # Parse sort parameter
    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if sort_parts else "created_at"
    sort_dir = sort_parts[1] if len(sort_parts) > 1 else "desc"

    valid_sort_fields = ["id", "name", "lifecycle", "balance", "total_spent", "created_at", "updated_at"]
    if sort_field not in valid_sort_fields:
        sort_field = "created_at"
    ascending = sort_dir == "asc"

    # Build query
    query = (
        supabase.table("accounts")
        .select("*", count="exact")
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
    )

    # Apply filters
    if lifecycle is not None:
        if lifecycle not in VALID_LIFECYCLES:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": f"Invalid lifecycle. Must be one of: {', '.join(VALID_LIFECYCLES)}"},
            )
        query = query.eq("lifecycle", lifecycle)

    # Get total count
    query = query.order(sort_field, desc=not ascending)
    count_result = query.execute()
    total = count_result.count or 0

    # Apply pagination
    offset = (page - 1) * limit
    query = (
        supabase.table("accounts")
        .select("*")
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
    )
    if lifecycle is not None:
        query = query.eq("lifecycle", lifecycle)

    query = query.order(sort_field, desc=not ascending).range(offset, offset + limit - 1)
    result = query.execute()
    accounts = result.data or []

    # Serialize
    serialized = [serialize_account_list(a).model_dump() for a in accounts]

    path = f"{settings.api_base_url}/api/accounts"
    return build_pagination_response(serialized, total, page, limit, path)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_account(
    body: AccountCreate,
    auth: AuthContext = Depends(get_current_auth),
) -> AccountResponse:
    """Create a new account."""
    supabase = get_supabase()

    # Validate lifecycle
    if body.lifecycle not in VALID_LIFECYCLES:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "The given data was invalid.",
                "errors": {"lifecycle": [f"Must be one of: {', '.join(VALID_LIFECYCLES)}"]},
            },
        )

    # Check for duplicate domain if provided
    if body.domain:
        existing = (
            supabase.table("accounts")
            .select("id")
            .eq("org_id", auth.org_id)
            .eq("domain", body.domain.lower().strip())
            .is_("deleted_at", "null")
            .execute()
        )
        if existing.data and len(existing.data) > 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"domain": ["An account with this domain already exists."]},
                },
            )

    # Create account
    now = datetime.now(timezone.utc).isoformat()
    account_data = {
        "org_id": auth.org_id,
        "name": body.name.strip(),
        "domain": body.domain.lower().strip() if body.domain else None,
        "lifecycle": body.lifecycle,
        "tax_id": body.tax_id,
        "source": body.source,
        "ga_cid": body.ga_cid,
        "note": body.note,
        "custom_fields": body.custom_fields or {},
        "balance": 0.00,
        "total_spent": 0.00,
        "created_at": now,
        "updated_at": now,
    }

    result = supabase.table("accounts").insert(account_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account",
        )

    return serialize_account(result.data[0])


@router.get("/{account_id}")
async def retrieve_account(
    account_id: str,
    auth: AuthContext = Depends(get_current_auth),
) -> AccountWithContacts:
    """Retrieve an account with its contacts."""
    if not is_valid_uuid(account_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get account with address
    result = (
        supabase.table("accounts")
        .select("*, billing_address:addresses(*)")
        .eq("id", account_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    account = result.data[0]

    # Handle address join result
    addr_data = account.get("billing_address")
    if isinstance(addr_data, list):
        addr_data = addr_data[0] if addr_data else None

    # Get contacts for this account
    contacts_result = (
        supabase.table("contacts")
        .select("id, name_f, name_l, email, is_primary, is_billing")
        .eq("account_id", account_id)
        .is_("deleted_at", "null")
        .order("is_primary", desc=True)
        .execute()
    )
    contacts = contacts_result.data or []

    # Build response
    base_response = serialize_account(account, addr_data)
    return AccountWithContacts(
        **base_response.model_dump(),
        contacts=[serialize_contact_brief(c) for c in contacts],
    )


@router.put("/{account_id}")
async def update_account(
    account_id: str,
    body: AccountUpdate,
    auth: AuthContext = Depends(get_current_auth),
) -> AccountResponse:
    """Update an account."""
    if not is_valid_uuid(account_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get existing account
    existing_result = (
        supabase.table("accounts")
        .select("*")
        .eq("id", account_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not existing_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Validate lifecycle if provided
    if body.lifecycle is not None and body.lifecycle not in VALID_LIFECYCLES:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "The given data was invalid.",
                "errors": {"lifecycle": [f"Must be one of: {', '.join(VALID_LIFECYCLES)}"]},
            },
        )

    # Check for duplicate domain if changing
    if body.domain is not None:
        domain_check = (
            supabase.table("accounts")
            .select("id")
            .eq("org_id", auth.org_id)
            .eq("domain", body.domain.lower().strip())
            .neq("id", account_id)
            .is_("deleted_at", "null")
            .execute()
        )
        if domain_check.data and len(domain_check.data) > 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"domain": ["An account with this domain already exists."]},
                },
            )

    # Build update payload
    now = datetime.now(timezone.utc).isoformat()
    update_payload: dict[str, Any] = {"updated_at": now}

    if body.name is not None:
        update_payload["name"] = body.name.strip()
    if body.domain is not None:
        update_payload["domain"] = body.domain.lower().strip() if body.domain else None
    if body.lifecycle is not None:
        update_payload["lifecycle"] = body.lifecycle
    if body.balance is not None:
        update_payload["balance"] = body.balance
    if body.total_spent is not None:
        update_payload["total_spent"] = body.total_spent
    if body.stripe_customer_id is not None:
        update_payload["stripe_customer_id"] = body.stripe_customer_id
    if body.tax_id is not None:
        update_payload["tax_id"] = body.tax_id
    if body.aff_id is not None:
        update_payload["aff_id"] = body.aff_id
    if body.aff_link is not None:
        update_payload["aff_link"] = body.aff_link
    if body.source is not None:
        update_payload["source"] = body.source
    if body.ga_cid is not None:
        update_payload["ga_cid"] = body.ga_cid
    if body.note is not None:
        update_payload["note"] = body.note
    if body.custom_fields is not None:
        update_payload["custom_fields"] = body.custom_fields

    # Update account
    result = (
        supabase.table("accounts")
        .update(update_payload)
        .eq("id", account_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update account",
        )

    # Fetch address for response
    addr_data = None
    if result.data[0].get("billing_address_id"):
        addr_result = (
            supabase.table("addresses")
            .select("*")
            .eq("id", result.data[0]["billing_address_id"])
            .execute()
        )
        if addr_result.data:
            addr_data = addr_result.data[0]

    return serialize_account(result.data[0], addr_data)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: str,
    auth: AuthContext = Depends(get_current_auth),
) -> Response:
    """Soft delete an account."""
    if not is_valid_uuid(account_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify account exists
    existing = (
        supabase.table("accounts")
        .select("id")
        .eq("id", account_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Check for active engagements
    engagements = (
        supabase.table("engagements")
        .select("id")
        .eq("account_id", account_id)
        .neq("status", 3)  # Not closed
        .limit(1)
        .execute()
    )
    if engagements.data and len(engagements.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete account with active engagements",
        )

    # Soft delete
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("accounts").update(
        {"deleted_at": now, "updated_at": now}
    ).eq("id", account_id).execute()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# =============================================================================
# NESTED ENDPOINTS
# =============================================================================

@router.get("/{account_id}/contacts")
async def list_account_contacts(
    account_id: str,
    auth: AuthContext = Depends(get_current_auth),
) -> list[dict[str, Any]]:
    """List all contacts for an account."""
    if not is_valid_uuid(account_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify account exists
    account = (
        supabase.table("accounts")
        .select("id")
        .eq("id", account_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not account.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Get contacts
    contacts_result = (
        supabase.table("contacts")
        .select("*")
        .eq("account_id", account_id)
        .is_("deleted_at", "null")
        .order("is_primary", desc=True)
        .order("created_at", desc=False)
        .execute()
    )

    return [
        {
            "id": c["id"],
            "name": f"{c.get('name_f', '')} {c.get('name_l', '')}".strip(),
            "name_f": c.get("name_f", ""),
            "name_l": c.get("name_l", ""),
            "email": c.get("email", ""),
            "phone": c.get("phone"),
            "title": c.get("title"),
            "is_primary": c.get("is_primary", False),
            "is_billing": c.get("is_billing", False),
            "has_portal_access": c.get("user_id") is not None,
            "created_at": c["created_at"],
        }
        for c in (contacts_result.data or [])
    ]


@router.get("/{account_id}/engagements")
async def list_account_engagements(
    account_id: str,
    auth: AuthContext = Depends(get_current_auth),
) -> list[dict[str, Any]]:
    """List all engagements for an account."""
    if not is_valid_uuid(account_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify account exists
    account = (
        supabase.table("accounts")
        .select("id")
        .eq("id", account_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not account.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Get engagements - check both account_id and client_id for transition period
    engagements_result = (
        supabase.table("engagements")
        .select("*")
        .eq("account_id", account_id)
        .order("created_at", desc=True)
        .execute()
    )

    status_map = {1: "Active", 2: "Paused", 3: "Closed"}

    return [
        {
            "id": e["id"],
            "name": e.get("name"),
            "status": status_map.get(e.get("status", 1), "Unknown"),
            "status_id": e.get("status", 1),
            "created_at": e["created_at"],
            "updated_at": e["updated_at"],
            "closed_at": e.get("closed_at"),
        }
        for e in (engagements_result.data or [])
    ]
