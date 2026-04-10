"""Cal.com webhook sink — captures raw payloads for development inspection."""

import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.database import get_supabase

router = APIRouter(prefix="/api/webhooks/calcom", tags=["Cal.com Webhooks"])


@router.post("")
async def calcom_webhook_sink(request: Request) -> JSONResponse:
    """Catch any Cal.com webhook event and store the raw payload."""
    body = await request.body()
    payload = json.loads(body)

    event_type = payload.get("triggerEvent", payload.get("type", "unknown"))

    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() in ("content-type", "user-agent", "x-cal-signature-256")
    }

    supabase = get_supabase()
    supabase.table("calcom_webhook_log").insert(
        {
            "event_type": event_type,
            "payload": payload,
            "headers": headers,
        }
    ).execute()

    return JSONResponse(
        status_code=200,
        content={"status": "captured", "event_type": event_type},
    )
