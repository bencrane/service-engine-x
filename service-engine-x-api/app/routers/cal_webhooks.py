"""Cal.com webhook receiver — HMAC-verified, dual-shape, agent-routable.

Handles both the standard envelope ``{ triggerEvent, payload: {...} }``
and the flat shape used by MEETING_STARTED / MEETING_ENDED.

See: api-reference-docs-new/cal.com/CALCOM-WEBHOOKS.md for payload specs.
"""

import hashlib
import hmac
import json
import logging
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import get_supabase
from app.services.cal_event_handlers import route_cal_event

logger = logging.getLogger("cal_webhooks")

router = APIRouter(tags=["Cal.com Webhooks"])

# Trigger events that use a flat payload (no nested `payload` key).
# Ref: CALCOM-WEBHOOKS.md §3 — MEETING_STARTED / MEETING_ENDED
FLAT_PAYLOAD_TRIGGERS = {"MEETING_STARTED", "MEETING_ENDED"}


def _verify_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Verify X-Cal-Signature-256 HMAC-SHA256 signature.

    If CALCOM_WEBHOOK_SECRET is empty (local dev), verification is skipped.
    """
    secret = settings.CAL_WEBHOOK_SECRET
    if not secret:
        logger.warning("CAL_WEBHOOK_SECRET not set — skipping HMAC verification")
        return True

    if not signature_header:
        logger.warning("Missing X-Cal-Signature-256 header")
        return False

    expected = hmac.new(
        secret.encode(), raw_body, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature_header)


def _extract_fields(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract storage fields from either payload shape.

    Standard envelope:  { triggerEvent, createdAt, payload: { uid, hosts, attendees, eventTypeId, ... } }
    Flat (meetings):    { triggerEvent, createdAt, bookingId, roomName, ... }
    """
    trigger_event = payload.get("triggerEvent", "unknown")
    is_flat = trigger_event in FLAT_PAYLOAD_TRIGGERS

    if is_flat:
        # Flat shape — fields are top-level. No uid/hosts/attendees/eventTypeId.
        return {
            "trigger_event": trigger_event,
            "cal_event_uid": None,
            "organizer_email": None,
            "attendee_emails": [],
            "event_type_id": None,
        }

    # Standard envelope — booking data lives under payload.
    inner = payload.get("payload", {})
    if not isinstance(inner, dict):
        inner = {}

    # organizer_email: first host's email
    hosts = inner.get("hosts") or []
    organizer_email = hosts[0].get("email") if hosts else None

    # attendee_emails: all attendee emails + guests
    attendees = inner.get("attendees") or []
    attendee_emails = [a.get("email") for a in attendees if a.get("email")]
    guests = inner.get("guests") or []
    attendee_emails.extend(g for g in guests if isinstance(g, str))

    return {
        "trigger_event": trigger_event,
        "cal_event_uid": inner.get("uid"),
        "organizer_email": organizer_email,
        "attendee_emails": attendee_emails,
        "event_type_id": inner.get("eventTypeId"),
    }


@router.post("/api/webhooks/cal")
async def cal_webhook(request: Request) -> JSONResponse:
    """Receive Cal.com webhook, verify HMAC, store, and route."""
    raw_body = await request.body()

    # --- HMAC verification ---
    signature = request.headers.get("X-Cal-Signature-256")
    if not _verify_signature(raw_body, signature):
        return JSONResponse(status_code=401, content={"error": "invalid signature"})

    # --- Parse ---
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "invalid JSON"})

    fields = _extract_fields(payload)

    # --- Store in cal_raw_events ---
    supabase = get_supabase()
    row = {
        "trigger_event": fields["trigger_event"],
        "payload": payload,
        "cal_event_uid": fields["cal_event_uid"],
        "organizer_email": fields["organizer_email"],
        "attendee_emails": fields["attendee_emails"],
        "event_type_id": fields["event_type_id"],
        "processed": False,
    }
    result = supabase.table("cal_raw_events").insert(row).execute()
    event_row = result.data[0] if result.data else row

    logger.info(
        "cal_webhook stored event=%s uid=%s id=%s",
        fields["trigger_event"],
        fields["cal_event_uid"],
        event_row.get("id"),
    )

    # --- Route to handler ---
    route_cal_event(event_row)

    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "trigger_event": fields["trigger_event"],
            "event_id": event_row.get("id"),
        },
    )
