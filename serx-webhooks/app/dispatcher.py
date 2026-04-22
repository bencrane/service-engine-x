"""Dispatch persisted webhook_events_raw rows to managed-agents-x-api.

Called from the ingest BackgroundTask after a successful insert. Never
raises — failures are logged and recorded on the row via dispatch_status
+ dispatch_error. The raw payload is never forwarded; managed-agents
pulls it via serx-mcp.get_webhook_event(id) using event_ref.id.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.database import get_supabase

logger = logging.getLogger("serx_webhooks.dispatcher")

_RETRYABLE_STATUS = {500, 502, 503, 504}
_DISPATCH_PATH = "/sessions/from-event"
_EVENT_STORE = "serx_webhook_events_raw"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _truncate(value: str | None, limit: int = 512) -> str | None:
    if value is None:
        return None
    return value[:limit]


def update_dispatch_result(
    row_id: str,
    dispatch_status: str,
    *,
    session_id: str | None = None,
    error: str | None = None,
) -> None:
    """Best-effort update of the dispatch columns. Never raises."""
    update = {
        "dispatch_status": dispatch_status,
        "dispatched_session_id": session_id,
        "dispatch_error": _truncate(error),
        "dispatched_at": _now_iso(),
    }
    try:
        get_supabase().table("webhook_events_raw").update(update).eq("id", row_id).execute()
    except Exception as exc:
        logger.exception(
            "dispatch_update_failed row_id=%s dispatch_status=%s error=%s",
            row_id,
            dispatch_status,
            exc,
        )


def _normalize_event_name(source: str, trigger_event: str | None) -> str:
    value = trigger_event or ""
    if source == "cal.com":
        return value.upper()
    return value


def _sleep_backoff(attempt: int) -> None:
    delay = min(0.5 * (2 ** attempt), 5.0)
    time.sleep(delay)


def dispatch_event(row_id: str, source: str, trigger_event: str | None) -> None:
    """Synchronous dispatch entry point. Must not raise."""
    try:
        _dispatch_event_inner(row_id=row_id, source=source, trigger_event=trigger_event)
    except Exception as exc:
        logger.exception("dispatch_unhandled_error row_id=%s", row_id)
        update_dispatch_result(row_id, "dispatch_failed", error=f"unhandled: {exc}")


def _dispatch_event_inner(row_id: str, source: str, trigger_event: str | None) -> None:
    if not settings.MANAGED_AGENTS_DISPATCH_ENABLED or not settings.MAG_AUTH_TOKEN:
        update_dispatch_result(row_id, "dispatch_disabled")
        logger.info("dispatch_disabled row_id=%s source=%s", row_id, source)
        return

    event_name = _normalize_event_name(source, trigger_event)
    if not event_name:
        update_dispatch_result(row_id, "dispatched_skipped", error="empty_event_name")
        logger.info("dispatch_skipped_empty_event_name row_id=%s source=%s", row_id, source)
        return

    body = {
        "source": source,
        "event_name": event_name,
        "event_ref": {"store": _EVENT_STORE, "id": row_id},
    }
    url = f"{settings.MANAGED_AGENTS_API_BASE_URL.rstrip('/')}{_DISPATCH_PATH}"
    headers = {
        "Authorization": f"Bearer {settings.MAG_AUTH_TOKEN}",
        "Content-Type": "application/json",
    }

    max_attempts = max(settings.MANAGED_AGENTS_DISPATCH_MAX_ATTEMPTS, 1)
    last_error: str | None = None

    with httpx.Client(timeout=settings.MANAGED_AGENTS_DISPATCH_TIMEOUT_SECONDS) as client:
        for attempt in range(1, max_attempts + 1):
            t0 = time.monotonic()
            try:
                resp = client.post(url, json=body, headers=headers)
            except httpx.RequestError as exc:
                last_error = f"network_error: {exc.__class__.__name__}: {exc}"
                logger.warning(
                    "dispatch_network_error row_id=%s attempt=%d error=%s",
                    row_id,
                    attempt,
                    last_error,
                )
                if attempt < max_attempts:
                    _sleep_backoff(attempt)
                    continue
                break

            latency_ms = int((time.monotonic() - t0) * 1000)
            status = resp.status_code

            if status == 200:
                try:
                    session_id = resp.json().get("session_id")
                except Exception:
                    session_id = None
                update_dispatch_result(row_id, "dispatched", session_id=session_id)
                logger.info(
                    "dispatched row_id=%s source=%s event_name=%s session_id=%s "
                    "attempt=%d latency_ms=%d",
                    row_id,
                    source,
                    event_name,
                    session_id,
                    attempt,
                    latency_ms,
                )
                return

            if status == 404:
                update_dispatch_result(
                    row_id, "dispatched_skipped", error="managed_agents_404"
                )
                logger.info(
                    "dispatch_skipped_404 row_id=%s source=%s event_name=%s latency_ms=%d",
                    row_id,
                    source,
                    event_name,
                    latency_ms,
                )
                return

            if status == 409:
                body_text = resp.text[:512]
                update_dispatch_result(
                    row_id, "dispatched_skipped", error="managed_agents_409_conflict"
                )
                logger.error(
                    "dispatch_conflict row_id=%s source=%s event_name=%s body=%s",
                    row_id,
                    source,
                    event_name,
                    body_text,
                )
                return

            if status in _RETRYABLE_STATUS:
                last_error = f"http_{status}: {resp.text[:256]}"
                logger.warning(
                    "dispatch_retryable row_id=%s attempt=%d status=%d",
                    row_id,
                    attempt,
                    status,
                )
                if attempt < max_attempts:
                    _sleep_backoff(attempt)
                    continue
                break

            # Terminal 4xx (not 404/409): do not retry.
            update_dispatch_result(
                row_id,
                "dispatch_failed",
                error=f"http_{status}: {resp.text[:256]}",
            )
            logger.error(
                "dispatch_failed_terminal row_id=%s source=%s event_name=%s status=%d",
                row_id,
                source,
                event_name,
                status,
            )
            return

    update_dispatch_result(
        row_id,
        "dispatch_failed",
        error=f"exhausted_after_{max_attempts}_attempts: {last_error}",
    )
    logger.error(
        "dispatch_failed_exhausted row_id=%s source=%s event_name=%s attempts=%d error=%s",
        row_id,
        source,
        event_name,
        max_attempts,
        last_error,
    )
