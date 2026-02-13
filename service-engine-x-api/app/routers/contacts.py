"""Contacts API router."""

import secrets
import string
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse, Response

from app.auth import AuthContext, get_current_auth
from app.config import get_settings
from app.database import get_supabase
from app.models.contacts import (
    AccountBrief,
    ContactCreate,
    ContactListResponse,
    ContactResponse,
    ContactUpdate,
    GrantPortalAccessRequest,
    UserBrief,
)
from app.utils import build_pagination_response, is_valid_uuid

router = APIRouter(prefix="/api/contacts", tags=["Contacts"])


def serialize_account_brief(account: dict[str, Any] | None) -> AccountBrief | None:
    """Serialize account to brief model."""
    if not account:
        return None
    return AccountBrief(
        id=account["id"],
        name=account["name"],
        lifecycle=account.get("lifecycle", "lead"),
    )


def serialize_user_brief(user: dict[str, Any] | None) -> UserBrief | None:
    """Serialize user to brief model."""
    if not user:
        return None
    return UserBrief(
        id=user["id"],
        email=user["email"],
    )


def serialize_contact(
    contact: dict[str, Any],
    account: dict[str, Any] | None = None,
    user: dict[str, Any] | None = None,
) -> ContactResponse:
    """Serialize contact data to response model."""
    return ContactResponse(
        id=contact["id"],
        org_id=contact["org_id"],
        account_id=contact.get("account_id"),
        account=serialize_account_brief(account),
        name=f"{contact.get('name_f', '')} {contact.get('name_l', '')}".strip(),
        name_f=contact.get("name_f", ""),
        name_l=contact.get("name_l", ""),
        email=contact.get("email", ""),
        phone=contact.get("phone"),
        title=contact.get("title"),
        user_id=contact.get("user_id"),
        user=serialize_user_brief(user),
        has_portal_access=contact.get("user_id") is not None,
        is_primary=contact.get("is_primary", False),
        is_billing=contact.get("is_billing", False),
        optin=contact.get("optin"),
        custom_fields=contact.get("custom_fields", {}),
        created_at=contact["created_at"],
        updated_at=contact["updated_at"],
    )


def serialize_contact_list(contact: dict[str, Any]) -> ContactListResponse:
    """Serialize contact for list response."""
    return ContactListResponse(
        id=contact["id"],
        org_id=contact["org_id"],
        account_id=contact.get("account_id"),
        name=f"{contact.get('name_f', '')} {contact.get('name_l', '')}".strip(),
        name_f=contact.get("name_f", ""),
        name_l=contact.get("name_l", ""),
        email=contact.get("email", ""),
        phone=contact.get("phone"),
        title=contact.get("title"),
        has_portal_access=contact.get("user_id") is not None,
        is_primary=contact.get("is_primary", False),
        is_billing=contact.get("is_billing", False),
        created_at=contact["created_at"],
        updated_at=contact["updated_at"],
    )


