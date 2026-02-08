"""Conversations API router - Project-scoped."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse, Response

from app.auth import AuthContext, get_current_org
from app.config import get_settings
from app.database import get_supabase
from app.models.conversations import (
    Attachment,
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
    ProjectBrief,
    MessageCreate,
    MessageResponse,
    SenderSummary,
    CONVERSATION_STATUS_OPEN,
    CONVERSATION_STATUS_CLOSED,
    CONVERSATION_STATUS_MAP,
)
from app.utils import build_pagination_response, is_valid_uuid

router = APIRouter(prefix="/api/projects", tags=["Conversations"])


def serialize_sender(user: dict[str, Any] | None) -> SenderSummary | None:
    """Serialize user to sender summary."""
    if not user:
        return None
    return SenderSummary(
        id=user["id"],
        name=f"{user.get('name_f', '')} {user.get('name_l', '')}".strip(),
        email=user.get("email", ""),
    )


def serialize_message(
    message: dict[str, Any],
    sender: dict[str, Any] | None = None,
) -> MessageResponse:
    """Serialize message data to response model."""
    attachments_raw = message.get("attachments") or []
    attachments = [
        Attachment(name=a.get("name", ""), url=a.get("url", ""), size=a.get("size"))
        for a in attachments_raw
    ]

    return MessageResponse(
        id=message["id"],
        conversation_id=message["conversation_id"],
        sender_id=message["sender_id"],
        sender=serialize_sender(sender),
        content=message["content"],
        is_internal=message.get("is_internal", False),
        attachments=attachments,
        created_at=message["created_at"],
        updated_at=message["updated_at"],
    )


def serialize_project_brief(project: dict[str, Any] | None) -> ProjectBrief | None:
    """Serialize project to brief model."""
    if not project:
        return None
    return ProjectBrief(
        id=project["id"],
        name=project.get("name"),
        engagement_id=project["engagement_id"],
    )


def serialize_conversation(
    conversation: dict[str, Any],
    project: dict[str, Any] | None = None,
    messages: list[dict[str, Any]] | None = None,
    message_count: int | None = None,
    include_messages: bool = False,
) -> ConversationResponse | ConversationListResponse:
    """Serialize conversation data to response model."""
    status_id = conversation.get("status", CONVERSATION_STATUS_OPEN)

    base = {
        "id": conversation["id"],
        "project_id": conversation["project_id"],
        "org_id": conversation["org_id"],
        "subject": conversation.get("subject"),
        "status": CONVERSATION_STATUS_MAP.get(status_id, "Unknown"),
        "status_id": status_id,
        "created_at": conversation["created_at"],
        "updated_at": conversation["updated_at"],
        "last_message_at": conversation.get("last_message_at"),
    }

    if include_messages:
        return ConversationResponse(
            **base,
            project=serialize_project_brief(project),
            messages=messages,
            message_count=len(messages) if messages else 0,
        )

    return ConversationListResponse(
        **base,
        message_count=message_count or 0,
    )


@router.get("/{project_id}/conversations")
async def list_conversations(
    project_id: str,
    request: Request,
    auth: AuthContext = Depends(get_current_org),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    sort: str = Query("last_message_at:desc"),
    status: int | None = Query(None, ge=1, le=2, description="Filter by status"),
) -> dict[str, Any]:
    """List all conversations for a project."""
    if not is_valid_uuid(project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()
    settings = get_settings()

    # Verify project exists and belongs to org
    project_result = (
        supabase.table("projects")
        .select("id")
        .eq("id", project_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not project_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Parse sort parameter
    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if sort_parts else "last_message_at"
    sort_dir = sort_parts[1] if len(sort_parts) > 1 else "desc"

    valid_sort_fields = ["id", "subject", "status", "created_at", "updated_at", "last_message_at"]
    if sort_field not in valid_sort_fields:
        sort_field = "last_message_at"
    ascending = sort_dir == "asc"

    # Build base query
    query = (
        supabase.table("conversations")
        .select("*", count="exact")
        .eq("org_id", auth.org_id)
        .eq("project_id", project_id)
    )

    # Apply filters
    if status is not None:
        query = query.eq("status", status)

    # Get total count
    query = query.order(sort_field, desc=not ascending, nullsfirst=False)
    count_result = query.execute()
    total = count_result.count or 0

    # Apply pagination
    offset = (page - 1) * limit
    query = (
        supabase.table("conversations")
        .select("*")
        .eq("org_id", auth.org_id)
        .eq("project_id", project_id)
    )
    if status is not None:
        query = query.eq("status", status)

    query = query.order(sort_field, desc=not ascending, nullsfirst=False).range(offset, offset + limit - 1)
    result = query.execute()
    conversations = result.data or []

    # Get message counts for each conversation
    conv_ids = [c["id"] for c in conversations]
    message_counts: dict[str, int] = {}

    if conv_ids:
        for conv_id in conv_ids:
            count_result = (
                supabase.table("conversation_messages")
                .select("id", count="exact")
                .eq("conversation_id", conv_id)
                .is_("deleted_at", "null")
                .execute()
            )
            message_counts[conv_id] = count_result.count or 0

    # Serialize
    serialized = [
        serialize_conversation(
            c,
            message_count=message_counts.get(c["id"], 0),
            include_messages=False,
        ).model_dump()
        for c in conversations
    ]

    path = f"{settings.api_base_url}/api/projects/{project_id}/conversations"
    return build_pagination_response(serialized, total, page, limit, path)


@router.post("/{project_id}/conversations", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    project_id: str,
    body: ConversationCreate,
    auth: AuthContext = Depends(get_current_org),
) -> ConversationResponse:
    """Create a new conversation within a project."""
    if not is_valid_uuid(project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Validate project exists and belongs to org
    project_result = (
        supabase.table("projects")
        .select("id, name, engagement_id")
        .eq("id", project_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )
    if not project_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    project_data = project_result.data[0]

    # Create conversation
    now = datetime.now(timezone.utc).isoformat()
    conversation_data = {
        "project_id": project_id,
        "org_id": auth.org_id,
        "subject": body.subject,
        "status": CONVERSATION_STATUS_OPEN,
        "created_at": now,
        "updated_at": now,
    }

    result = supabase.table("conversations").insert(conversation_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation",
        )

    new_conversation = result.data[0]
    return serialize_conversation(
        new_conversation,
        project=project_data,
        messages=[],
        include_messages=True,
    )


@router.get("/{project_id}/conversations/{conversation_id}")
async def retrieve_conversation(
    project_id: str,
    conversation_id: str,
    auth: AuthContext = Depends(get_current_org),
    include_internal: bool = Query(True, description="Include internal messages"),
) -> ConversationResponse:
    """Retrieve a conversation with its messages."""
    if not is_valid_uuid(project_id) or not is_valid_uuid(conversation_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get conversation
    result = (
        supabase.table("conversations")
        .select("*")
        .eq("id", conversation_id)
        .eq("project_id", project_id)
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    conversation = result.data[0]

    # Get project
    project_result = (
        supabase.table("projects")
        .select("id, name, engagement_id")
        .eq("id", project_id)
        .execute()
    )
    project_data = project_result.data[0] if project_result.data else None

    # Get messages
    messages_query = (
        supabase.table("conversation_messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .is_("deleted_at", "null")
    )

    if not include_internal:
        messages_query = messages_query.eq("is_internal", False)

    messages_query = messages_query.order("created_at", desc=False)
    messages_result = messages_query.execute()
    messages_raw = messages_result.data or []

    # Get sender info for all messages
    sender_ids = list(set(m["sender_id"] for m in messages_raw))
    senders: dict[str, dict[str, Any]] = {}

    if sender_ids:
        senders_result = (
            supabase.table("users")
            .select("id, name_f, name_l, email")
            .in_("id", sender_ids)
            .execute()
        )
        for s in (senders_result.data or []):
            senders[s["id"]] = s

    # Serialize messages
    messages = [
        serialize_message(m, sender=senders.get(m["sender_id"]))
        for m in messages_raw
    ]

    return serialize_conversation(
        conversation,
        project=project_data,
        messages=messages,
        include_messages=True,
    )


@router.put("/{project_id}/conversations/{conversation_id}")
async def update_conversation(
    project_id: str,
    conversation_id: str,
    body: ConversationUpdate,
    auth: AuthContext = Depends(get_current_org),
) -> ConversationResponse:
    """Update a conversation."""
    if not is_valid_uuid(project_id) or not is_valid_uuid(conversation_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get existing conversation
    existing_result = (
        supabase.table("conversations")
        .select("*")
        .eq("id", conversation_id)
        .eq("project_id", project_id)
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not existing_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    now = datetime.now(timezone.utc).isoformat()

    # Build update payload
    update_payload: dict[str, Any] = {"updated_at": now}

    if body.subject is not None:
        update_payload["subject"] = body.subject

    if body.status is not None:
        update_payload["status"] = body.status

    # Update
    result = (
        supabase.table("conversations")
        .update(update_payload)
        .eq("id", conversation_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update conversation",
        )

    updated = result.data[0]

    # Fetch project
    project_result = (
        supabase.table("projects")
        .select("id, name, engagement_id")
        .eq("id", project_id)
        .execute()
    )
    project_data = project_result.data[0] if project_result.data else None

    # Get messages for response
    messages_result = (
        supabase.table("conversation_messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .is_("deleted_at", "null")
        .order("created_at", desc=False)
        .execute()
    )
    messages_raw = messages_result.data or []

    sender_ids = list(set(m["sender_id"] for m in messages_raw))
    senders: dict[str, dict[str, Any]] = {}
    if sender_ids:
        senders_result = (
            supabase.table("users")
            .select("id, name_f, name_l, email")
            .in_("id", sender_ids)
            .execute()
        )
        for s in (senders_result.data or []):
            senders[s["id"]] = s

    messages = [
        serialize_message(m, sender=senders.get(m["sender_id"]))
        for m in messages_raw
    ]

    return serialize_conversation(
        updated,
        project=project_data,
        messages=messages,
        include_messages=True,
    )


@router.delete("/{project_id}/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    project_id: str,
    conversation_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> Response:
    """
    Close a conversation (sets status to Closed).

    Conversations are not deleted to preserve history.
    """
    if not is_valid_uuid(project_id) or not is_valid_uuid(conversation_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify exists
    existing = (
        supabase.table("conversations")
        .select("id")
        .eq("id", conversation_id)
        .eq("project_id", project_id)
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Close the conversation
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("conversations").update({
        "status": CONVERSATION_STATUS_CLOSED,
        "updated_at": now,
    }).eq("id", conversation_id).execute()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# =============================================================================
# Message endpoints (nested under conversations)
# =============================================================================


@router.get("/{project_id}/conversations/{conversation_id}/messages")
async def list_messages(
    project_id: str,
    conversation_id: str,
    auth: AuthContext = Depends(get_current_org),
    include_internal: bool = Query(True, description="Include internal messages"),
    limit: int = Query(50, ge=1, le=100),
    page: int = Query(1, ge=1),
) -> dict[str, Any]:
    """List messages in a conversation."""
    if not is_valid_uuid(project_id) or not is_valid_uuid(conversation_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()
    settings = get_settings()

    # Verify conversation exists and belongs to org and project
    conv_result = (
        supabase.table("conversations")
        .select("id")
        .eq("id", conversation_id)
        .eq("project_id", project_id)
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not conv_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Build query
    query = (
        supabase.table("conversation_messages")
        .select("*", count="exact")
        .eq("conversation_id", conversation_id)
        .is_("deleted_at", "null")
    )

    if not include_internal:
        query = query.eq("is_internal", False)

    query = query.order("created_at", desc=False)
    count_result = query.execute()
    total = count_result.count or 0

    # Apply pagination
    offset = (page - 1) * limit
    query = (
        supabase.table("conversation_messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .is_("deleted_at", "null")
    )
    if not include_internal:
        query = query.eq("is_internal", False)

    query = query.order("created_at", desc=False).range(offset, offset + limit - 1)
    result = query.execute()
    messages_raw = result.data or []

    # Get senders
    sender_ids = list(set(m["sender_id"] for m in messages_raw))
    senders: dict[str, dict[str, Any]] = {}
    if sender_ids:
        senders_result = (
            supabase.table("users")
            .select("id, name_f, name_l, email")
            .in_("id", sender_ids)
            .execute()
        )
        for s in (senders_result.data or []):
            senders[s["id"]] = s

    serialized = [
        serialize_message(m, sender=senders.get(m["sender_id"])).model_dump()
        for m in messages_raw
    ]

    path = f"{settings.api_base_url}/api/projects/{project_id}/conversations/{conversation_id}/messages"
    return build_pagination_response(serialized, total, page, limit, path)


@router.post("/{project_id}/conversations/{conversation_id}/messages", status_code=status.HTTP_201_CREATED)
async def create_message(
    project_id: str,
    conversation_id: str,
    body: MessageCreate,
    auth: AuthContext = Depends(get_current_org),
) -> MessageResponse:
    """Create a new message in a conversation."""
    if not is_valid_uuid(project_id) or not is_valid_uuid(conversation_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify conversation exists and belongs to org and project
    conv_result = (
        supabase.table("conversations")
        .select("id, org_id")
        .eq("id", conversation_id)
        .eq("project_id", project_id)
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not conv_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Get sender info
    sender_result = (
        supabase.table("users")
        .select("id, name_f, name_l, email")
        .eq("id", auth.user_id)
        .execute()
    )
    sender_data = sender_result.data[0] if sender_result.data else None

    # Create message
    now = datetime.now(timezone.utc).isoformat()
    attachments_data = [a.model_dump() for a in (body.attachments or [])]

    message_data = {
        "conversation_id": conversation_id,
        "org_id": auth.org_id,
        "sender_id": auth.user_id,
        "content": body.content,
        "is_internal": body.is_internal,
        "attachments": attachments_data,
        "created_at": now,
        "updated_at": now,
    }

    result = supabase.table("conversation_messages").insert(message_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create message",
        )

    # Update conversation last_message_at
    supabase.table("conversations").update({
        "last_message_at": now,
        "updated_at": now,
    }).eq("id", conversation_id).execute()

    new_message = result.data[0]
    return serialize_message(new_message, sender=sender_data)


@router.delete("/{project_id}/conversations/{conversation_id}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    project_id: str,
    conversation_id: str,
    message_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> Response:
    """Soft delete a message."""
    if not is_valid_uuid(project_id) or not is_valid_uuid(conversation_id) or not is_valid_uuid(message_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify conversation belongs to org and project
    conv_result = (
        supabase.table("conversations")
        .select("id")
        .eq("id", conversation_id)
        .eq("project_id", project_id)
        .eq("org_id", auth.org_id)
        .execute()
    )

    if not conv_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Verify message exists
    msg_result = (
        supabase.table("conversation_messages")
        .select("id")
        .eq("id", message_id)
        .eq("conversation_id", conversation_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not msg_result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Soft delete
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("conversation_messages").update({
        "deleted_at": now,
        "updated_at": now,
    }).eq("id", message_id).execute()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
