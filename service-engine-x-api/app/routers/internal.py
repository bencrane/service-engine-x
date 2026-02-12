"""Internal API router for admin panels."""

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.config import get_settings
from app.database import get_supabase

router = APIRouter(prefix="/internal", tags=["Internal"])
public_router = APIRouter(prefix="/public", tags=["Public"])


async def verify_internal_key(x_internal_key: str = Header(...)) -> None:
    """Verify internal API key."""
    settings = get_settings()
    if not settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Internal API not configured",
        )
    if x_internal_key != settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal API key",
        )


class InternalServiceCreate(BaseModel):
    """Request body for creating a service via internal API."""

    org_id: str = Field(..., description="Organization ID")
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    recurring: int = Field(0, ge=0, le=2)
    currency: str = Field("USD", min_length=1)
    price: float | None = None
    public: bool = True


class OrganizationResponse(BaseModel):
    """Organization response."""

    id: str
    name: str
    slug: str
    domain: str | None


class ServiceResponse(BaseModel):
    """Service response."""

    id: str
    org_id: str
    name: str
    description: str | None
    recurring: int
    price: float | None
    currency: str
    public: bool
    created_at: str
    updated_at: str


@router.get("/orgs", dependencies=[Depends(verify_internal_key)])
async def list_organizations() -> list[OrganizationResponse]:
    """List all organizations."""
    supabase = get_supabase()
    result = supabase.table("organizations").select("id, name, slug, domain").execute()
    return [OrganizationResponse(**org) for org in result.data]


@router.get("/orgs/{org_id}/services", dependencies=[Depends(verify_internal_key)])
async def list_services_for_org(
    org_id: str,
    limit: int = Query(50, ge=1, le=100),
) -> list[ServiceResponse]:
    """List services for a specific organization."""
    supabase = get_supabase()
    result = (
        supabase.table("services")
        .select("id, org_id, name, description, recurring, price, currency, public, created_at, updated_at")
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .limit(limit)
        .execute()
    )
    return [ServiceResponse(**svc) for svc in result.data]


@router.post("/services", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_internal_key)])
async def create_service(body: InternalServiceCreate) -> ServiceResponse:
    """Create a service for any organization."""
    supabase = get_supabase()

    # Verify org exists
    org_result = supabase.table("organizations").select("id").eq("id", body.org_id).execute()
    if not org_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    service_data = {
        "org_id": body.org_id,
        "name": body.name.strip(),
        "description": body.description,
        "recurring": body.recurring,
        "currency": body.currency.upper().strip(),
        "price": body.price,
        "public": body.public,
    }

    result = supabase.table("services").insert(service_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create service",
        )

    return ServiceResponse(**result.data[0])


# ============== Systems (for Everything Automation) ==============

class InternalSystemCreate(BaseModel):
    """Request body for creating a system via internal API."""

    org_id: str = Field(..., description="Organization ID")
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class SystemResponse(BaseModel):
    """System response."""

    id: str
    org_id: str
    name: str
    slug: str | None
    description: str | None
    created_at: str
    updated_at: str


@router.get("/orgs/{org_id}/systems", dependencies=[Depends(verify_internal_key)])
async def list_systems_for_org(
    org_id: str,
    limit: int = Query(50, ge=1, le=100),
) -> list[SystemResponse]:
    """List systems for a specific organization."""
    supabase = get_supabase()
    result = (
        supabase.table("systems")
        .select("id, org_id, name, slug, description, created_at, updated_at")
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .limit(limit)
        .execute()
    )
    return [SystemResponse(**sys) for sys in result.data]


@router.post("/systems", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_internal_key)])
async def create_system(body: InternalSystemCreate) -> SystemResponse:
    """Create a system for any organization."""
    supabase = get_supabase()

    # Verify org exists
    org_result = supabase.table("organizations").select("id").eq("id", body.org_id).execute()
    if not org_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    system_data = {
        "org_id": body.org_id,
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

    return SystemResponse(**result.data[0])


# ============== Public Endpoints (no auth) ==============

class PublicSystemResponse(BaseModel):
    """Public system response (limited fields)."""

    id: str
    name: str
    slug: str | None
    description: str | None


@public_router.get("/orgs/{org_slug}/systems")
async def public_list_systems(org_slug: str) -> list[PublicSystemResponse]:
    """List systems for an organization by slug (public, no auth)."""
    supabase = get_supabase()

    # Find org by slug
    org_result = supabase.table("organizations").select("id").eq("slug", org_slug).execute()
    if not org_result.data:
        raise HTTPException(status_code=404, detail="Organization not found")

    org_id = org_result.data[0]["id"]

    result = (
        supabase.table("systems")
        .select("id, name, slug, description")
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    return [PublicSystemResponse(**sys) for sys in result.data]
