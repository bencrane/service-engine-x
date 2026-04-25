"""Internal API endpoints for meetings/deals and Cal.com org resolution."""

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.auth import verify_token_or_internal_bearer
from app.config import settings
from app.database import get_supabase
from app.services.calcom_client import CalcomClient, CalcomClientError, CalcomNotFoundError

router = APIRouter(prefix="/api/internal", tags=["Internal Meetings & Deals"])

MEETING_STATUSES = {
    "pending",
    "scheduled",
    "in_progress",
    "completed",
    "cancelled",
    "rejected",
    "no_show",
    "rescheduled",
}

DEAL_STATUSES = {"qualified", "proposal_sent", "negotiating", "won", "lost"}


class CalAttendee(BaseModel):
    """Attendee payload from Cal.com event context."""

    name: str = Field(default="")
    email: str


class MeetingFromCalEventRequest(BaseModel):
    """Create or retrieve a meeting based on Cal.com event payload."""

    attendees: list[CalAttendee] = Field(default_factory=list)
    cal_event_uid: str | None = None
    cal_booking_id: int | None = None
    title: str
    start_time: datetime
    end_time: datetime
    organizer_email: str | None = None
    status: str = "scheduled"
    rescheduled_from_uid: str | None = None
    notes: str | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)


class MeetingUpdateRequest(BaseModel):
    """Internal meeting updates driven by orchestrators/webhooks."""

    status: str | None = None
    deal_id: str | None = None
    notes: str | None = None
    recording_url: str | None = None
    transcript_url: str | None = None
    host_no_show: bool | None = None
    guest_no_show: bool | None = None
    custom_fields: dict[str, Any] | None = None
    cancellation_reason: str | None = None


class DealCreateRequest(BaseModel):
    """Create a deal from an existing meeting."""

    meeting_id: str
    title: str
    value: float | None = None
    source: str = "cal_com"
    notes: str | None = None
    referred_by_account_id: str | None = None


class DealUpdateRequest(BaseModel):
    """Update deal state and metadata."""

    title: str | None = None
    status: str | None = None
    value: float | None = None
    source: str | None = None
    notes: str | None = None
    lost_reason: str | None = None


class DealProposalLinkRequest(BaseModel):
    """Link a proposal to a deal."""

    proposal_id: str


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _split_name(raw_name: str) -> tuple[str, str]:
    """Split full name into first + last while preserving multi-word last names."""
    cleaned = " ".join(raw_name.strip().split())
    if not cleaned:
        return "", ""
    if " " not in cleaned:
        return cleaned, ""
    first, rest = cleaned.split(" ", 1)
    return first, rest


def _email_domain(email: str) -> str | None:
    parts = email.lower().strip().split("@")
    if len(parts) != 2 or not parts[1]:
        return None
    return parts[1]


def _extract_cal_team_id(event_type_payload: dict[str, Any]) -> int | None:
    """Extract team ID from variable Cal.com event type response shapes."""
    data = event_type_payload.get("data", {})

    if isinstance(data.get("teamId"), int):
        return data["teamId"]
    if isinstance(data.get("team_id"), int):
        return data["team_id"]

    team_obj = data.get("team")
    if isinstance(team_obj, dict) and isinstance(team_obj.get("id"), int):
        return team_obj["id"]

    parent_obj = data.get("parent")
    if isinstance(parent_obj, dict) and isinstance(parent_obj.get("teamId"), int):
        return parent_obj["teamId"]

    return None