@router.get("")
async def list_contacts(
    request: Request,
    auth: AuthContext = Depends(get_current_auth),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    sort: str = Query("created_at:desc"),
    account_id: str | None = Query(None, description="Filter by account UUID"),
    has_portal_access: bool | None = Query(None, description="Filter by portal access"),
) -> dict[str, Any]:
    """List all contacts for the authenticated organization."""
    supabase = get_supabase()
    settings = get_settings()

    # Parse sort parameter
    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if sort_parts else "created_at"
    sort_dir = sort_parts[1] if len(sort_parts) > 1 else "desc"

    valid_sort_fields = ["id", "name_f", "name_l", "email", "created_at", "updated_at"]
    if sort_field not in valid_sort_fields:
        sort_field = "created_at"
    ascending = sort_dir == "asc"

    # Build query
    query = (
        supabase.table("contacts")
        .select("*", count="exact")
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
    )

    # Apply filters
    if account_id is not None:
        if not is_valid_uuid(account_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Invalid account_id format"},
            )
        query = query.eq("account_id", account_id)

    if has_portal_access is not None:
        if has_portal_access:
            query = query.not_.is_("user_id", "null")
        else:
            query = query.is_("user_id", "null")

    # Get total count
    query = query.order(sort_field, desc=not ascending)
    count_result = query.execute()
    total = count_result.count or 0

    # Apply pagination
    offset = (page - 1) * limit
    query = (
        supabase.table("contacts")
        .select("*")
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
    )
    if account_id is not None:
        query = query.eq("account_id", account_id)
    if has_portal_access is not None:
        if has_portal_access:
            query = query.not_.is_("user_id", "null")
        else:
            query = query.is_("user_id", "null")

    query = query.order(sort_field, desc=not ascending).range(offset, offset + limit - 1)
    result = query.execute()
    contacts = result.data or []

    # Serialize
    serialized = [serialize_contact_list(c).model_dump() for c in contacts]

    path = f"{settings.api_base_url}/api/contacts"
    return build_pagination_response(serialized, total, page, limit, path)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreate,
    auth: AuthContext = Depends(get_current_auth),
) -> ContactResponse:
    """Create a new contact."""
    supabase = get_supabase()

    # Validate account_id if provided
    account_data = None
    if body.account_id:
        if not is_valid_uuid(body.account_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"account_id": ["Invalid UUID format"]},
                },
            )
        account_result = (
            supabase.table("accounts")
            .select("id, name, lifecycle")
            .eq("id", body.account_id)
            .eq("org_id", auth.org_id)
            .is_("deleted_at", "null")
            .execute()
        )
        if not account_result.data:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"account_id": ["Account not found"]},
                },
            )
        account_data = account_result.data[0]

    # Check for duplicate email in org
    existing = (
        supabase.table("contacts")
        .select("id")
        .eq("org_id", auth.org_id)
        .eq("email", body.email.lower().strip())
        .is_("deleted_at", "null")
        .execute()
    )
    if existing.data and len(existing.data) > 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "The given data was invalid.",
                "errors": {"email": ["A contact with this email already exists."]},
            },
        )

    # If setting as primary, clear other primaries for the account
    if body.is_primary and body.account_id:
        supabase.table("contacts").update({"is_primary": False}).eq(
            "account_id", body.account_id
        ).eq("is_primary", True).execute()

    # Create contact
    now = datetime.now(timezone.utc).isoformat()
    contact_data = {
        "org_id": auth.org_id,
        "account_id": body.account_id,
        "name_f": body.name_f.strip(),
        "name_l": body.name_l.strip(),
        "email": body.email.lower().strip(),
        "phone": body.phone,
        "title": body.title,
        "is_primary": body.is_primary,
        "is_billing": body.is_billing,
        "optin": body.optin,
        "custom_fields": body.custom_fields or {},
        "created_at": now,
        "updated_at": now,
    }

    result = supabase.table("contacts").insert(contact_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create contact",
        )

    return serialize_contact(result.data[0], account=account_data)


