"""Internal API endpoints for Cal.com webhook normalization tables."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.config import settings
from app.database import get_supabase

router = APIRouter(prefix="/api/internal/cal", tags=["Internal Cal.com"])


BOOKING_EVENT_TYPES = {
    "BOOKING_CREATED",
    "BOOKING_REQUESTED",
    "BOOKING_RESCHEDULED",
    "BOOKING_CANCELLED",
    "BOOKING_REJECTED",
    "BOOKING_NO_SHOW_UPDATED",
    "BOOKING_PAYMENT_INITIATED",
    "BOOKING_PAID",
    "INSTANT_MEETING",
    "MEETING_STARTED",
    "MEETING_ENDED",
}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _parse_dt(value: Any) -> str | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return None


def _as_list_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def _extract_trigger_event(payload: dict[str, Any]) -> str:
    trigger_event = payload.get("triggerEvent") or payload.get("type")
    return str(trigger_event) if trigger_event else "UNKNOWN"


def _extract_booking_uid(payload: dict[str, Any]) -> str | None:
    nested = payload.get("payload")
    if isinstance(nested, dict):
        uid = nested.get("uid")
        if isinstance(uid, str) and uid.strip():
            return uid.strip()
    top_uid = payload.get("uid")
    if isinstance(top_uid, str) and top_uid.strip():
        return top_uid.strip()
    return None


def _extract_booking_id(payload: dict[str, Any]) -> int | None:
    # MEETING_STARTED/MEETING_ENDED are flat payloads with bookingId at top-level.
    for candidate in (payload.get("bookingId"), payload.get("booking_id")):
        if isinstance(candidate, int):
            return candidate
        if isinstance(candidate, str) and candidate.isdigit():
            return int(candidate)
    nested = payload.get("payload")
    if isinstance(nested, dict):
        for key in ("bookingId", "booking_id", "id"):
            candidate = nested.get(key)
            if isinstance(candidate, int):
                return candidate
            if isinstance(candidate, str) and candidate.isdigit():
                return int(candidate)
    return None


def _extract_payload_obj(payload: dict[str, Any]) -> dict[str, Any]:
    nested = payload.get("payload")
    if isinstance(nested, dict):
        return nested
    return payload


def _extract_location(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("type") or value.get("value")
    return None


def _extract_meeting_url(payload_obj: dict[str, Any], root_payload: dict[str, Any]) -> str | None:
    for candidate in (
        payload_obj.get("meetingUrl"),
        payload_obj.get("meeting_url"),
        payload_obj.get("rescheduleUrl"),
        root_payload.get("meetingUrl"),
        root_payload.get("meeting_url"),
    ):
        if isinstance(candidate, str) and candidate:
            return candidate
    return None


def _normalize_booking_event_from_payload(raw_payload: dict[str, Any]) -> dict[str, Any]:
    payload_obj = _extract_payload_obj(raw_payload)
    organizer_obj = payload_obj.get("organizer")
    organizer = organizer_obj if isinstance(organizer_obj, dict) else {}
    guests = _as_list_strings(payload_obj.get("guests"))
    trigger_event = _extract_trigger_event(raw_payload)

    return {
        "trigger_event": trigger_event,
        "cal_booking_uid": _extract_booking_uid(raw_payload),
        "cal_booking_id": _extract_booking_id(raw_payload),
        "cal_event_type_id": payload_obj.get("eventTypeId") or payload_obj.get("eventType"),
        "title": payload_obj.get("title") or raw_payload.get("title"),
        "start_time": _parse_dt(payload_obj.get("startTime") or payload_obj.get("start")),
        "end_time": _parse_dt(payload_obj.get("endTime") or payload_obj.get("end")),
        "status": payload_obj.get("status") or raw_payload.get("status"),
        "location": _extract_location(payload_obj.get("location")),
        "meeting_url": _extract_meeting_url(payload_obj, raw_payload),
        "organizer_email": organizer.get("email") or raw_payload.get("organizerEmail"),
        "organizer_name": organizer.get("name") or raw_payload.get("organizerName"),
        "organizer_cal_user_id": organizer.get("id") or payload_obj.get("userId"),
        "guests": guests,
        "event_occurred_at": _parse_dt(
            raw_payload.get("createdAt") or payload_obj.get("createdAt")
        ),
    }


def _normalize_attendees_from_payload(raw_payload: dict[str, Any]) -> list[dict[str, Any]]:
    payload_obj = _extract_payload_obj(raw_payload)
    booking_uid = _extract_booking_uid(raw_payload)
    booking_id = _extract_booking_id(raw_payload)

    attendees: list[dict[str, Any]] = []
    payload_attendees = payload_obj.get("attendees")
    if isinstance(payload_attendees, list):
        for attendee in payload_attendees:
            if not isinstance(attendee, dict):
                continue
            email = attendee.get("email")
            if not isinstance(email, str) or not email.strip():
                continue
            attendees.append(
                {
                    "cal_booking_uid": booking_uid,
                    "cal_booking_id": booking_id,
                    "role": "attendee",
                    "name": attendee.get("name"),
                    "email": email.strip().lower(),
                    "timezone": attendee.get("timeZone") or attendee.get("timezone"),
                    "language": attendee.get("language"),
                    "phone_number": attendee.get("phoneNumber") or attendee.get("phone"),
                    "absent": attendee.get("absent"),
                }
            )

    payload_hosts = payload_obj.get("hosts")
    if isinstance(payload_hosts, list):
        for host in payload_hosts:
            if not isinstance(host, dict):
                continue
            email = host.get("email")
            if not isinstance(email, str) or not email.strip():
                continue
            attendees.append(
                {
                    "cal_booking_uid": booking_uid,
                    "cal_booking_id": booking_id,
                    "role": "host",
                    "name": host.get("name"),
                    "email": email.strip().lower(),
                    "timezone": host.get("timeZone") or host.get("timezone"),
                    "language": host.get("language"),
                    "phone_number": host.get("phoneNumber") or host.get("phone"),
                    "absent": host.get("absent"),
                }
            )
    return attendees


def _normalize_recording_from_payload(raw_payload: dict[str, Any]) -> dict[str, Any]:
    payload_obj = _extract_payload_obj(raw_payload)
    recording_id = payload_obj.get("id") or raw_payload.get("id")
    if recording_id is None:
        raise HTTPException(status_code=422, detail="Recording payload missing id")

    return {
        "cal_booking_uid": _extract_booking_uid(raw_payload),
        "cal_booking_id": _extract_booking_id(raw_payload),
        "cal_recording_id": str(recording_id),
        "room_name": payload_obj.get("roomName") or payload_obj.get("room_name"),
        "start_ts": _parse_dt(payload_obj.get("startTs") or payload_obj.get("start_ts")),
        "status": payload_obj.get("status"),
        "duration_seconds": payload_obj.get("duration"),
        "share_token": payload_obj.get("shareToken") or payload_obj.get("share_token"),
        "max_participants": payload_obj.get("maxParticipants")
        or payload_obj.get("max_participants"),
        "download_link": payload_obj.get("downloadLink") or payload_obj.get("download_link"),
    }


async def verify_internal_key(x_internal_key: str = Header(...)) -> None:
    if not settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Internal API not configured",
        )
    if x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal API key",
        )


class RawEventCreateRequest(BaseModel):
    trigger_event: str
    payload: dict[str, Any]
    org_id: UUID | None = None
    cal_booking_uid: str | None = None


class RawEventProcessedRequest(BaseModel):
    processed_at: datetime | None = None


class BookingEventCreateRequest(BaseModel):
    raw_event_id: UUID | None = None
    org_id: UUID | None = None
    trigger_event: str | None = None
    cal_booking_uid: str | None = None
    cal_booking_id: int | None = None
    cal_event_type_id: int | None = None
    title: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str | None = None
    location: str | None = None
    meeting_url: str | None = None
    organizer_email: str | None = None
    organizer_name: str | None = None
    organizer_cal_user_id: int | None = None
    guests: list[str] = Field(default_factory=list)
    event_occurred_at: datetime | None = None
    raw_payload: dict[str, Any] | None = None


class BookingAttendeeItem(BaseModel):
    booking_event_id: UUID | None = None
    org_id: UUID | None = None
    cal_booking_uid: str | None = None
    cal_booking_id: int | None = None
    role: str = "attendee"
    name: str | None = None
    email: str
    timezone: str | None = None
    language: str | None = None
    phone_number: str | None = None
    absent: bool | None = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"attendee", "host"}:
            raise ValueError("role must be attendee or host")
        return normalized


class BookingAttendeesBulkRequest(BaseModel):
    attendees: list[BookingAttendeeItem] = Field(default_factory=list)
    raw_payload: dict[str, Any] | None = None
    booking_event_id: UUID | None = None
    org_id: UUID | None = None


class RecordingCreateRequest(BaseModel):
    raw_event_id: UUID | None = None
    org_id: UUID | None = None
    cal_booking_uid: str | None = None
    cal_booking_id: int | None = None
    cal_recording_id: str | None = None
    room_name: str | None = None
    start_ts: datetime | None = None
    status: str | None = None
    duration_seconds: int | None = None
    share_token: str | None = None
    max_participants: int | None = None
    download_link: str | None = None
    transcript_url: str | None = None
    raw_payload: dict[str, Any] | None = None


class RecordingUpdateRequest(BaseModel):
    status: str | None = None
    transcript_url: str | None = None
    download_link: str | None = None


@router.post("/events/raw", dependencies=[Depends(verify_internal_key)])
async def create_raw_event(body: RawEventCreateRequest) -> dict[str, Any]:
    supabase = get_supabase()
    insert_payload = {
        "trigger_event": body.trigger_event,
        "payload": body.payload,
        "org_id": str(body.org_id) if body.org_id else None,
        "cal_booking_uid": body.cal_booking_uid,
    }
    result = supabase.table("cal_webhook_events_raw").insert(insert_payload).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create raw event")
    return {"id": result.data[0]["id"], "event": result.data[0]}


@router.get("/events/raw/unprocessed", dependencies=[Depends(verify_internal_key)])
async def list_unprocessed_raw_events(limit: int = 100) -> list[dict[str, Any]]:
    bounded_limit = max(1, min(limit, 500))
    supabase = get_supabase()
    result = (
        supabase.table("cal_webhook_events_raw")
        .select("*")
        .is_("processed_at", "null")
        .order("received_at")
        .limit(bounded_limit)
        .execute()
    )
    return result.data or []


@router.patch(
    "/events/raw/{event_id}/processed",
    dependencies=[Depends(verify_internal_key)],
)
async def mark_raw_event_processed(
    event_id: UUID, body: RawEventProcessedRequest
) -> dict[str, Any]:
    supabase = get_supabase()
    processed_at = body.processed_at.isoformat() if body.processed_at else _now_iso()
    result = (
        supabase.table("cal_webhook_events_raw")
        .update({"processed_at": processed_at})
        .eq("id", str(event_id))
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Raw event not found")
    return result.data[0]


@router.post("/booking-events", dependencies=[Depends(verify_internal_key)])
async def create_booking_event(body: BookingEventCreateRequest) -> dict[str, Any]:
    merged = body.model_dump()
    raw_payload = merged.pop("raw_payload")
    derived: dict[str, Any] = {}

    if raw_payload:
        derived = _normalize_booking_event_from_payload(raw_payload)

    trigger_event = merged.get("trigger_event") or derived.get("trigger_event")
    if not trigger_event:
        raise HTTPException(status_code=422, detail="trigger_event is required")
    if trigger_event not in BOOKING_EVENT_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported booking trigger_event")

    payload = {
        "raw_event_id": str(merged["raw_event_id"]) if merged.get("raw_event_id") else None,
        "org_id": str(merged["org_id"]) if merged.get("org_id") else None,
        "trigger_event": trigger_event,
        "cal_booking_uid": merged.get("cal_booking_uid") or derived.get("cal_booking_uid"),
        "cal_booking_id": merged.get("cal_booking_id") or derived.get("cal_booking_id"),
        "cal_event_type_id": merged.get("cal_event_type_id") or derived.get("cal_event_type_id"),
        "title": merged.get("title") or derived.get("title"),
        "start_time": (
            merged["start_time"].isoformat()
            if merged.get("start_time")
            else derived.get("start_time")
        ),
        "end_time": (
            merged["end_time"].isoformat() if merged.get("end_time") else derived.get("end_time")
        ),
        "status": merged.get("status") or derived.get("status"),
        "location": merged.get("location") or derived.get("location"),
        "meeting_url": merged.get("meeting_url") or derived.get("meeting_url"),
        "organizer_email": merged.get("organizer_email") or derived.get("organizer_email"),
        "organizer_name": merged.get("organizer_name") or derived.get("organizer_name"),
        "organizer_cal_user_id": merged.get("organizer_cal_user_id")
        or derived.get("organizer_cal_user_id"),
        "guests": merged.get("guests") or derived.get("guests") or [],
        "event_occurred_at": (
            merged["event_occurred_at"].isoformat()
            if merged.get("event_occurred_at")
            else derived.get("event_occurred_at")
        ),
    }

    supabase = get_supabase()
    # Deliberately allowing duplicate booking lifecycle events for auditability/replay safety.
    result = supabase.table("cal_booking_events").insert(payload).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create booking event")

    created = result.data[0]
    attendees = (
        supabase.table("cal_booking_attendees")
        .select("*")
        .eq("booking_event_id", created["id"])
        .order("email")
        .execute()
    )
    created["attendees"] = attendees.data or []
    return created


@router.get("/booking-events/by-uid/{cal_booking_uid}", dependencies=[Depends(verify_internal_key)])
async def get_booking_events_by_uid(cal_booking_uid: str) -> dict[str, Any]:
    supabase = get_supabase()
    events_result = (
        supabase.table("cal_booking_events")
        .select("*")
        .eq("cal_booking_uid", cal_booking_uid)
        .order("created_at")
        .execute()
    )
    attendees_result = (
        supabase.table("cal_booking_attendees")
        .select("*")
        .eq("cal_booking_uid", cal_booking_uid)
        .order("role")
        .order("email")
        .execute()
    )
    return {"events": events_result.data or [], "attendees": attendees_result.data or []}


@router.get(
    "/booking-events/by-booking-id/{cal_booking_id}",
    dependencies=[Depends(verify_internal_key)],
)
async def get_booking_events_by_booking_id(cal_booking_id: int) -> list[dict[str, Any]]:
    supabase = get_supabase()
    result = (
        supabase.table("cal_booking_events")
        .select("*")
        .eq("cal_booking_id", cal_booking_id)
        .order("created_at")
        .execute()
    )
    return result.data or []


@router.get(
    "/booking-events/latest/by-uid/{cal_booking_uid}",
    dependencies=[Depends(verify_internal_key)],
)
async def get_latest_booking_event_by_uid(cal_booking_uid: str) -> dict[str, Any]:
    supabase = get_supabase()
    result = (
        supabase.table("cal_booking_events")
        .select("*")
        .eq("cal_booking_uid", cal_booking_uid)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="No booking events found")
    return result.data[0]


@router.post("/booking-attendees/bulk", dependencies=[Depends(verify_internal_key)])
async def bulk_upsert_booking_attendees(body: BookingAttendeesBulkRequest) -> dict[str, Any]:
    attendees = [item.model_dump() for item in body.attendees]
    if body.raw_payload and not attendees:
        attendees = _normalize_attendees_from_payload(body.raw_payload)

    if not attendees:
        raise HTTPException(status_code=422, detail="No attendees provided")

    upserts: list[dict[str, Any]] = []
    for attendee in attendees:
        upserts.append(
            {
                "booking_event_id": str(attendee.get("booking_event_id") or body.booking_event_id)
                if attendee.get("booking_event_id") or body.booking_event_id
                else None,
                "org_id": str(attendee.get("org_id") or body.org_id)
                if attendee.get("org_id") or body.org_id
                else None,
                "cal_booking_uid": attendee.get("cal_booking_uid"),
                "cal_booking_id": attendee.get("cal_booking_id"),
                "role": attendee.get("role", "attendee"),
                "name": attendee.get("name"),
                "email": attendee.get("email").strip().lower(),
                "timezone": attendee.get("timezone"),
                "language": attendee.get("language"),
                "phone_number": attendee.get("phone_number"),
                "absent": attendee.get("absent"),
            }
        )

    supabase = get_supabase()
    result = (
        supabase.table("cal_booking_attendees")
        .upsert(upserts, on_conflict="cal_booking_uid,email,role")
        .execute()
    )
    return {"count": len(result.data or []), "attendees": result.data or []}


@router.get(
    "/booking-attendees/by-uid/{cal_booking_uid}",
    dependencies=[Depends(verify_internal_key)],
)
async def get_booking_attendees_by_uid(cal_booking_uid: str) -> list[dict[str, Any]]:
    supabase = get_supabase()
    result = (
        supabase.table("cal_booking_attendees")
        .select("*")
        .eq("cal_booking_uid", cal_booking_uid)
        .order("role")
        .order("email")
        .execute()
    )
    return result.data or []


@router.post("/recordings", dependencies=[Depends(verify_internal_key)])
async def create_recording(body: RecordingCreateRequest) -> dict[str, Any]:
    merged = body.model_dump()
    raw_payload = merged.pop("raw_payload")
    derived: dict[str, Any] = {}
    if raw_payload:
        derived = _normalize_recording_from_payload(raw_payload)

    cal_recording_id = merged.get("cal_recording_id") or derived.get("cal_recording_id")
    if not cal_recording_id:
        raise HTTPException(status_code=422, detail="cal_recording_id is required")

    payload = {
        "raw_event_id": str(merged["raw_event_id"]) if merged.get("raw_event_id") else None,
        "org_id": str(merged["org_id"]) if merged.get("org_id") else None,
        "cal_booking_uid": merged.get("cal_booking_uid") or derived.get("cal_booking_uid"),
        "cal_booking_id": merged.get("cal_booking_id") or derived.get("cal_booking_id"),
        "cal_recording_id": cal_recording_id,
        "room_name": merged.get("room_name") or derived.get("room_name"),
        "start_ts": (
            merged["start_ts"].isoformat() if merged.get("start_ts") else derived.get("start_ts")
        ),
        "status": merged.get("status") or derived.get("status"),
        "duration_seconds": merged.get("duration_seconds") or derived.get("duration_seconds"),
        "share_token": merged.get("share_token") or derived.get("share_token"),
        "max_participants": merged.get("max_participants") or derived.get("max_participants"),
        "download_link": merged.get("download_link") or derived.get("download_link"),
        "transcript_url": merged.get("transcript_url"),
        "updated_at": _now_iso(),
    }

    supabase = get_supabase()
    result = (
        supabase.table("cal_recordings")
        .upsert(payload, on_conflict="cal_recording_id")
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create recording")
    return result.data[0]


@router.get("/recordings/by-uid/{cal_booking_uid}", dependencies=[Depends(verify_internal_key)])
async def get_recordings_by_uid(cal_booking_uid: str) -> list[dict[str, Any]]:
    supabase = get_supabase()
    result = (
        supabase.table("cal_recordings")
        .select("*")
        .eq("cal_booking_uid", cal_booking_uid)
        .order("created_at")
        .execute()
    )
    return result.data or []


@router.patch("/recordings/{recording_id}", dependencies=[Depends(verify_internal_key)])
async def update_recording(recording_id: UUID, body: RecordingUpdateRequest) -> dict[str, Any]:
    payload = {"updated_at": _now_iso()}
    if body.status is not None:
        payload["status"] = body.status
    if body.transcript_url is not None:
        payload["transcript_url"] = body.transcript_url
    if body.download_link is not None:
        payload["download_link"] = body.download_link

    supabase = get_supabase()
    result = supabase.table("cal_recordings").update(payload).eq("id", str(recording_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Recording not found")
    return result.data[0]