def _get_existing_meeting_context(
    supabase: Any,
    org_id: str,
    meeting: dict[str, Any],
) -> dict[str, Any]:
    """Build agent-friendly context payload for an existing meeting."""
    account = None
    contacts: list[dict[str, Any]] = []
    existing_deals: list[dict[str, Any]] = []
    linked_deal = None

    if meeting.get("account_id"):
        account_result = (
            supabase.table("accounts")
            .select("*")
            .eq("id", meeting["account_id"])
            .eq("org_id", org_id)
            .is_("deleted_at", "null")
            .limit(1)
            .execute()
        )
        account = account_result.data[0] if account_result.data else None

        deals_result = (
            supabase.table("deals")
            .select("*")
            .eq("org_id", org_id)
            .eq("account_id", meeting["account_id"])
            .is_("deleted_at", "null")
            .order("created_at", desc=True)
            .execute()
        )
        existing_deals = deals_result.data or []

    attendee_emails = meeting.get("attendee_emails") or []
    if attendee_emails:
        contacts_result = (
            supabase.table("contacts")
            .select("*")
            .eq("org_id", org_id)
            .is_("deleted_at", "null")
            .in_("email", attendee_emails)
            .execute()
        )
        contacts = contacts_result.data or []

    if meeting.get("deal_id"):
        linked_deal_result = (
            supabase.table("deals")
            .select("*")
            .eq("id", meeting["deal_id"])
            .eq("org_id", org_id)
            .is_("deleted_at", "null")
            .limit(1)
            .execute()
        )
        linked_deal = linked_deal_result.data[0] if linked_deal_result.data else None

    return {
        "meeting": meeting,
        "account": account,
        "contacts": contacts,
        "existing_deals": existing_deals,
        "linked_deal": linked_deal,
        "created": False,
        "warnings": [],
    }


@router.get("/resolve-org", dependencies=[Depends(verify_token_or_internal_bearer)])
async def resolve_org_from_event_type(event_type_id: int = Query(..., ge=1)) -> dict[str, Any]:
    """Resolve SERX org context from a Cal.com event type."""
    if not settings.CAL_API_KEY:
        raise HTTPException(status_code=503, detail="CAL_API_KEY is not configured")

    supabase = get_supabase()
    ttl_seconds = max(settings.CALCOM_EVENT_TYPE_CACHE_TTL_SECONDS, 60)
    cutoff = datetime.now(UTC) - timedelta(seconds=ttl_seconds)

    cached_result = (
        supabase.table("cal_event_type_cache")
        .select("*")
        .eq("event_type_id", event_type_id)
        .limit(1)
        .execute()
    )

    cached = cached_result.data[0] if cached_result.data else None
    if cached and cached.get("refreshed_at"):
        refreshed = datetime.fromisoformat(cached["refreshed_at"].replace("Z", "+00:00"))
        if refreshed >= cutoff:
            org_result = (
                supabase.table("organizations")
                .select("id, name, slug, domain")
                .eq("id", cached["org_id"])
                .limit(1)
                .execute()
            )
            if org_result.data:
                return {
                    "event_type_id": event_type_id,
                    "cal_team_id": cached["cal_team_id"],
                    "org": org_result.data[0],
                    "from_cache": True,
                    "cache_refreshed_at": cached["refreshed_at"],
                }

    client = CalcomClient(
        api_key=settings.CAL_API_KEY,
        base_url=settings.CALCOM_BASE_URL,
        api_version=settings.CALCOM_API_VERSION,
    )

    try:
        event_type = await client.get_event_type(event_type_id)
    except CalcomNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CalcomClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    cal_team_id = _extract_cal_team_id(event_type)
    if cal_team_id is None:
        raise HTTPException(
            status_code=422,
            detail="Event type did not include a team context; cannot resolve organization.",
        )

    mapping_result = (
        supabase.table("cal_team_mappings")
        .select("org_id, cal_team_id")
        .eq("cal_team_id", cal_team_id)
        .eq("is_active", True)
        .limit(1)
        .execute()
    )
    if not mapping_result.data:
        raise HTTPException(status_code=404, detail="No Cal team mapping found for event type team")

    mapping = mapping_result.data[0]
    now_iso = _now_iso()
    data_obj = event_type.get("data", {})
    supabase.table("cal_event_type_cache").upsert(
        {
            "event_type_id": event_type_id,
            "org_id": mapping["org_id"],
            "cal_team_id": cal_team_id,
            "event_type_slug": data_obj.get("slug"),
            "event_type_title": data_obj.get("title"),
            "raw_response": event_type,
            "refreshed_at": now_iso,
            "updated_at": now_iso,
        },
        on_conflict="event_type_id",
    ).execute()

    org_result = (
        supabase.table("organizations")
        .select("id, name, slug, domain")
        .eq("id", mapping["org_id"])
        .limit(1)
        .execute()
    )
    if not org_result.data:
        raise HTTPException(status_code=404, detail="Mapped organization no longer exists")

    return {
        "event_type_id": event_type_id,
        "cal_team_id": cal_team_id,
        "org": org_result.data[0],
        "from_cache": False,
        "cache_refreshed_at": now_iso,
    }


