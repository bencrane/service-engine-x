"""Cal.com webhook ingestion endpoint.

Phase 1 behavior: return 202 Accepted immediately, persist the full body
(plus raw bytes, headers, and HMAC validity) to webhook_events_raw via a
FastAPI BackgroundTask. Idempotent by sha256(raw_body).
"""

import hashlib
import hmac
import json
import logging
import time
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import get_supabase
from app.dispatcher import dispatch_event

logger = logging.getLogger("serx_webhooks.cal")

router = APIRouter(tags=["Cal.com Webhooks"])


def _compute_signature_valid(raw_body: bytes, signature_header: str | None) -> bool | None:
    secret = settings.CAL_WEBHOOK_SECRET
    if not secret:
        logger.warning("CAL_WEBHOOK_SECRET not set — signature_valid stored as null")
        return None
    if not signature_header:
        return False
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def _parse_payload(raw_body: bytes) -> tuple[Any, str | None]:
    """Return (payload_for_jsonb, trigger_event_or_none)."""
    try:
        parsed = json.loads(raw_body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"_raw_text": raw_body.decode("utf-8", errors="replace")}, None
    trigger_event = parsed.get("triggerEvent") if isinstance(parsed, dict) else None
    return parsed, trigger_event


def _store_event(
    raw_body: bytes,
    headers: dict[str, str],
    signature_header: str | None,
    t_start: float,
) -> None:
    """Background task: parse + insert. Never raises."""
    event_key = hashlib.sha256(raw_body).hexdigest()
    trigger_event: str | None = None
    row_id: str | None = None
    duplicate = False
    signature_valid: bool | None = None

    try:
        payload, trigger_event = _parse_payload(raw_body)
        signature_valid = _compute_signature_valid(raw_body, signature_header)
        row = {
            "source": "cal_com",
            "trigger_event": trigger_event,
            "event_key": event_key,
            "payload": payload,
            "raw_body": raw_body.decode("latin-1"),
            "headers": headers,
            "signature_valid": signature_valid,
        }
        result = get_supabase().table("webhook_events_raw").insert(row).execute()
        row_id = result.data[0].get("id") if result.data else None
    except Exception as exc:
        msg = str(exc)
        if "23505" in msg or "duplicate key" in msg.lower():
            duplicate = True
        else:
            logger.exception(
                "webhook_error source=cal_com trigger_event=%s event_key=%s",
                trigger_event,
                event_key,
            )
            return

    if not duplicate and row_id:
        dispatch_event(row_id=row_id, source="cal_com", trigger_event=trigger_event)

    latency_ms = int((time.monotonic() - t_start) * 1000)
    logger.info(
        "%s source=cal_com trigger_event=%s event_key=%s row_id=%s "
        "signature_valid=%s duplicate=%s latency_ms=%d",
        "webhook_duplicate" if duplicate else "webhook_stored",
        trigger_event,
        event_key,
        row_id,
        signature_valid,
        duplicate,
        latency_ms,
    )


@router.post("/webhooks/cal")
async def cal_webhook(request: Request, background_tasks: BackgroundTasks) -> JSONResponse:
    t_start = time.monotonic()
    raw_body = await request.body()
    headers = {k.lower(): v for k, v in request.headers.items()}
    signature_header = request.headers.get("X-Cal-Signature-256")
    background_tasks.add_task(_store_event, raw_body, headers, signature_header, t_start)
    return JSONResponse(status_code=202, content={"status": "accepted"})
