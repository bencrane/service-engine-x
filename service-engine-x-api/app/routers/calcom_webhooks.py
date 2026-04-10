"""Cal.com webhook sink — captures immutable raw events for downstream processing."""

import json
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.database import get_supabase

router = APIRouter(prefix="/api/webhooks/calcom", tags=["Cal.com Webhooks"])


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


@router.post("")
async def calcom_webhook_sink(request: Request) -> JSONResponse:
    """Catch any Cal.com webhook event and store the raw payload."""
    body = await request.body()
    payload = json.loads(body)

    event_type = payload.get("triggerEvent", payload.get("type", "unknown"))

    supabase = get_supabase()
    supabase.table("cal_webhook_events_raw").insert(
        {
            "trigger_event": event_type,
            "payload": payload,
            "cal_booking_uid": _extract_booking_uid(payload),
        }
    ).execute()

    return JSONResponse(
        status_code=200,
        content={"status": "captured", "event_type": event_type},
    )
