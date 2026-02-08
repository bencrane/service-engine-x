"""Projects API router."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse, Response

from app.auth import AuthContext, get_current_org
from app.config import get_settings
from app.database import get_supabase
from app.models.projects import (
    EngagementSummary,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
    ServiceSummary,
    PROJECT_STATUS_ACTIVE,
    PROJECT_STATUS_COMPLETED,
    PROJECT_STATUS_CANCELLED,
    PROJECT_STATUS_MAP,
    PROJECT_PHASE_KICKOFF,
    PROJECT_PHASE_MAP,
    VALID_PHASE_TRANSITIONS,
)
from app.utils import build_pagination_response, is_valid_uuid

router = APIRouter(prefix="/api/projects", tags=["Projects"])


def serialize_engagement_summary(engagement: dict[str, Any] | None) -> EngagementSummary | None:
    """Serialize engagement to summary model."""
    if not engagement:
        return None
    return EngagementSummary(
        id=engagement["id"],
        name=engagement.get("name"),
        client_id=engagement["client_id"],
    )


def serialize_service_summary(service: dict[str, Any] | None) -> ServiceSummary | None:
    """Serialize service to summary model."""
    if not service:
        return None
    return ServiceSummary(
        id=service["id"],
        name=service["name"],
    )


def serialize_project(
    project: dict[str, Any],
    engagement: dict[str, Any] | None = None,
    service: dict[str, Any] | None = None,
    include_relations: bool = False,
) -> ProjectResponse | ProjectListResponse:
    """Serialize project data to response model."""
    status_id = project.get("status", PROJECT_STATUS_ACTIVE)
    phase_id = project.get("phase", PROJECT_PHASE_KICKOFF)

    base = {
        "id": project["id"],
        "engagement_id": project["engagement_id"],
        "org_id": project["org_id"],
        "name": project["name"],
        "description": project.get("description"),
        "status": PROJECT_STATUS_MAP.get(status_id, "Unknown"),
        "status_id": status_id,
        "phase": PROJECT_PHASE_MAP.get(phase_id, "Unknown"),
        "phase_id": phase_id,
        "service_id": project.get("service_id"),
        "created_at": project["created_at"],
        "updated_at": project["updated_at"],
        "completed_at": project.get("completed_at"),
    }

    if include_relations:
        return ProjectResponse(
            **base,
            engagement=serialize_engagement_summary(engagement),
            service=serialize_service_summary(service),
        )
    return ProjectListResponse(**base)


@router.get("")
async def list_projects(
    request: Request,
    auth: AuthContext = Depends(get_current_org),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    sort: str = Query("created_at:desc"),
    status: int | None = Query(None, ge=1, le=4, description="Filter by status"),
    phase: int | None = Query(None, ge=1, le=6, description="Filter by phase"),
    engagement_id: str | None = Query(None, description="Filter by engagement UUID"),
) -> dict[str, Any]:
    """List all projects for the authenticated organization."""
    supabase = get_supabase()
    settings = get_settings()

    # Parse sort parameter
    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if sort_parts else "created_at"
    sort_dir = sort_parts[1] if len(sort_parts) > 1 else "desc"

    valid_sort_fields = ["id", "name", "status", "phase", "created_at", "updated_at"]
    if sort_field not in valid_sort_fields:
        sort_field = "created_at"
    ascending = sort_dir == "asc"

    # Build base query
    query = (
        supabase.table("projects")
        .select("*", count="exact")
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
    )

    # Apply filters
    if status is not None:
        query = query.eq("status", status)
    if phase is not None:
        query = query.eq("phase", phase)
    if engagement_id is not None:
        if not is_valid_uuid(engagement_id):
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid engagement_id format"},
            )
        query = query.eq("engagement_id", engagement_id)

    # Get total count
    query = query.order(sort_field, desc=not ascending)
    count_result = query.execute()
    total = count_result.count or 0

    # Apply pagination
    offset = (page - 1) * limit
    query = (
        supabase.table("projects")
        .select("*")
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
    )
    if status is not None:
        query = query.eq("status", status)
    if phase is not None:
        query = query.eq("phase", phase)
    if engagement_id is not None:
        query = query.eq("engagement_id", engagement_id)

    query = query.order(sort_field, desc=not ascending).range(offset, offset + limit - 1)
    result = query.execute()
    projects = result.data or []

    # Serialize
    serialized = [
        serialize_project(p, include_relations=False).model_dump()
        for p in projects
    ]

    path = f"{settings.api_base_url}/api/projects"
    return build_pagination_response(serialized, total, page, limit, path)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate,
    auth: AuthContext = Depends(get_current_org),
) -> ProjectResponse:
    """Create a new project within an engagement."""
    supabase = get_supabase()

    # Validate engagement exists and belongs to org
    if not is_valid_uuid(body.engagement_id):
        return JSONResponse(
            status_code=400,
            content={"message": "Invalid engagement_id format", "errors": {"engagement_id": ["Invalid UUID"]}},
        )

    engagement_result = (
        supabase.table("engagements")
        .select("id, name, client_id, status")
        .eq("id", body.engagement_id)
        .eq("org_id", auth.org_id)
        .execute()
    )
    if not engagement_result.data:
        return JSONResponse(
            status_code=400,
            content={"message": "Engagement not found", "errors": {"engagement_id": ["Engagement not found"]}},
        )
    engagement_data = engagement_result.data[0]

    # Validate service if provided
    service_data = None
    if body.service_id:
        if not is_valid_uuid(body.service_id):
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid service_id format", "errors": {"service_id": ["Invalid UUID"]}},
            )
        service_result = (
            supabase.table("services")
            .select("id, name")
            .eq("id", body.service_id)
            .eq("org_id", auth.org_id)
            .is_("deleted_at", "null")
            .execute()
        )
        if not service_result.data:
            return JSONResponse(
                status_code=400,
                content={"message": "Service not found", "errors": {"service_id": ["Service not found"]}},
            )
        service_data = service_result.data[0]

    # Create project
    now = datetime.now(timezone.utc).isoformat()
    project_data = {
        "engagement_id": body.engagement_id,
        "org_id": auth.org_id,
        "name": body.name.strip(),
        "description": body.description,
        "status": PROJECT_STATUS_ACTIVE,
        "phase": PROJECT_PHASE_KICKOFF,
        "service_id": body.service_id,
        "created_at": now,
        "updated_at": now,
    }

    result = supabase.table("projects").insert(project_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project",
        )

    new_project = result.data[0]
    return serialize_project(
        new_project,
        engagement=engagement_data,
        service=service_data,
        include_relations=True,
    )


@router.get("/{project_id}")
async def retrieve_project(
    project_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> ProjectResponse:
    """Retrieve a project with its engagement and service info."""
    if not is_valid_uuid(project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get project
    result = (
        supabase.table("projects")
        .select("*")
        .eq("id", project_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    project = result.data[0]

    # Get engagement
    engagement_result = (
        supabase.table("engagements")
        .select("id, name, client_id")
        .eq("id", project["engagement_id"])
        .execute()
    )
    engagement_data = engagement_result.data[0] if engagement_result.data else None

    # Get service if linked
    service_data = None
    if project.get("service_id"):
        service_result = (
            supabase.table("services")
            .select("id, name")
            .eq("id", project["service_id"])
            .execute()
        )
        service_data = service_result.data[0] if service_result.data else None

    return serialize_project(
        project,
        engagement=engagement_data,
        service=service_data,
        include_relations=True,
    )


@router.put("/{project_id}")
async def update_project(
    project_id: str,
    body: ProjectUpdate,
    auth: AuthContext = Depends(get_current_org),
) -> ProjectResponse:
    """Update a project."""
    if not is_valid_uuid(project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get existing project
    existing_result = (
        supabase.table("projects")
        .select("*")
        .eq("id", project_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not existing_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    existing = existing_result.data[0]
    now = datetime.now(timezone.utc).isoformat()

    # Build update payload
    update_payload: dict[str, Any] = {"updated_at": now}

    if body.name is not None:
        update_payload["name"] = body.name.strip()

    if body.description is not None:
        update_payload["description"] = body.description

    if body.status is not None:
        update_payload["status"] = body.status
        # Set completed_at when transitioning to Completed
        if body.status == PROJECT_STATUS_COMPLETED and existing["status"] != PROJECT_STATUS_COMPLETED:
            update_payload["completed_at"] = now
        # Clear completed_at when transitioning away from Completed
        elif body.status != PROJECT_STATUS_COMPLETED and existing["status"] == PROJECT_STATUS_COMPLETED:
            update_payload["completed_at"] = None

    if body.phase is not None:
        current_phase = existing["phase"]
        # Validate phase transition
        valid_transitions = VALID_PHASE_TRANSITIONS.get(current_phase, [])
        if body.phase not in valid_transitions and body.phase != current_phase:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "Invalid phase transition",
                    "errors": {
                        "phase": [f"Cannot transition from {PROJECT_PHASE_MAP[current_phase]} to {PROJECT_PHASE_MAP.get(body.phase, 'Unknown')}"]
                    },
                },
            )
        update_payload["phase"] = body.phase

    # Update
    result = (
        supabase.table("projects")
        .update(update_payload)
        .eq("id", project_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project",
        )

    updated = result.data[0]

    # Fetch engagement and service for response
    engagement_result = (
        supabase.table("engagements")
        .select("id, name, client_id")
        .eq("id", updated["engagement_id"])
        .execute()
    )
    engagement_data = engagement_result.data[0] if engagement_result.data else None

    service_data = None
    if updated.get("service_id"):
        service_result = (
            supabase.table("services")
            .select("id, name")
            .eq("id", updated["service_id"])
            .execute()
        )
        service_data = service_result.data[0] if service_result.data else None

    return serialize_project(
        updated,
        engagement=engagement_data,
        service=service_data,
        include_relations=True,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> Response:
    """Soft delete a project."""
    if not is_valid_uuid(project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify exists
    existing = (
        supabase.table("projects")
        .select("id")
        .eq("id", project_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Soft delete
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("projects").update({
        "deleted_at": now,
        "updated_at": now,
    }).eq("id", project_id).execute()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{project_id}/advance", status_code=status.HTTP_200_OK)
async def advance_project_phase(
    project_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> ProjectResponse:
    """Advance a project to the next phase."""
    if not is_valid_uuid(project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get existing project
    existing_result = (
        supabase.table("projects")
        .select("*")
        .eq("id", project_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not existing_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    existing = existing_result.data[0]
    current_phase = existing["phase"]

    # Check if already at final phase
    if current_phase >= 6:
        return JSONResponse(
            status_code=400,
            content={"message": "Project is already at final phase (Handoff)"},
        )

    # Advance to next phase
    next_phase = current_phase + 1
    now = datetime.now(timezone.utc).isoformat()

    result = (
        supabase.table("projects")
        .update({"phase": next_phase, "updated_at": now})
        .eq("id", project_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to advance project phase",
        )

    updated = result.data[0]

    # Fetch relations
    engagement_result = (
        supabase.table("engagements")
        .select("id, name, client_id")
        .eq("id", updated["engagement_id"])
        .execute()
    )
    engagement_data = engagement_result.data[0] if engagement_result.data else None

    service_data = None
    if updated.get("service_id"):
        service_result = (
            supabase.table("services")
            .select("id, name")
            .eq("id", updated["service_id"])
            .execute()
        )
        service_data = service_result.data[0] if service_result.data else None

    return serialize_project(
        updated,
        engagement=engagement_data,
        service=service_data,
        include_relations=True,
    )
