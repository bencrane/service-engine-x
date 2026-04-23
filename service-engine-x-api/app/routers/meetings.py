"""Meetings API router."""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from app.auth import AuthContext, get_current_auth
from app.config import settings
from app.database import get_supabase
from app.models.meetings import (
    UPCOMING_MEETING_STATUSES,
    VALID_MEETING_STATUSES,
    AccountSummary,
    ContactSummary,
    DealSummary,
    MeetingListResponse,
    MeetingResponse,
)
from app.utils import build_pagination_response, format_currency_optional, is_valid_uuid

router = APIRouter(prefix="/api/meetings", tags=["Meetings"])


VALID_SORT_FIELDS = {"start_time", "created_at", "updated_at", "status"}


def _serialize_account(account: dict[str, Any] | None) -> AccountSummary | None:
    if not account:
        return None
    return AccountSummary(
        id=account["id"],
        name=account["name"],
        lifecycle=account.get("lifecycle"),
    )


def _serialize_contact(contact: dict[str, Any] | None) -> ContactSummary | None:
    if not contact:
        return None
    first = contact.get("name_f") or ""
    last = contact.get("name_l") or ""
    full = f"{first} {last}".strip() or contact.get("email") or contact["id"]
    return ContactSummary(id=contact["id"], name=full, email=contact.get("email"))


def _serialize_deal(deal: dict[str, Any] | None) -> DealSummary | None:
    if not deal:
        return None
    return DealSummary(
        id=deal["id"],
        name=deal.get("name"),
        stage=deal.get("stage"),
        amount=format_currency_optional(deal.get("amount")),
    )