@router.get("/resolve-org-from-team", dependencies=[Depends(verify_token_or_internal_bearer)])
async def resolve_org_from_team(cal_team_id: int = Query(..., ge=1)) -> dict[str, Any]:
    """Resolve SERX org context directly from a Cal.com team ID."""
    supabase = get_supabase()

    mapping_result = (
        supabase.table("cal_team_mappings")
        .select("*")
        .eq("cal_team_id", cal_team_id)
        .eq("is_active", True)
        .limit(1)
        .execute()
    )
    if not mapping_result.data:
        raise HTTPException(status_code=404, detail="No active Cal team mapping found for this team ID")

    mapping = mapping_result.data[0]

    org_result = (
        supabase.table("organizations")
        .select("id, name, slug, domain")
        .eq("id", mapping["org_id"])
        .limit(1)
        .execute()
    )
    if not org_result.data:
        raise HTTPException(status_code=404, detail="Mapped organization no longer exists")

    return {
        "cal_team_id": cal_team_id,
        "org": org_result.data[0],
        "mapping": mapping,
    }


@router.post("/orgs/{org_id}/meetings/from-cal-event", dependencies=[Depends(verify_token_or_internal_bearer)])
async def create_meeting_from_cal_event(org_id: str, body: MeetingFromCalEventRequest) -> dict[str, Any]:
    """Create (or de-duplicate) a meeting from Cal.com booking payload data."""
    if body.status not in MEETING_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid meeting status")

    supabase = get_supabase()
    warnings: list[str] = []

    org_result = supabase.table("organizations").select("id").eq("id", org_id).limit(1).execute()
    if not org_result.data:
        raise HTTPException(status_code=404, detail="Organization not found")

    if body.cal_event_uid:
        existing_uid = (
            supabase.table("meetings")
            .select("*")
            .eq("org_id", org_id)
            .eq("cal_event_uid", body.cal_event_uid)
            .limit(1)
            .execute()
        )
        if existing_uid.data:
            return _get_existing_meeting_context(supabase, org_id, existing_uid.data[0])

    if body.cal_booking_id is not None:
        existing_booking = (
            supabase.table("meetings")
            .select("*")
            .eq("org_id", org_id)
            .eq("cal_booking_id", body.cal_booking_id)
            .limit(1)
            .execute()
        )
        if existing_booking.data:
            return _get_existing_meeting_context(supabase, org_id, existing_booking.data[0])

    attendees = [
        {"name": att.name.strip(), "email": att.email.lower().strip()}
        for att in body.attendees
        if att.email.strip()
    ]
    attendee_emails = [att["email"] for att in attendees]

    contacts_by_email: dict[str, dict[str, Any]] = {}
    accounts_by_domain: dict[str, dict[str, Any]] = {}

    for attendee in attendees:
        domain = _email_domain(attendee["email"])
        account: dict[str, Any] | None = None
        if domain:
            if domain in accounts_by_domain:
                account = accounts_by_domain[domain]
            else:
                account_result = (
                    supabase.table("accounts")
                    .select("*")
                    .eq("org_id", org_id)
                    .eq("domain", domain)
                    .is_("deleted_at", "null")
                    .limit(1)
                    .execute()
                )
                if account_result.data:
                    account = account_result.data[0]
                else:
                    now_iso = _now_iso()
                    created_account = (
                        supabase.table("accounts")
                        .insert(
                            {
                                "org_id": org_id,
                                "name": domain,
                                "domain": domain,
                                "lifecycle": "lead",
                                "source": "cal_com",
                                "created_at": now_iso,
                                "updated_at": now_iso,
                            }
                        )
                        .execute()
                    )
                    if not created_account.data:
                        raise HTTPException(status_code=500, detail="Failed to create account")
                    account = created_account.data[0]
                accounts_by_domain[domain] = account

        first, last = _split_name(attendee["name"])
        contact_result = (
            supabase.table("contacts")
            .select("*")
            .eq("org_id", org_id)
            .eq("email", attendee["email"])
            .is_("deleted_at", "null")
            .limit(1)
            .execute()
        )
        if contact_result.data:
            contact = contact_result.data[0]
            if not contact.get("account_id") and account:
                updated = (
                    supabase.table("contacts")
                    .update({"account_id": account["id"], "updated_at": _now_iso()})
                    .eq("id", contact["id"])
                    .execute()
                )
                if updated.data:
                    contact = updated.data[0]
        else:
            now_iso = _now_iso()
            created_contact = (
                supabase.table("contacts")
                .insert(
                    {
                        "org_id": org_id,
                        "account_id": account["id"] if account else None,
                        "name_f": first,
                        "name_l": last,
                        "email": attendee["email"],
                        "created_at": now_iso,
                        "updated_at": now_iso,
                    }
                )
                .execute()
            )
            if not created_contact.data:
                raise HTTPException(status_code=500, detail="Failed to create contact")
            contact = created_contact.data[0]

        contacts_by_email[attendee["email"]] = contact

    old_meeting = None
    if body.rescheduled_from_uid:
        old_result = (
            supabase.table("meetings")
            .select("*")
            .eq("org_id", org_id)
            .eq("cal_event_uid", body.rescheduled_from_uid)
            .limit(1)
            .execute()
        )
        if old_result.data:
            old_meeting = old_result.data[0]
            supabase.table("meetings").update(
                {"status": "rescheduled", "updated_at": _now_iso()}
            ).eq("id", old_meeting["id"]).execute()
        else:
            warnings.append("rescheduled_from_uid did not match any existing meeting")

    primary_contact = contacts_by_email.get(attendee_emails[0]) if attendee_emails else None
    primary_account = None
    if primary_contact and primary_contact.get("account_id"):
        primary_account_result = (
            supabase.table("accounts")
            .select("*")
            .eq("id", primary_contact["account_id"])
            .eq("org_id", org_id)
            .is_("deleted_at", "null")
            .limit(1)
            .execute()
        )
        if primary_account_result.data:
            primary_account = primary_account_result.data[0]

    account_id = old_meeting["account_id"] if old_meeting else (primary_account["id"] if primary_account else None)
    contact_id = old_meeting["contact_id"] if old_meeting else (primary_contact["id"] if primary_contact else None)
    deal_id = old_meeting["deal_id"] if old_meeting else None

    meeting_result = (
        supabase.table("meetings")
        .insert(
            {
                "org_id": org_id,
                "account_id": account_id,
                "contact_id": contact_id,
                "deal_id": deal_id,
                "cal_event_uid": body.cal_event_uid,
                "cal_booking_id": body.cal_booking_id,
                "title": body.title.strip(),
                "start_time": body.start_time.isoformat(),
                "end_time": body.end_time.isoformat(),
                "status": body.status,
                "organizer_email": body.organizer_email.lower().strip()
                if body.organizer_email
                else None,
                "attendee_emails": attendee_emails,
                "notes": body.notes,
                "custom_fields": body.custom_fields or {},
                "updated_at": _now_iso(),
            }
        )
        .execute()
    )

    if not meeting_result.data:
        raise HTTPException(status_code=500, detail="Failed to create meeting")

    meeting = meeting_result.data[0]

    account = None
    if meeting.get("account_id"):
        account_result = (
            supabase.table("accounts")
            .select("*")
            .eq("id", meeting["account_id"])
            .eq("org_id", org_id)
            .is_("deleted_at", "null")
            .limit(1)
            .execute()
        )
        account = account_result.data[0] if account_result.data else None

    existing_deals: list[dict[str, Any]] = []
    linked_deal = None
    if account:
        deals_result = (
            supabase.table("deals")
            .select("*")
            .eq("org_id", org_id)
            .eq("account_id", account["id"])
            .is_("deleted_at", "null")
            .order("created_at", desc=True)
            .execute()
        )
        existing_deals = deals_result.data or []

    if meeting.get("deal_id"):
        linked_result = (
            supabase.table("deals")
            .select("*")
            .eq("id", meeting["deal_id"])
            .eq("org_id", org_id)
            .is_("deleted_at", "null")
            .limit(1)
            .execute()
        )
        linked_deal = linked_result.data[0] if linked_result.data else None

    return {
        "meeting": meeting,
        "account": account,
        "contacts": list(contacts_by_email.values()),
        "existing_deals": existing_deals,
        "linked_deal": linked_deal,
        "rescheduled_from": old_meeting,
        "created": True,
        "warnings": warnings,
    }


