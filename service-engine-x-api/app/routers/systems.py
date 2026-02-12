"""Systems API router."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.auth import AuthContext, get_current_org
from app.database import get_supabase
from app.models.systems import (
    SystemCreate,
    SystemUpdate,
    SystemResponse,
    SystemAccessCreate,
    SystemAccessUpdate,
    SystemAccessResponse,
)
from app.utils import is_valid_uuid

router = APIRouter(prefix="/api/systems", tags=["Systems"])


def serialize_system(system: dict[str, Any]) -> SystemResponse:
    """Serialize system data to response model."""
    return SystemResponse(
        id=system["id"],
        org_id=system["org_id"],
        name=system["name"],
        slug=system.get("slug"),
        description=system.get("description"),
        created_at=system["created_at"],
        updated_at=system["updated_at"],
    )


def serialize_system_access(access: dict[str, Any], system: dict[str, Any] | None = None) -> SystemAccessResponse:
    """Serialize system access data to response model."""
    return SystemAccessResponse(
        id=access["id"],
        org_id=access["org_id"],
        system_id=access["system_id"],
        client_id=access["client_id"],
        engagement_id=access.get("engagement_id"),
        status=access["status"],
        granted_at=access["granted_at"],
        expires_at=access.get("expires_at"),
        created_at=access["created_at"],
        updated_at=access["updated_at"],
        system=serialize_system(system) if system else None,
    )


# ============== Systems CRUD ==============

@router.get("")
async def list_systems(
    auth: AuthContext = Depends(get_current_org),
    limit: int = Query(50, ge=1, le=100),
    page: int = Query(1, ge=1),
) -> dict[str, Any]:
    """List all systems for the authenticated organization."""
    supabase = get_supabase()
    offset = (page - 1) * limit

    # Get count
    count_result = (
        supabase.table("systems")
        .select("id", count="exact")
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )
    total = count_result.count or 0

    # Get data
    result = (
        supabase.table("systems")
        .select("*")
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .order("sort_order", desc=False)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    return {
        "data": [serialize_system(s) for s in result.data],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1,
        },
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_system(
    body: SystemCreate,
    auth: AuthContext = Depends(get_current_org),
) -> SystemResponse:
    """Create a new system."""
    supabase = get_supabase()

    system_data = {
        "org_id": auth.org_id,
        "name": body.name.strip(),
        "slug": body.slug.strip().lower(),
        "description": body.description,
    }

    result = supabase.table("systems").insert(system_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create system",
        )

    return serialize_system(result.data[0])


@router.get("/{system_id}")
async def get_system(
    system_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> SystemResponse:
    """Get a specific system."""
    if not is_valid_uuid(system_id):
        raise HTTPException(status_code=404, detail="System not found")

    supabase = get_supabase()
    result = (
        supabase.table("systems")
        .select("*")
        .eq("id", system_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="System not found")

    return serialize_system(result.data[0])


@router.patch("/{system_id}")
async def update_system(
    system_id: str,
    body: SystemUpdate,
    auth: AuthContext = Depends(get_current_org),
) -> SystemResponse:
    """Update a system."""
    if not is_valid_uuid(system_id):
        raise HTTPException(status_code=404, detail="System not found")

    supabase = get_supabase()

    # Verify exists
    existing = (
        supabase.table("systems")
        .select("id")
        .eq("id", system_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="System not found")

    # Build update
    update_data: dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if body.name is not None:
        update_data["name"] = body.name.strip()
    if body.slug is not None:
        update_data["slug"] = body.slug.strip().lower()
    if body.description is not None:
        update_data["description"] = body.description

    result = (
        supabase.table("systems")
        .update(update_data)
        .eq("id", system_id)
        .eq("org_id", auth.org_id)
        .execute()
    )

    return serialize_system(result.data[0])


@router.delete("/{system_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system(
    system_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> None:
    """Soft delete a system."""
    if not is_valid_uuid(system_id):
        raise HTTPException(status_code=404, detail="System not found")

    supabase = get_supabase()

    result = (
        supabase.table("systems")
        .update({"deleted_at": datetime.now(timezone.utc).isoformat()})
        .eq("id", system_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="System not found")


# ============== System Access CRUD ==============

@router.get("/access/list")
async def list_system_access(
    auth: AuthContext = Depends(get_current_org),
    client_id: str | None = Query(None),
    system_id: str | None = Query(None),
    status_filter: int | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
) -> dict[str, Any]:
    """List system access records."""
    supabase = get_supabase()

    query = (
        supabase.table("system_access")
        .select("*, systems(*)")
        .eq("org_id", auth.org_id)
    )

    if client_id:
        query = query.eq("client_id", client_id)
    if system_id:
        query = query.eq("system_id", system_id)
    if status_filter:
        query = query.eq("status", status_filter)

    result = query.limit(limit).execute()

    return {
        "data": [
            serialize_system_access(a, a.get("systems"))
            for a in result.data
        ],
    }


@router.post("/access", status_code=status.HTTP_201_CREATED)
async def grant_system_access(
    body: SystemAccessCreate,
    auth: AuthContext = Depends(get_current_org),
) -> SystemAccessResponse:
    """Grant a client access to a system."""
    supabase = get_supabase()

    # Verify system exists and belongs to org
    system_result = (
        supabase.table("systems")
        .select("*")
        .eq("id", body.system_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )
    if not system_result.data:
        raise HTTPException(status_code=404, detail="System not found")

    # Verify client exists
    client_result = (
        supabase.table("users")
        .select("id")
        .eq("id", body.client_id)
        .execute()
    )
    if not client_result.data:
        raise HTTPException(status_code=404, detail="Client not found")

    access_data = {
        "org_id": auth.org_id,
        "system_id": body.system_id,
        "client_id": body.client_id,
        "engagement_id": body.engagement_id,
        "status": 1,  # active
        "granted_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": body.expires_at,
    }

    result = supabase.table("system_access").insert(access_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grant access",
        )

    return serialize_system_access(result.data[0], system_result.data[0])


@router.patch("/access/{access_id}")
async def update_system_access(
    access_id: str,
    body: SystemAccessUpdate,
    auth: AuthContext = Depends(get_current_org),
) -> SystemAccessResponse:
    """Update system access (status, expiry)."""
    if not is_valid_uuid(access_id):
        raise HTTPException(status_code=404, detail="Access record not found")

    supabase = get_supabase()

    # Verify exists
    existing = (
        supabase.table("system_access")
        .select("*, systems(*)")
        .eq("id", access_id)
        .eq("org_id", auth.org_id)
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Access record not found")

    update_data: dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if body.status is not None:
        update_data["status"] = body.status
    if body.expires_at is not None:
        update_data["expires_at"] = body.expires_at

    result = (
        supabase.table("system_access")
        .update(update_data)
        .eq("id", access_id)
        .eq("org_id", auth.org_id)
        .execute()
    )

    return serialize_system_access(result.data[0], existing.data[0].get("systems"))


@router.delete("/access/{access_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_system_access(
    access_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> None:
    """Revoke system access (sets status to revoked)."""
    if not is_valid_uuid(access_id):
        raise HTTPException(status_code=404, detail="Access record not found")

    supabase = get_supabase()

    result = (
        supabase.table("system_access")
        .update({
            "status": 3,  # revoked
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", access_id)
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Access record not found")