@router.get("/{contact_id}")
async def retrieve_contact(
    contact_id: str,
    auth: AuthContext = Depends(get_current_auth),
) -> ContactResponse:
    """Retrieve a contact by ID."""
    if not is_valid_uuid(contact_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get contact with account
    result = (
        supabase.table("contacts")
        .select("*, account:accounts(id, name, lifecycle)")
        .eq("id", contact_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    contact = result.data[0]

    # Handle account join result
    account_data = contact.get("account")
    if isinstance(account_data, list):
        account_data = account_data[0] if account_data else None

    # Get user if linked
    user_data = None
    if contact.get("user_id"):
        user_result = (
            supabase.table("users")
            .select("id, email")
            .eq("id", contact["user_id"])
            .execute()
        )
        if user_result.data:
            user_data = user_result.data[0]

    return serialize_contact(contact, account=account_data, user=user_data)


@router.put("/{contact_id}")
async def update_contact(
    contact_id: str,
    body: ContactUpdate,
    auth: AuthContext = Depends(get_current_auth),
) -> ContactResponse:
    """Update a contact."""
    if not is_valid_uuid(contact_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get existing contact
    existing_result = (
        supabase.table("contacts")
        .select("*")
        .eq("id", contact_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not existing_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    existing = existing_result.data[0]

    # Validate account_id if changing
    if body.account_id is not None and body.account_id != existing.get("account_id"):
        if body.account_id:
            if not is_valid_uuid(body.account_id):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "message": "The given data was invalid.",
                        "errors": {"account_id": ["Invalid UUID format"]},
                    },
                )
            account_check = (
                supabase.table("accounts")
                .select("id")
                .eq("id", body.account_id)
                .eq("org_id", auth.org_id)
                .is_("deleted_at", "null")
                .execute()
            )
            if not account_check.data:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "message": "The given data was invalid.",
                        "errors": {"account_id": ["Account not found"]},
                    },
                )

    # Check for duplicate email if changing
    if body.email is not None:
        email_check = (
            supabase.table("contacts")
            .select("id")
            .eq("org_id", auth.org_id)
            .eq("email", body.email.lower().strip())
            .neq("id", contact_id)
            .is_("deleted_at", "null")
            .execute()
        )
        if email_check.data and len(email_check.data) > 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"email": ["A contact with this email already exists."]},
                },
            )

    # If setting as primary, clear other primaries for the account
    account_id = body.account_id if body.account_id is not None else existing.get("account_id")
    if body.is_primary and account_id:
        supabase.table("contacts").update({"is_primary": False}).eq(
            "account_id", account_id
        ).eq("is_primary", True).neq("id", contact_id).execute()

    # Build update payload
    now = datetime.now(timezone.utc).isoformat()
    update_payload: dict[str, Any] = {"updated_at": now}

    if body.account_id is not None:
        update_payload["account_id"] = body.account_id if body.account_id else None
    if body.name_f is not None:
        update_payload["name_f"] = body.name_f.strip()
    if body.name_l is not None:
        update_payload["name_l"] = body.name_l.strip()
    if body.email is not None:
        update_payload["email"] = body.email.lower().strip()
    if body.phone is not None:
        update_payload["phone"] = body.phone
    if body.title is not None:
        update_payload["title"] = body.title
    if body.is_primary is not None:
        update_payload["is_primary"] = body.is_primary
    if body.is_billing is not None:
        update_payload["is_billing"] = body.is_billing
    if body.optin is not None:
        update_payload["optin"] = body.optin
    if body.custom_fields is not None:
        update_payload["custom_fields"] = body.custom_fields

    # Update contact
    result = (
        supabase.table("contacts")
        .update(update_payload)
        .eq("id", contact_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update contact",
        )

    updated = result.data[0]

    # Fetch account for response
    account_data = None
    if updated.get("account_id"):
        account_result = (
            supabase.table("accounts")
            .select("id, name, lifecycle")
            .eq("id", updated["account_id"])
            .execute()
        )
        if account_result.data:
            account_data = account_result.data[0]

    # Fetch user for response
    user_data = None
    if updated.get("user_id"):
        user_result = (
            supabase.table("users")
            .select("id, email")
            .eq("id", updated["user_id"])
            .execute()
        )
        if user_result.data:
            user_data = user_result.data[0]

    return serialize_contact(updated, account=account_data, user=user_data)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: str,
    auth: AuthContext = Depends(get_current_auth),
) -> Response:
    """Soft delete a contact."""
    if not is_valid_uuid(contact_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify contact exists
    existing = (
        supabase.table("contacts")
        .select("id")
        .eq("id", contact_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Soft delete
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("contacts").update(
        {"deleted_at": now, "updated_at": now}
    ).eq("id", contact_id).execute()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# =============================================================================
# PORTAL ACCESS
# =============================================================================

def generate_temp_password() -> str:
    """Generate a temporary password for new portal users."""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(12))


@router.post("/{contact_id}/grant-portal-access")
async def grant_portal_access(
    contact_id: str,
    body: GrantPortalAccessRequest,
    auth: AuthContext = Depends(get_current_auth),
) -> dict[str, Any]:
    """
    Grant portal access to a contact.

    Creates a user account linked to this contact, allowing them to log in
    to the client portal.
    """
    if not is_valid_uuid(contact_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get contact
    contact_result = (
        supabase.table("contacts")
        .select("*")
        .eq("id", contact_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not contact_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    contact = contact_result.data[0]

    # Check if already has portal access
    if contact.get("user_id"):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Contact already has portal access",
                "user_id": contact["user_id"],
            },
        )

    # Check if email already exists as a user
    existing_user = (
        supabase.table("users")
        .select("id")
        .eq("email", contact["email"])
        .eq("org_id", auth.org_id)
        .execute()
    )

    if existing_user.data and len(existing_user.data) > 0:
        # Link to existing user
        user_id = existing_user.data[0]["id"]
        supabase.table("contacts").update({"user_id": user_id}).eq(
            "id", contact_id
        ).execute()

        return {
            "success": True,
            "message": "Contact linked to existing user",
            "user_id": user_id,
            "is_new_user": False,
        }

    # Get client role (dashboard_access = 0)
    role_result = (
        supabase.table("roles")
        .select("id")
        .eq("dashboard_access", 0)
        .execute()
    )

    if not role_result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Client role not configured",
        )

    client_role_id = role_result.data[0]["id"]

    # Create user
    now = datetime.now(timezone.utc).isoformat()
    temp_password = generate_temp_password()

    user_data = {
        "org_id": auth.org_id,
        "email": contact["email"],
        "name_f": contact["name_f"],
        "name_l": contact["name_l"],
        "phone": contact.get("phone"),
        "role_id": client_role_id,
        "status": 1,
        "balance": "0.00",
        "spent": "0.00",
        "custom_fields": {},
        "password_hash": "pending_reset",  # Placeholder - user will set password on first login
        "created_at": now,
    }

    user_result = supabase.table("users").insert(user_data).execute()

    if not user_result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )

    user_id = user_result.data[0]["id"]

    # Link contact to user
    supabase.table("contacts").update(
        {"user_id": user_id, "updated_at": now}
    ).eq("id", contact_id).execute()

    # TODO: Send welcome email if body.send_welcome_email is True

    return {
        "success": True,
        "message": "Portal access granted",
        "user_id": user_id,
        "is_new_user": True,
        "email": contact["email"],
    }
