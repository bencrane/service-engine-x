"""Internal API router for admin panels."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.config import get_settings
from app.database import get_supabase

# Signing URL base (where clients view/sign proposals)
SIGNING_URL_BASE = "https://revenueactivation.com/p"
from app.models.proposals import (
    AdminCreateProposalRequest,
    ProposalItemResponse,
    ProposalResponse,
    PROPOSAL_STATUS_MAP,
)
from app.services.resend_service import send_proposal_email

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


# ============== Proposals ==============


def _serialize_proposal_item(item: dict) -> ProposalItemResponse:
    """Serialize a proposal item."""
    return ProposalItemResponse(
        id=item["id"],
        name=item["name"],
        description=item.get("description"),
        price=f"{float(item.get('price', 0)):.2f}",
        service_id=item.get("service_id"),
        created_at=item["created_at"],
    )


def _serialize_proposal(proposal: dict, items: list[dict]) -> ProposalResponse:
    """Serialize a proposal with items."""
    status_id = proposal.get("status", 0)
    proposal_id = proposal["id"]
    return ProposalResponse(
        id=proposal_id,
        account_name=proposal.get("client_company"),
        contact_email=proposal["client_email"],
        contact_name=f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip(),
        contact_name_f=proposal.get("client_name_f", ""),
        contact_name_l=proposal.get("client_name_l", ""),
        status=PROPOSAL_STATUS_MAP.get(status_id, "Unknown"),
        status_id=status_id,
        total=f"{float(proposal.get('total', 0)):.2f}",
        notes=proposal.get("notes"),
        created_at=proposal["created_at"],
        updated_at=proposal["updated_at"],
        sent_at=proposal.get("sent_at"),
        signed_at=proposal.get("signed_at"),
        pdf_url=proposal.get("pdf_url"),
        signing_url=f"{SIGNING_URL_BASE}/{proposal_id}",
        converted_order_id=proposal.get("converted_order_id"),
        converted_engagement_id=proposal.get("converted_engagement_id"),
        items=[_serialize_proposal_item(item) for item in items],
    )


@router.post("/proposals", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_internal_key)])
async def create_proposal_internal(body: AdminCreateProposalRequest) -> ProposalResponse:
    """Create a proposal for any organization (internal admin use)."""
    supabase = get_supabase()

    # Get org details for email
    org_result = supabase.table("organizations").select("id, name, domain, notification_email").eq("id", body.org_id).execute()
    if not org_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    org = org_result.data[0]
    org_name = org.get("name", "Service Engine X")
    # Use notification_email if set, otherwise construct from domain
    from_email = org.get("notification_email") or f"proposals@{org.get('domain', 'serviceengine.xyz')}"

    # Validate service_ids if provided
    service_ids = [item.service_id for item in body.items if item.service_id]
    if service_ids:
        services_result = (
            supabase.table("services")
            .select("id")
            .eq("org_id", body.org_id)
            .is_("deleted_at", "null")
            .in_("id", service_ids)
            .execute()
        )
        found_service_ids = {s["id"] for s in (services_result.data or [])}
        missing_services = [sid for sid in service_ids if sid not in found_service_ids]
        if missing_services:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Service with ID {missing_services[0]} does not exist.",
            )

    # Calculate total
    total = sum(item.price for item in body.items)
    now = datetime.now(timezone.utc).isoformat()

    # Create proposal as Sent (ready for client to view/sign)
    proposal_data = {
        "org_id": body.org_id,
        "client_email": body.contact_email.lower().strip(),
        "client_name_f": body.contact_name_f.strip(),
        "client_name_l": body.contact_name_l.strip(),
        "client_company": body.account_name,
        "status": 1,  # Sent
        "sent_at": now,
        "total": total,
        "notes": body.notes,
    }

    proposal_result = supabase.table("proposals").insert(proposal_data).select().execute()
    if not proposal_result.data:
        raise HTTPException(status_code=500, detail="Failed to create proposal")

    proposal = proposal_result.data[0]

    # Create proposal items
    item_rows = [
        {
            "proposal_id": proposal["id"],
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "service_id": item.service_id,
        }
        for item in body.items
    ]

    items_result = supabase.table("proposal_items").insert(item_rows).select("*").execute()
    if not items_result.data:
        supabase.table("proposals").delete().eq("id", proposal["id"]).execute()
        raise HTTPException(status_code=500, detail="Failed to create proposal items")

    # Send proposal email to client
    proposal_id = proposal["id"]
    signing_url = f"{SIGNING_URL_BASE}/{proposal_id}"
    contact_name = f"{body.contact_name_f} {body.contact_name_l}".strip()
    formatted_total = f"${total:,.0f}"

    try:
        send_proposal_email(
            to_email=body.contact_email.lower().strip(),
            from_email=from_email,
            contact_name=contact_name,
            org_name=org_name,
            signing_url=signing_url,
            total=formatted_total,
            subject=body.email_subject,
            body=body.email_body,
        )
    except Exception as e:
        # Log but don't fail the request if email fails
        print(f"Failed to send proposal email: {e}")

    return _serialize_proposal(proposal, items_result.data)


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


class SimpleLoginRequest(BaseModel):
    """Simple login request."""

    email: str
    password: str


class UserSystemsResponse(BaseModel):
    """User with their purchased systems."""

    user_id: str
    email: str
    name: str
    systems: list[PublicSystemResponse]


@public_router.post("/login")
async def simple_login(body: SimpleLoginRequest) -> UserSystemsResponse:
    """Simple login - returns user's purchased systems."""
    supabase = get_supabase()

    # Find user by email and password (simple plaintext check)
    user_result = (
        supabase.table("users")
        .select("id, email, name_f, name_l, password_hash")
        .eq("email", body.email.lower().strip())
        .execute()
    )

    if not user_result.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = user_result.data[0]

    # Simple password check (plaintext for testing)
    if user["password_hash"] != body.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Get user's systems via system_access
    access_result = (
        supabase.table("system_access")
        .select("system_id, systems(id, name, slug, description)")
        .eq("client_id", user["id"])
        .eq("status", 1)  # active only
        .execute()
    )

    systems = []
    for access in access_result.data:
        if access.get("systems"):
            sys = access["systems"]
            systems.append(PublicSystemResponse(
                id=sys["id"],
                name=sys["name"],
                slug=sys["slug"],
                description=sys.get("description"),
            ))

    return UserSystemsResponse(
        user_id=user["id"],
        email=user["email"],
        name=f"{user['name_f']} {user['name_l']}".strip(),
        systems=systems,
    )