def _base_meeting_dict(row: dict[str, Any]) -> dict[str, Any]:
    account = row.get("account")
    if isinstance(account, list):
        account = account[0] if account else None
    contact = row.get("contact")
    if isinstance(contact, list):
        contact = contact[0] if contact else None
    deal = row.get("deal")
    if isinstance(deal, list):
        deal = deal[0] if deal else None

    attendee_emails = row.get("attendee_emails") or []
    if not isinstance(attendee_emails, list):
        attendee_emails = []

    return {
        "id": row["id"],
        "org_id": row["org_id"],
        "account_id": row.get("account_id"),
        "contact_id": row.get("contact_id"),
        "deal_id": row.get("deal_id"),
        "cal_event_uid": row.get("cal_event_uid"),
        "cal_booking_id": row.get("cal_booking_id"),
        "title": row["title"],
        "start_time": row["start_time"],
        "end_time": row["end_time"],
        "status": row.get("status", "scheduled"),
        "organizer_email": row.get("organizer_email"),
        "attendee_emails": attendee_emails,
        "host_no_show": bool(row.get("host_no_show", False)),
        "guest_no_show": bool(row.get("guest_no_show", False)),
        "account": _serialize_account(account),
        "contact": _serialize_contact(contact),
        "deal": _serialize_deal(deal),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def serialize_meeting_list(row: dict[str, Any]) -> MeetingListResponse:
    return MeetingListResponse(**_base_meeting_dict(row))


def serialize_meeting(row: dict[str, Any]) -> MeetingResponse:
    base = _base_meeting_dict(row)
    base.update(
        {
            "cancellation_reason": row.get("cancellation_reason"),
            "custom_fields": row.get("custom_fields") or {},
            "notes": row.get("notes"),
            "recording_url": row.get("recording_url"),
            "transcript_url": row.get("transcript_url"),
        }
    )
    return MeetingResponse(**base)


_SELECT_WITH_RELATIONS = (
    "*, "
    "account:accounts(id, name, lifecycle), "
    "contact:contacts(id, name_f, name_l, email), "
    "deal:deals(id, name, stage, amount)"
)


def _apply_filters(
    query: Any,
    *,
    status_filter: str | None,
    statuses_in: tuple[str, ...] | None,
    start_after: datetime | None,
    start_before: datetime | None,
    account_id: str | None,
    contact_id: str | None,
    deal_id: str | None,
) -> Any:
    if status_filter is not None:
        query = query.eq("status", status_filter)
    if statuses_in is not None:
        query = query.in_("status", list(statuses_in))
    if start_after is not None:
        query = query.gte("start_time", start_after.isoformat())
    if start_before is not None:
        query = query.lte("start_time", start_before.isoformat())
    if account_id is not None:
        query = query.eq("account_id", account_id)
    if contact_id is not None:
        query = query.eq("contact_id", contact_id)
    if deal_id is not None:
        query = query.eq("deal_id", deal_id)
    return query


@router.get("")
async def list_meetings(
    request: Request,
    auth: AuthContext = Depends(get_current_auth),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    sort: str = Query("start_time:desc"),
    status_filter: str | None = Query(
        None, alias="status", description="Filter by meeting status"
    ),
    start_after: datetime | None = Query(
        None, description="Only meetings with start_time >= this ISO timestamp"
    ),
    start_before: datetime | None = Query(
        None, description="Only meetings with start_time <= this ISO timestamp"
    ),
    account_id: str | None = Query(None),
    contact_id: str | None = Query(None),
    deal_id: str | None = Query(None),
) -> dict[str, Any]:
    """List meetings for the authenticated organization with filters."""
    supabase = get_supabase()

    if status_filter is not None and status_filter not in VALID_MEETING_STATUSES:
        return JSONResponse(
            status_code=400,
            content={
                "message": "The given data was invalid.",
                "errors": {"status": [f"Must be one of {sorted(VALID_MEETING_STATUSES)}"]},
            },
        )

    for field_name, value in (
        ("account_id", account_id),
        ("contact_id", contact_id),
        ("deal_id", deal_id),
    ):
        if value is not None and not is_valid_uuid(value):
            return JSONResponse(
                status_code=400,
                content={
                    "message": "The given data was invalid.",
                    "errors": {field_name: ["Invalid UUID"]},
                },
            )

    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if sort_parts else "start_time"
    sort_dir = sort_parts[1] if len(sort_parts) > 1 else "desc"
    if sort_field not in VALID_SORT_FIELDS:
        sort_field = "start_time"
    ascending = sort_dir == "asc"

    count_query = (
        supabase.table("meetings")
        .select("id", count="exact")
        .eq("org_id", auth.org_id)
    )
    count_query = _apply_filters(
        count_query,
        status_filter=status_filter,
        statuses_in=None,
        start_after=start_after,
        start_before=start_before,
        account_id=account_id,
        contact_id=contact_id,
        deal_id=deal_id,
    )
    count_result = count_query.execute()
    total = count_result.count or 0

    offset = (page - 1) * limit
    data_query = (
        supabase.table("meetings")
        .select(_SELECT_WITH_RELATIONS)
        .eq("org_id", auth.org_id)
    )
    data_query = _apply_filters(
        data_query,
        status_filter=status_filter,
        statuses_in=None,
        start_after=start_after,
        start_before=start_before,
        account_id=account_id,
        contact_id=contact_id,
        deal_id=deal_id,
    )
    data_query = data_query.order(sort_field, desc=not ascending).range(
        offset, offset + limit - 1
    )
    result = data_query.execute()
    rows = result.data or []

    serialized = [serialize_meeting_list(row).model_dump() for row in rows]
    path = f"{settings.API_BASE_URL}/api/meetings"
    return build_pagination_response(serialized, total, page, limit, path)


@router.get("/upcoming")
async def list_upcoming_meetings(
    auth: AuthContext = Depends(get_current_auth),
    within_hours: int | None = Query(
        None, ge=1, le=24 * 365, description="Upcoming meetings within N hours"
    ),
    within_days: int | None = Query(
        None, ge=1, le=365, description="Upcoming meetings within N days (default 30)"
    ),
    limit: int = Query(100, ge=1, le=500),
    account_id: str | None = Query(None),
    contact_id: str | None = Query(None),
    deal_id: str | None = Query(None),
) -> dict[str, Any]:
    """High-level convenience endpoint: upcoming scheduled/pending meetings.

    Defaults to the next 30 days when neither `within_hours` nor `within_days` is
    given. Exactly one of the two windows may be provided.
    """
    if within_hours is not None and within_days is not None:
        return JSONResponse(
            status_code=400,
            content={
                "message": "The given data was invalid.",
                "errors": {"within_hours": ["Provide only one of within_hours or within_days"]},
            },
        )

    for field_name, value in (
        ("account_id", account_id),
        ("contact_id", contact_id),
        ("deal_id", deal_id),
    ):
        if value is not None and not is_valid_uuid(value):
            return JSONResponse(
                status_code=400,
                content={
                    "message": "The given data was invalid.",
                    "errors": {field_name: ["Invalid UUID"]},
                },
            )

    now = datetime.now(timezone.utc)
    if within_hours is not None:
        window_end = now + timedelta(hours=within_hours)
        window_label = f"{within_hours}h"
    else:
        days = within_days if within_days is not None else 30
        window_end = now + timedelta(days=days)
        window_label = f"{days}d"

    supabase = get_supabase()
    query = (
        supabase.table("meetings")
        .select(_SELECT_WITH_RELATIONS)
        .eq("org_id", auth.org_id)
    )
    query = _apply_filters(
        query,
        status_filter=None,
        statuses_in=UPCOMING_MEETING_STATUSES,
        start_after=now,
        start_before=window_end,
        account_id=account_id,
        contact_id=contact_id,
        deal_id=deal_id,
    )
    query = query.order("start_time", desc=False).limit(limit)
    result = query.execute()
    rows = result.data or []

    return {
        "window": {
            "from": now.isoformat(),
            "to": window_end.isoformat(),
            "label": window_label,
        },
        "count": len(rows),
        "data": [serialize_meeting_list(row).model_dump() for row in rows],
    }


@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: str,
    auth: AuthContext = Depends(get_current_auth),
) -> MeetingResponse:
    """Fetch a single meeting by id, scoped to the caller's organization."""
    if not is_valid_uuid(meeting_id):
        raise HTTPException(status_code=400, detail="Invalid meeting_id format")

    supabase = get_supabase()
    result = (
        supabase.table("meetings")
        .select(_SELECT_WITH_RELATIONS)
        .eq("id", meeting_id)
        .eq("org_id", auth.org_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return serialize_meeting(result.data[0])
