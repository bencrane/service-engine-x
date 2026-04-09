"""Organization bank details API router."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.auth import AuthContext, get_current_auth
from app.database import get_supabase
from app.models.bank_details import (
    BankDetailsCreate,
    BankDetailsUpdate,
    BankDetailsResponse,
)

router = APIRouter(prefix="/api/bank-details", tags=["Bank Details"])

TABLE = "organization_bank_details"


def serialize_bank_details(row: dict[str, Any]) -> BankDetailsResponse:
    """Serialize a DB row to the response model."""
    return BankDetailsResponse(
        id=row["id"],
        org_id=row["org_id"],
        account_name=row["account_name"],
        account_number=row.get("account_number"),
        routing_number=row.get("routing_number"),
        bank_name=row.get("bank_name"),
        bank_address_line1=row.get("bank_address_line1"),
        bank_address_line2=row.get("bank_address_line2"),
        bank_city=row.get("bank_city"),
        bank_state=row.get("bank_state"),
        bank_postal_code=row.get("bank_postal_code"),
        bank_country=row.get("bank_country"),
        swift_code=row.get("swift_code"),
        iban=row.get("iban"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.get("")
async def get_bank_details(
    auth: AuthContext = Depends(get_current_auth),
) -> BankDetailsResponse | None:
    """Get bank details for the authenticated organization."""
    supabase = get_supabase()

    result = (
        supabase.table(TABLE)
        .select("*")
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not result.data:
        return None

    return serialize_bank_details(result.data[0])


@router.put("", status_code=status.HTTP_200_OK)
async def upsert_bank_details(
    body: BankDetailsCreate,
    auth: AuthContext = Depends(get_current_auth),
) -> BankDetailsResponse:
    """Create or replace bank details for the authenticated organization."""
    supabase = get_supabase()
    now = datetime.now(timezone.utc).isoformat()

    # Check if bank details already exist for this org
    existing = (
        supabase.table(TABLE)
        .select("id")
        .eq("org_id", auth.org_id)
        .execute()
    )

    payload = {
        "account_name": body.account_name.strip(),
        "account_number": body.account_number,
        "routing_number": body.routing_number,
        "bank_name": body.bank_name,
        "bank_address_line1": body.bank_address_line1,
        "bank_address_line2": body.bank_address_line2,
        "bank_city": body.bank_city,
        "bank_state": body.bank_state,
        "bank_postal_code": body.bank_postal_code,
        "bank_country": body.bank_country,
        "swift_code": body.swift_code,
        "iban": body.iban,
        "updated_at": now,
    }

    if existing.data:
        # Update existing record
        result = (
            supabase.table(TABLE)
            .update(payload)
            .eq("org_id", auth.org_id)
            .execute()
        )
    else:
        # Insert new record
        payload["org_id"] = auth.org_id
        payload["created_at"] = now
        result = supabase.table(TABLE).insert(payload).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save bank details",
        )

    return serialize_bank_details(result.data[0])


@router.patch("")
async def update_bank_details(
    body: BankDetailsUpdate,
    auth: AuthContext = Depends(get_current_auth),
) -> BankDetailsResponse:
    """Partially update bank details for the authenticated organization."""
    supabase = get_supabase()

    existing = (
        supabase.table(TABLE)
        .select("*")
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No bank details found. Use PUT to create.",
        )

    now = datetime.now(timezone.utc).isoformat()
    update_payload: dict[str, Any] = {"updated_at": now}

    for field, value in body.model_dump(exclude_unset=True).items():
        if field == "account_name" and value is not None:
            update_payload[field] = value.strip()
        else:
            update_payload[field] = value

    result = (
        supabase.table(TABLE)
        .update(update_payload)
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update bank details",
        )

    return serialize_bank_details(result.data[0])


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bank_details(
    auth: AuthContext = Depends(get_current_auth),
) -> Response:
    """Delete bank details for the authenticated organization."""
    supabase = get_supabase()

    existing = (
        supabase.table(TABLE)
        .select("id")
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found",
        )

    supabase.table(TABLE).delete().eq("org_id", auth.org_id).execute()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