@router.put("/orgs/{org_id}/meetings/{meeting_id}", dependencies=[Depends(verify_token_or_internal_bearer)])
async def update_meeting(org_id: str, meeting_id: str, body: MeetingUpdateRequest) -> dict[str, Any]:
    """Update meeting status/links/notes for internal orchestration."""
    supabase = get_supabase()

    existing = (
        supabase.table("meetings")
        .select("*")
        .eq("id", meeting_id)
        .eq("org_id", org_id)
        .limit(1)
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Meeting not found")

    update_payload: dict[str, Any] = {"updated_at": _now_iso()}
    if body.status is not None:
        if body.status not in MEETING_STATUSES:
            raise HTTPException(status_code=422, detail="Invalid meeting status")
        update_payload["status"] = body.status
    if body.deal_id is not None:
        if body.deal_id:
            deal_result = (
                supabase.table("deals")
                .select("id")
                .eq("id", body.deal_id)
                .eq("org_id", org_id)
                .is_("deleted_at", "null")
                .limit(1)
                .execute()
            )
            if not deal_result.data:
                raise HTTPException(status_code=404, detail="Deal not found")
            update_payload["deal_id"] = body.deal_id
        else:
            update_payload["deal_id"] = None
    if body.notes is not None:
        update_payload["notes"] = body.notes
    if body.recording_url is not None:
        update_payload["recording_url"] = body.recording_url
    if body.transcript_url is not None:
        update_payload["transcript_url"] = body.transcript_url
    if body.host_no_show is not None:
        update_payload["host_no_show"] = body.host_no_show
    if body.guest_no_show is not None:
        update_payload["guest_no_show"] = body.guest_no_show
    if body.custom_fields is not None:
        update_payload["custom_fields"] = body.custom_fields
    if body.cancellation_reason is not None:
        update_payload["cancellation_reason"] = body.cancellation_reason

    result = supabase.table("meetings").update(update_payload).eq("id", meeting_id).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update meeting")
    return result.data[0]


@router.get(
    "/orgs/{org_id}/meetings/by-cal-uid/{cal_event_uid}",
    dependencies=[Depends(verify_token_or_internal_bearer)],
)
async def get_meeting_by_cal_uid(org_id: str, cal_event_uid: str) -> dict[str, Any]:
    """Find a meeting by Cal.com event UID."""
    supabase = get_supabase()
    result = (
        supabase.table("meetings")
        .select("*")
        .eq("org_id", org_id)
        .eq("cal_event_uid", cal_event_uid)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return result.data[0]


@router.get(
    "/orgs/{org_id}/meetings/by-cal-booking-id/{cal_booking_id}",
    dependencies=[Depends(verify_token_or_internal_bearer)],
)
async def get_meeting_by_cal_booking_id(org_id: str, cal_booking_id: int) -> dict[str, Any]:
    """Find a meeting by Cal.com numeric booking ID."""
    supabase = get_supabase()
    result = (
        supabase.table("meetings")
        .select("*")
        .eq("org_id", org_id)
        .eq("cal_booking_id", cal_booking_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return result.data[0]


@router.post("/orgs/{org_id}/deals", dependencies=[Depends(verify_token_or_internal_bearer)])
async def create_deal_from_meeting(org_id: str, body: DealCreateRequest) -> dict[str, Any]:
    """Create a deal from a qualified meeting and link meeting.deal_id."""
    supabase = get_supabase()

    meeting_result = (
        supabase.table("meetings")
        .select("*")
        .eq("id", body.meeting_id)
        .eq("org_id", org_id)
        .limit(1)
        .execute()
    )
    if not meeting_result.data:
        raise HTTPException(status_code=404, detail="Meeting not found")
    meeting = meeting_result.data[0]

    if meeting.get("deal_id"):
        raise HTTPException(status_code=409, detail="Meeting is already linked to a deal")

    if body.referred_by_account_id:
        referral_result = (
            supabase.table("accounts")
            .select("id")
            .eq("id", body.referred_by_account_id)
            .eq("org_id", org_id)
            .is_("deleted_at", "null")
            .limit(1)
            .execute()
        )
        if not referral_result.data:
            raise HTTPException(status_code=404, detail="Referred-by account not found")

    now_iso = _now_iso()
    deal_insert = {
        "org_id": org_id,
        "account_id": meeting.get("account_id"),
        "contact_id": meeting.get("contact_id"),
        "title": body.title.strip(),
        "status": "qualified",
        "value": body.value,
        "source": body.source,
        "notes": body.notes,
        "referred_by_account_id": body.referred_by_account_id,
        "created_at": now_iso,
        "updated_at": now_iso,
    }
    deal_result = supabase.table("deals").insert(deal_insert).execute()
    if not deal_result.data:
        raise HTTPException(status_code=500, detail="Failed to create deal")
    deal = deal_result.data[0]

    updated_meeting_result = (
        supabase.table("meetings")
        .update({"deal_id": deal["id"], "updated_at": _now_iso()})
        .eq("id", meeting["id"])
        .execute()
    )
    updated_meeting = updated_meeting_result.data[0] if updated_meeting_result.data else meeting

    return {
        "deal": deal,
        "meeting": updated_meeting,
    }


def _build_deal_context(supabase: Any, org_id: str, deal: dict[str, Any]) -> dict[str, Any]:
    """Build full, agent-ready deal context payload."""
    account = None
    contact = None
    proposal = None
    meetings: list[dict[str, Any]] = []
    account_meetings: list[dict[str, Any]] = []

    if deal.get("account_id"):
        account_result = (
            supabase.table("accounts")
            .select("*")
            .eq("id", deal["account_id"])
            .eq("org_id", org_id)
            .is_("deleted_at", "null")
            .limit(1)
            .execute()
        )
        account = account_result.data[0] if account_result.data else None

    if deal.get("contact_id"):
        contact_result = (
            supabase.table("contacts")
            .select("*")
            .eq("id", deal["contact_id"])
            .eq("org_id", org_id)
            .is_("deleted_at", "null")
            .limit(1)
            .execute()
        )
        contact = contact_result.data[0] if contact_result.data else None

    if deal.get("proposal_id"):
        proposal_result = (
            supabase.table("proposals")
            .select("*")
            .eq("id", deal["proposal_id"])
            .eq("org_id", org_id)
            .is_("deleted_at", "null")
            .limit(1)
            .execute()
        )
        proposal = proposal_result.data[0] if proposal_result.data else None

    meetings_result = (
        supabase.table("meetings")
        .select("*")
        .eq("org_id", org_id)
        .eq("deal_id", deal["id"])
        .order("start_time", desc=True)
        .execute()
    )
    meetings = meetings_result.data or []

    if deal.get("account_id"):
        all_account_meetings = (
            supabase.table("meetings")
            .select("*")
            .eq("org_id", org_id)
            .eq("account_id", deal["account_id"])
            .order("start_time", desc=True)
            .execute()
        )
        account_meetings = all_account_meetings.data or []

    return {
        "deal": deal,
        "account": account,
        "contact": contact,
        "proposal": proposal,
        "meetings": meetings,
        "account_meetings": account_meetings,
    }


@router.get("/orgs/{org_id}/deals/{deal_id}", dependencies=[Depends(verify_token_or_internal_bearer)])
async def get_deal(org_id: str, deal_id: str) -> dict[str, Any]:
    """Get deal with rich related context for downstream agents."""
    supabase = get_supabase()
    deal_result = (
        supabase.table("deals")
        .select("*")
        .eq("id", deal_id)
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .limit(1)
        .execute()
    )
    if not deal_result.data:
        raise HTTPException(status_code=404, detail="Deal not found")
    return _build_deal_context(supabase, org_id, deal_result.data[0])


@router.put("/orgs/{org_id}/deals/{deal_id}", dependencies=[Depends(verify_token_or_internal_bearer)])
async def update_deal(org_id: str, deal_id: str, body: DealUpdateRequest) -> dict[str, Any]:
    """Update deal fields and enforce lifecycle transitions."""
    supabase = get_supabase()
    deal_result = (
        supabase.table("deals")
        .select("*")
        .eq("id", deal_id)
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .limit(1)
        .execute()
    )
    if not deal_result.data:
        raise HTTPException(status_code=404, detail="Deal not found")
    existing = deal_result.data[0]

    update_payload: dict[str, Any] = {"updated_at": _now_iso()}
    if body.title is not None:
        update_payload["title"] = body.title.strip()
    if body.status is not None:
        if body.status not in DEAL_STATUSES:
            raise HTTPException(status_code=422, detail="Invalid deal status")
        if body.status == "lost" and not (body.lost_reason or existing.get("lost_reason")):
            raise HTTPException(status_code=422, detail="lost_reason is required when status is lost")
        update_payload["status"] = body.status
        if body.status in {"won", "lost"}:
            update_payload["closed_at"] = _now_iso()
    if body.value is not None:
        update_payload["value"] = body.value
    if body.source is not None:
        update_payload["source"] = body.source
    if body.notes is not None:
        update_payload["notes"] = body.notes
    if body.lost_reason is not None:
        update_payload["lost_reason"] = body.lost_reason

    updated_result = supabase.table("deals").update(update_payload).eq("id", deal_id).execute()
    if not updated_result.data:
        raise HTTPException(status_code=500, detail="Failed to update deal")
    updated_deal = updated_result.data[0]

    if updated_deal.get("status") == "won" and updated_deal.get("account_id"):
        supabase.table("accounts").update(
            {"lifecycle": "active", "updated_at": _now_iso()}
        ).eq("id", updated_deal["account_id"]).eq("org_id", org_id).execute()

    return _build_deal_context(supabase, org_id, updated_deal)


@router.put(
    "/orgs/{org_id}/deals/{deal_id}/proposal",
    dependencies=[Depends(verify_token_or_internal_bearer)],
)
async def link_proposal_to_deal(
    org_id: str,
    deal_id: str,
    body: DealProposalLinkRequest,
) -> dict[str, Any]:
    """Link a proposal to a deal and move status to proposal_sent."""
    supabase = get_supabase()

    deal_result = (
        supabase.table("deals")
        .select("*")
        .eq("id", deal_id)
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .limit(1)
        .execute()
    )
    if not deal_result.data:
        raise HTTPException(status_code=404, detail="Deal not found")

    proposal_result = (
        supabase.table("proposals")
        .select("id")
        .eq("id", body.proposal_id)
        .eq("org_id", org_id)
        .is_("deleted_at", "null")
        .limit(1)
        .execute()
    )
    if not proposal_result.data:
        raise HTTPException(status_code=404, detail="Proposal not found")

    updated_result = (
        supabase.table("deals")
        .update(
            {
                "proposal_id": body.proposal_id,
                "status": "proposal_sent",
                "updated_at": _now_iso(),
            }
        )
        .eq("id", deal_id)
        .execute()
    )
    if not updated_result.data:
        raise HTTPException(status_code=500, detail="Failed to link proposal")

    return _build_deal_context(supabase, org_id, updated_result.data[0])
