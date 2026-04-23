"""Internal API router for admin panels."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.auth import verify_token
from app.config import settings
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

router = APIRouter(prefix="/api/internal", tags=["Internal"])


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


@router.get("/orgs", dependencies=[Depends(verify_token)])
async def list_organizations() -> list[OrganizationResponse]:
    """List all organizations."""
    supabase = get_supabase()
    result = supabase.table("organizations").select("id, name, slug, domain").execute()
    return [OrganizationResponse(**org) for org in result.data]


@router.get("/orgs/{org_id}/services", dependencies=[Depends(verify_token)])
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


@router.post("/services", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_token)])
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


@router.post("/proposals", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_token)])
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

    proposal_result = supabase.table("proposals").insert(proposal_data).execute()
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

    items_result = supabase.table("proposal_items").insert(item_rows).execute()
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


# ============== Accounts ==============


@router.get("/orgs/{org_id}/accounts", dependencies=[Depends(verify_token)])
async def list_accounts_for_org(
    org_id: str,
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None),
) -> list[dict[str, Any]]:
    """List accounts (companies) for an organization."""
    supabase = get_supabase()
    query = (
        supabase.table("accounts")
        .select("*")
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .order("created_at", desc=True)
        .limit(limit)
    )
    if search:
        query = query.or_(f"name.ilike.%{search}%,domain.ilike.%{search}%")
    result = query.execute()
    return result.data or []


@router.get("/orgs/{org_id}/accounts/{account_id}", dependencies=[Depends(verify_token)])
async def get_account_for_org(org_id: str, account_id: str) -> dict[str, Any]:
    """Get a specific account."""
    supabase = get_supabase()
    result = (
        supabase.table("accounts")
        .select("*")
        .eq("id", account_id)
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Account not found")
    return result.data[0]


# ============== Contacts ==============


@router.get("/orgs/{org_id}/contacts", dependencies=[Depends(verify_token)])
async def list_contacts_for_org(
    org_id: str,
    limit: int = Query(50, ge=1, le=100),
    account_id: str | None = Query(None),
    search: str | None = Query(None),
) -> list[dict[str, Any]]:
    """List contacts (people) for an organization."""
    supabase = get_supabase()
    query = (
        supabase.table("contacts")
        .select("*, accounts:account_id (id, name)")
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .order("created_at", desc=True)
        .limit(limit)
    )
    if account_id:
        query = query.eq("account_id", account_id)
    if search:
        query = query.or_(f"email.ilike.%{search}%,name_f.ilike.%{search}%,name_l.ilike.%{search}%")
    result = query.execute()
    return result.data or []


@router.get("/orgs/{org_id}/contacts/{contact_id}", dependencies=[Depends(verify_token)])
async def get_contact_for_org(org_id: str, contact_id: str) -> dict[str, Any]:
    """Get a specific contact."""
    supabase = get_supabase()
    result = (
        supabase.table("contacts")
        .select("*, accounts:account_id (id, name)")
        .eq("id", contact_id)
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Contact not found")
    return result.data[0]


class ContactUpsertRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    name_f: str | None = Field(None, max_length=100)
    name_l: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=50)
    title: str | None = Field(None, max_length=100)
    account_id: str | None = None


@router.post("/orgs/{org_id}/contacts/upsert", dependencies=[Depends(verify_token)])
async def upsert_contact_for_org(
    org_id: str,
    body: ContactUpsertRequest,
) -> dict[str, Any]:
    """Upsert a contact by (org_id, email). Idempotent: used by Cal.com booking orchestration to ensure attendee contacts exist before linking to meetings."""
    supabase = get_supabase()
    email = body.email.lower().strip()

    existing = (
        supabase.table("contacts")
        .select("*")
        .eq("org_id", org_id)
        .eq("email", email)
        .is_("deleted_at", "null")
        .limit(1)
        .execute()
    )

    now = datetime.now(timezone.utc).isoformat()

    if existing.data:
        contact = existing.data[0]
        update_payload: dict[str, Any] = {"updated_at": now}
        if body.name_f is not None and body.name_f.strip():
            update_payload["name_f"] = body.name_f.strip()
        if body.name_l is not None and body.name_l.strip():
            update_payload["name_l"] = body.name_l.strip()
        if body.phone is not None:
            update_payload["phone"] = body.phone
        if body.title is not None:
            update_payload["title"] = body.title
        if body.account_id is not None:
            update_payload["account_id"] = body.account_id or None

        if len(update_payload) > 1:
            result = (
                supabase.table("contacts")
                .update(update_payload)
                .eq("id", contact["id"])
                .execute()
            )
            contact = result.data[0] if result.data else contact

        return {"contact_id": contact["id"], "created": False, "contact": contact}

    insert_payload = {
        "org_id": org_id,
        "account_id": body.account_id or None,
        "name_f": (body.name_f or "").strip() or "Unknown",
        "name_l": (body.name_l or "").strip() or "Unknown",
        "email": email,
        "phone": body.phone,
        "title": body.title,
        "is_primary": False,
        "is_billing": False,
        "custom_fields": {},
        "created_at": now,
        "updated_at": now,
    }
    result = supabase.table("contacts").insert(insert_payload).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to upsert contact")
    contact = result.data[0]
    return {"contact_id": contact["id"], "created": True, "contact": contact}


# ============== Proposals (Read) ==============


@router.get("/orgs/{org_id}/proposals", dependencies=[Depends(verify_token)])
async def list_proposals_for_org(
    org_id: str,
    limit: int = Query(50, ge=1, le=100),
    status: int | None = Query(None, description="0=Draft, 1=Sent, 2=Signed, 3=Rejected"),
) -> list[dict[str, Any]]:
    """List proposals for an organization."""
    supabase = get_supabase()
    query = (
        supabase.table("proposals")
        .select("*, proposal_items (*)")
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .order("created_at", desc=True)
        .limit(limit)
    )
    if status is not None:
        query = query.eq("status", status)
    result = query.execute()

    # Serialize proposals
    proposals = []
    for p in (result.data or []):
        items = p.pop("proposal_items", []) or []
        proposals.append(_serialize_proposal(p, items).model_dump())
    return proposals


@router.get("/orgs/{org_id}/proposals/{proposal_id}", dependencies=[Depends(verify_token)])
async def get_proposal_for_org(org_id: str, proposal_id: str) -> dict[str, Any]:
    """Get a specific proposal with items."""
    supabase = get_supabase()
    result = (
        supabase.table("proposals")
        .select("*, proposal_items (*)")
        .eq("id", proposal_id)
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Proposal not found")

    proposal = result.data[0]
    items = proposal.pop("proposal_items", []) or []
    return _serialize_proposal(proposal, items).model_dump()


@router.get("/orgs/{org_id}/proposals/{proposal_id}/deliverables", dependencies=[Depends(verify_token)])
async def get_proposal_deliverables_for_org(org_id: str, proposal_id: str) -> dict[str, Any]:
    """
    Get deliverables (projects with service details) for a signed proposal.

    Returns the projects created from this proposal with their linked service info.
    """
    supabase = get_supabase()

    # Fetch proposal
    result = (
        supabase.table("proposals")
        .select("*, proposal_items (*)")
        .eq("id", proposal_id)
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Proposal not found")

    proposal = result.data[0]

    # Must be signed
    if proposal["status"] != 2:
        raise HTTPException(
            status_code=400,
            detail="Proposal is not signed. Deliverables are only available after signing.",
        )

    engagement_id = proposal.get("converted_engagement_id")
    order_id = proposal.get("converted_order_id")

    if not engagement_id:
        raise HTTPException(status_code=500, detail="Signed proposal missing engagement reference")

    # Fetch engagement
    engagement_result = supabase.table("engagements").select("*").eq("id", engagement_id).execute()
    engagement = engagement_result.data[0] if engagement_result.data else None

    # Fetch projects with service details
    projects_result = (
        supabase.table("projects")
        .select("*, services:service_id (id, name, description, price, recurring)")
        .eq("engagement_id", engagement_id)
        .is_("deleted_at", "null")
        .order("created_at", desc=False)
        .execute()
    )
    projects = projects_result.data or []

    # Fetch order
    order = None
    if order_id:
        order_result = supabase.table("orders").select("*").eq("id", order_id).execute()
        if order_result.data:
            order = order_result.data[0]

    client_name = f"{proposal.get('client_name_f', '')} {proposal.get('client_name_l', '')}".strip()

    return {
        "proposal": {
            "id": proposal["id"],
            "account_name": proposal.get("client_company"),
            "contact_name": client_name,
            "contact_email": proposal.get("client_email"),
            "total": f"{float(proposal.get('total', 0)):.2f}",
            "signed_at": proposal.get("signed_at"),
            "notes": proposal.get("notes"),
        },
        "engagement": {
            "id": engagement["id"],
            "name": engagement["name"],
            "status": "Active" if engagement["status"] == 1 else "Paused" if engagement["status"] == 2 else "Closed",
            "status_id": engagement["status"],
            "created_at": engagement["created_at"],
        } if engagement else None,
        "projects": [
            {
                "id": p["id"],
                "name": p["name"],
                "description": p.get("description"),
                "status": "Active" if p["status"] == 1 else "Paused" if p["status"] == 2 else "Completed" if p["status"] == 3 else "Cancelled",
                "status_id": p["status"],
                "phase": {1: "Kickoff", 2: "Setup", 3: "Build", 4: "Testing", 5: "Deployment", 6: "Handoff"}.get(p.get("phase", 1), "Kickoff"),
                "phase_id": p.get("phase", 1),
                "service": {
                    "id": p["services"]["id"],
                    "name": p["services"]["name"],
                    "description": p["services"].get("description"),
                    "price": f"{float(p['services'].get('price', 0)):.2f}",
                    "recurring": p["services"].get("recurring", 0),
                } if p.get("services") else None,
                "created_at": p["created_at"],
            }
            for p in projects
        ],
        "order": {
            "id": order["id"],
            "number": order["number"],
            "price": f"{float(order.get('price', 0)):.2f}",
            "currency": order.get("currency", "USD"),
            "status": {0: "Unpaid", 1: "In Progress", 2: "Completed", 3: "Cancelled", 4: "On Hold"}.get(order.get("status", 0), "Unknown"),
            "status_id": order.get("status", 0),
            "paid_at": order.get("paid_at"),
            "created_at": order["created_at"],
        } if order else None,
    }


# ============== Engagements ==============


@router.get("/orgs/{org_id}/engagements", dependencies=[Depends(verify_token)])
async def list_engagements_for_org(
    org_id: str,
    limit: int = Query(50, ge=1, le=100),
    status: int | None = Query(None, description="1=Active, 2=Paused, 3=Closed"),
    account_id: str | None = Query(None),
) -> list[dict[str, Any]]:
    """List engagements for an organization."""
    supabase = get_supabase()
    query = (
        supabase.table("engagements")
        .select("*, accounts:account_id (id, name), projects (id, name, status, phase)")
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .order("created_at", desc=True)
        .limit(limit)
    )
    if status is not None:
        query = query.eq("status", status)
    if account_id:
        query = query.eq("account_id", account_id)
    result = query.execute()
    return result.data or []


@router.get("/orgs/{org_id}/engagements/{engagement_id}", dependencies=[Depends(verify_token)])
async def get_engagement_for_org(org_id: str, engagement_id: str) -> dict[str, Any]:
    """Get a specific engagement with projects."""
    supabase = get_supabase()
    result = (
        supabase.table("engagements")
        .select("*, accounts:account_id (id, name), projects (*, services:service_id (id, name, price))")
        .eq("id", engagement_id)
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Engagement not found")
    return result.data[0]


# ============== Projects ==============


@router.get("/orgs/{org_id}/projects", dependencies=[Depends(verify_token)])
async def list_projects_for_org(
    org_id: str,
    limit: int = Query(50, ge=1, le=100),
    status: int | None = Query(None, description="1=Active, 2=Paused, 3=Completed, 4=Cancelled"),
    engagement_id: str | None = Query(None),
) -> list[dict[str, Any]]:
    """List projects for an organization."""
    supabase = get_supabase()
    query = (
        supabase.table("projects")
        .select("*, services:service_id (id, name), engagements:engagement_id (id, name)")
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .order("created_at", desc=True)
        .limit(limit)
    )
    if status is not None:
        query = query.eq("status", status)
    if engagement_id:
        query = query.eq("engagement_id", engagement_id)
    result = query.execute()
    return result.data or []


@router.get("/orgs/{org_id}/projects/{project_id}", dependencies=[Depends(verify_token)])
async def get_project_for_org(org_id: str, project_id: str) -> dict[str, Any]:
    """Get a specific project."""
    supabase = get_supabase()
    result = (
        supabase.table("projects")
        .select("*, services:service_id (id, name, description, price), engagements:engagement_id (id, name, account_id)")
        .eq("id", project_id)
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Project not found")
    return result.data[0]


# ============== Orders ==============


@router.get("/orgs/{org_id}/orders", dependencies=[Depends(verify_token)])
async def list_orders_for_org(
    org_id: str,
    limit: int = Query(50, ge=1, le=100),
    status: int | None = Query(None, description="0=Unpaid, 1=In Progress, 2=Completed, 3=Cancelled, 4=On Hold"),
    account_id: str | None = Query(None),
) -> list[dict[str, Any]]:
    """List orders for an organization."""
    supabase = get_supabase()
    query = (
        supabase.table("orders")
        .select("*, accounts:account_id (id, name)")
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .order("created_at", desc=True)
        .limit(limit)
    )
    if status is not None:
        query = query.eq("status", status)
    if account_id:
        query = query.eq("account_id", account_id)
    result = query.execute()
    return result.data or []


@router.get("/orgs/{org_id}/orders/{order_id}", dependencies=[Depends(verify_token)])
async def get_order_for_org(org_id: str, order_id: str) -> dict[str, Any]:
    """Get a specific order."""
    supabase = get_supabase()
    result = (
        supabase.table("orders")
        .select("*, accounts:account_id (id, name), engagements:engagement_id (id, name)")
        .eq("id", order_id)
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Order not found")
    return result.data[0]


