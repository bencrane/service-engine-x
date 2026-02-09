"""Engagements API router."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse, Response

from app.auth import AuthContext, get_current_auth
from app.config import get_settings
from app.database import get_supabase
from app.models.engagements import (
    ClientSummary,
    ConversationSummary,
    EngagementCreate,
    EngagementListResponse,
    EngagementResponse,
    EngagementUpdate,
    ProjectSummary,
    ENGAGEMENT_STATUS_ACTIVE,
    ENGAGEMENT_STATUS_CLOSED,
    ENGAGEMENT_STATUS_MAP,
)
from app.utils import build_pagination_response, is_valid_uuid

router = APIRouter(prefix="/api/engagements", tags=["Engagements"])

# Project status/phase maps (duplicated here, will be in projects model later)
PROJECT_STATUS_MAP = {1: "Active", 2: "Paused", 3: "Completed", 4: "Cancelled"}
PROJECT_PHASE_MAP = {1: "Kickoff", 2: "Setup", 3: "Build", 4: "Testing", 5: "Deployment", 6: "Handoff"}
CONVERSATION_STATUS_MAP = {1: "Open", 2: "Closed"}


def serialize_client(client: dict[str, Any] | None) -> ClientSummary | None:
    """Serialize client data to summary model."""
    if not client:
        return None
    return ClientSummary(
        id=client["id"],
        name=f"{client.get('name_f', '')} {client.get('name_l', '')}".strip(),
        email=client.get("email", ""),
    )


def serialize_project_summary(project: dict[str, Any]) -> ProjectSummary:
    """Serialize project to summary model."""
    status_id = project.get("status", 1)
    phase_id = project.get("phase", 1)
    return ProjectSummary(
        id=project["id"],
        name=project["name"],
        status=PROJECT_STATUS_MAP.get(status_id, "Unknown"),
        status_id=status_id,
        phase=PROJECT_PHASE_MAP.get(phase_id, "Unknown"),
        phase_id=phase_id,
    )


def serialize_conversation_summary(conv: dict[str, Any]) -> ConversationSummary:
    """Serialize conversation to summary model."""
    status_id = conv.get("status", 1)
    return ConversationSummary(
        id=conv["id"],
        subject=conv.get("subject"),
        status=CONVERSATION_STATUS_MAP.get(status_id, "Unknown"),
        status_id=status_id,
        last_message_at=conv.get("last_message_at"),
    )


def serialize_engagement(
    engagement: dict[str, Any],
    client: dict[str, Any] | None = None,
    projects: list[dict[str, Any]] | None = None,
    conversations: list[dict[str, Any]] | None = None,
    include_nested: bool = False,
) -> EngagementResponse | EngagementListResponse:
    """Serialize engagement data to response model."""
    status_id = engagement.get("status", ENGAGEMENT_STATUS_ACTIVE)

    base = {
        "id": engagement["id"],
        "org_id": engagement["org_id"],
        "client_id": engagement["client_id"],
        "client": serialize_client(client),
        "name": engagement.get("name"),
        "status": ENGAGEMENT_STATUS_MAP.get(status_id, "Unknown"),
        "status_id": status_id,
        "proposal_id": engagement.get("proposal_id"),
        "created_at": engagement["created_at"],
        "updated_at": engagement["updated_at"],
        "closed_at": engagement.get("closed_at"),
    }

    if include_nested:
        return EngagementResponse(
            **base,
            projects=[serialize_project_summary(p) for p in (projects or [])],
            conversations=[serialize_conversation_summary(c) for c in (conversations or [])],
        )
    return EngagementListResponse(**base)


@router.get("")
async def list_engagements(
    request: Request,
    auth: AuthContext = Depends(get_current_auth),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    sort: str = Query("created_at:desc"),
    status: int | None = Query(None, ge=1, le=3, description="Filter by status"),
    client_id: str | None = Query(None, description="Filter by client UUID"),
) -> dict[str, Any]:
    """List all engagements for the authenticated organization."""
    supabase = get_supabase()
    settings = get_settings()

    # Parse sort parameter
    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if sort_parts else "created_at"
    sort_dir = sort_parts[1] if len(sort_parts) > 1 else "desc"

    valid_sort_fields = ["id", "name", "status", "created_at", "updated_at"]
    if sort_field not in valid_sort_fields:
        sort_field = "created_at"
    ascending = sort_dir == "asc"

    # Build query with client join
    query = (
        supabase.table("engagements")
        .select("*, client:users!client_id(id, name_f, name_l, email)", count="exact")
        .eq("org_id", auth.org_id)
    )

    # Apply filters
    if status is not None:
        query = query.eq("status", status)
    if client_id is not None:
        if not is_valid_uuid(client_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Invalid client_id format"},
            )
        query = query.eq("client_id", client_id)

    # Get total count
    query = query.order(sort_field, desc=not ascending)
    count_result = query.execute()
    total = count_result.count or 0

    # Apply pagination
    offset = (page - 1) * limit
    query = (
        supabase.table("engagements")
        .select("*, client:users!client_id(id, name_f, name_l, email)")
        .eq("org_id", auth.org_id)
    )
    if status is not None:
        query = query.eq("status", status)
    if client_id is not None:
        query = query.eq("client_id", client_id)

    query = query.order(sort_field, desc=not ascending).range(offset, offset + limit - 1)
    result = query.execute()
    engagements = result.data or []

    # Serialize
    serialized = []
    for eng in engagements:
        client_data = eng.get("client")
        if isinstance(client_data, list):
            client_data = client_data[0] if client_data else None
        serialized.append(
            serialize_engagement(eng, client=client_data, include_nested=False).model_dump()
        )

    path = f"{settings.api_base_url}/api/engagements"
    return build_pagination_response(serialized, total, page, limit, path)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_engagement(
    body: EngagementCreate,
    auth: AuthContext = Depends(get_current_auth),
) -> EngagementResponse:
    """Create a new engagement."""
    supabase = get_supabase()

    # Validate client exists and belongs to org
    if not is_valid_uuid(body.client_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Invalid client_id format", "errors": {"client_id": ["Invalid UUID"]}},
        )

    client_result = (
        supabase.table("users")
        .select("id, name_f, name_l, email")
        .eq("id", body.client_id)
        .eq("org_id", auth.org_id)
        .execute()
    )
    if not client_result.data:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Client not found", "errors": {"client_id": ["Client not found in organization"]}},
        )
    client_data = client_result.data[0]

    # Validate proposal if provided
    if body.proposal_id:
        if not is_valid_uuid(body.proposal_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Invalid proposal_id format", "errors": {"proposal_id": ["Invalid UUID"]}},
            )
        proposal_result = (
            supabase.table("proposals")
            .select("id")
            .eq("id", body.proposal_id)
            .eq("org_id", auth.org_id)
            .execute()
        )
        if not proposal_result.data:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Proposal not found", "errors": {"proposal_id": ["Proposal not found"]}},
            )

    # Create engagement
    now = datetime.now(timezone.utc).isoformat()
    engagement_data = {
        "org_id": auth.org_id,
        "client_id": body.client_id,
        "name": body.name,
        "status": ENGAGEMENT_STATUS_ACTIVE,
        "proposal_id": body.proposal_id,
        "created_at": now,
        "updated_at": now,
    }

    result = supabase.table("engagements").insert(engagement_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create engagement",
        )

    new_engagement = result.data[0]
    return serialize_engagement(new_engagement, client=client_data, include_nested=True)


@router.get("/{engagement_id}")
async def retrieve_engagement(
    engagement_id: str,
    auth: AuthContext = Depends(get_current_auth),
) -> EngagementResponse:
    """Retrieve an engagement with its projects and conversations."""
    if not is_valid_uuid(engagement_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get engagement with client
    result = (
        supabase.table("engagements")
        .select("*, client:users!client_id(id, name_f, name_l, email)")
        .eq("id", engagement_id)
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    engagement = result.data[0]
    client_data = engagement.get("client")
    if isinstance(client_data, list):
        client_data = client_data[0] if client_data else None

    # Get projects (non-deleted)
    projects_result = (
        supabase.table("projects")
        .select("id, name, status, phase")
        .eq("engagement_id", engagement_id)
        .is_("deleted_at", "null")
        .order("created_at", desc=False)
        .execute()
    )
    projects = projects_result.data or []

    # Get conversations across all projects in the engagement
    project_ids = [p["id"] for p in projects]
    conversations: list[dict[str, Any]] = []
    if project_ids:
        conversations_result = (
            supabase.table("conversations")
            .select("id, subject, status, last_message_at")
            .in_("project_id", project_ids)
            .order("last_message_at", desc=True, nullsfirst=False)
            .execute()
        )
        conversations = conversations_result.data or []

    return serialize_engagement(
        engagement,
        client=client_data,
        projects=projects,
        conversations=conversations,
        include_nested=True,
    )


@router.put("/{engagement_id}")
async def update_engagement(
    engagement_id: str,
    body: EngagementUpdate,
    auth: AuthContext = Depends(get_current_auth),
) -> EngagementResponse:
    """Update an engagement."""
    if not is_valid_uuid(engagement_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get existing engagement
    existing_result = (
        supabase.table("engagements")
        .select("*")
        .eq("id", engagement_id)
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not existing_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    existing = existing_result.data[0]
    now = datetime.now(timezone.utc).isoformat()

    # Build update payload
    update_payload: dict[str, Any] = {"updated_at": now}

    if body.name is not None:
        update_payload["name"] = body.name

    if body.status is not None:
        update_payload["status"] = body.status
        # Set closed_at when transitioning to Closed
        if body.status == ENGAGEMENT_STATUS_CLOSED and existing["status"] != ENGAGEMENT_STATUS_CLOSED:
            update_payload["closed_at"] = now
        # Clear closed_at when transitioning away from Closed
        elif body.status != ENGAGEMENT_STATUS_CLOSED and existing["status"] == ENGAGEMENT_STATUS_CLOSED:
            update_payload["closed_at"] = None

    # Update
    result = (
        supabase.table("engagements")
        .update(update_payload)
        .eq("id", engagement_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update engagement",
        )

    updated = result.data[0]

    # Fetch client for response
    client_result = (
        supabase.table("users")
        .select("id, name_f, name_l, email")
        .eq("id", updated["client_id"])
        .execute()
    )
    client_data = client_result.data[0] if client_result.data else None

    # Fetch projects for response
    projects_result = (
        supabase.table("projects")
        .select("id, name, status, phase")
        .eq("engagement_id", engagement_id)
        .is_("deleted_at", "null")
        .execute()
    )
    projects = projects_result.data or []

    # Fetch conversations across all projects in the engagement
    project_ids = [p["id"] for p in projects]
    conversations: list[dict[str, Any]] = []
    if project_ids:
        conversations_result = (
            supabase.table("conversations")
            .select("id, subject, status, last_message_at")
            .in_("project_id", project_ids)
            .execute()
        )
        conversations = conversations_result.data or []

    return serialize_engagement(
        updated,
        client=client_data,
        projects=projects,
        conversations=conversations,
        include_nested=True,
    )


@router.delete("/{engagement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_engagement(
    engagement_id: str,
    auth: AuthContext = Depends(get_current_auth),
) -> Response:
    """
    Close an engagement (sets status to Closed).

    Engagements are not hard-deleted to preserve history.
    Use this to close an engagement relationship.
    """
    if not is_valid_uuid(engagement_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify exists
    existing = (
        supabase.table("engagements")
        .select("id, status")
        .eq("id", engagement_id)
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Close the engagement (soft close via status)
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("engagements").update({
        "status": ENGAGEMENT_STATUS_CLOSED,
        "closed_at": now,
        "updated_at": now,
    }).eq("id", engagement_id).execute()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
