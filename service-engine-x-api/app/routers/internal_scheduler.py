"""Internal SERX scheduler dispatch endpoints.

The Trigger.dev ticker is a dumb clock — it only POSTs here. This module owns:
  1. Querying due meetings per event-config (window, status, idempotency column).
  2. Inserting synthetic rows into webhook_events_raw with source='serx_scheduler'.
  3. Dispatching each row to managed-agents-x-api /sessions/from-event.
  4. Recording dispatch outcomes (dispatched / no_route / failed) for observability.

Adding a new time-based event (e.g. meeting_reminder_due, no_show_nudge_due)
means appending an `EventConfig` below, not restructuring the endpoint.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from app.config import settings
from app.database import get_supabase

router = APIRouter(prefix="/api/internal/scheduler", tags=["Internal Scheduler"])


# ────────────────────────────────────────────────────────────────────────────
# Auth — Bearer token matching INTERNAL_API_KEY.
# ────────────────────────────────────────────────────────────────────────────

async def verify_scheduler_token(authorization: str = Header(...)) -> None:
    if not settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scheduler endpoint not configured",
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid scheduler token",
        )


# ────────────────────────────────────────────────────────────────────────────
# Event configs — one per time-based event type.
# ────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EventConfig:
    event_name: str
    idempotency_column: str  # meetings column that orchestrator sets on success
    window_start_hours: int  # lower bound of meeting.start_time relative to now
    window_end_hours: int    # upper bound
    min_meeting_age_hours: int  # created_at must be older than this
    build_payload: Callable[[dict[str, Any], datetime], dict[str, Any]]


def _preframe_payload(meeting: dict[str, Any], now: datetime) -> dict[str, Any]:
    return {
        "meeting_id": meeting["id"],
        "org_id": meeting["org_id"],
        "due_at": now.isoformat(),
        "start_time": meeting["start_time"],
        "window_hours": settings.SCHEDULER_PREFRAME_WINDOW_END_HOURS,
    }


PREFRAME_CONFIG = EventConfig(
    event_name="meeting_preframe_due",
    idempotency_column="preframe_sent_at",
    window_start_hours=settings.SCHEDULER_PREFRAME_WINDOW_START_HOURS,
    window_end_hours=settings.SCHEDULER_PREFRAME_WINDOW_END_HOURS,
    min_meeting_age_hours=settings.SCHEDULER_PREFRAME_MIN_AGE_HOURS,
    build_payload=_preframe_payload,
)


# ────────────────────────────────────────────────────────────────────────────
# Response shape
# ────────────────────────────────────────────────────────────────────────────

class DispatchError(BaseModel):
    meeting_id: str
    stage: str  # "insert" | "dispatch"
    error: str


class DispatchSummary(BaseModel):
    ok: bool
    event_name: str
    due_count: int
    inserted: int
    dispatched: int
    no_route: int
    failed: int
    skipped_existing: int
    errors: list[DispatchError]


# ────────────────────────────────────────────────────────────────────────────
# Core dispatcher
# ────────────────────────────────────────────────────────────────────────────

def _query_due_meetings(
    supabase: Any, cfg: EventConfig, now: datetime
) -> list[dict[str, Any]]:
    window_start = now + timedelta(hours=cfg.window_start_hours)
    window_end = now + timedelta(hours=cfg.window_end_hours)
    max_created_at = now - timedelta(hours=cfg.min_meeting_age_hours)

    result = (
        supabase.table("meetings")
        .select("id, org_id, start_time, created_at, status")
        .eq("status", "scheduled")
        .gte("start_time", window_start.isoformat())
        .lte("start_time", window_end.isoformat())
        .is_(cfg.idempotency_column, "null")
        .lt("created_at", max_created_at.isoformat())
        .execute()
    )
    return result.data or []


def _insert_webhook_event(
    supabase: Any, cfg: EventConfig, meeting: dict[str, Any], now: datetime
) -> tuple[str | None, bool]:
    """Insert synthetic webhook event. Returns (row_id, was_duplicate)."""
    payload = cfg.build_payload(meeting, now)
    insert_result = (
        supabase.table("webhook_events_raw")
        .insert(
            {
                "source": "serx_scheduler",
                "event_name": cfg.event_name,
                "payload": payload,
                "dispatch_status": "pending",
                "dispatch_attempt_count": 0,
            }
        )
        .execute()
    )
    rows = insert_result.data or []
    if not rows:
        return None, True
    return rows[0]["id"], False


def _update_dispatch_outcome(
    supabase: Any,
    event_id: str,
    *,
    status_value: str,
    session_id: str | None,
    increment_attempt: bool,
    last_error: str | None = None,
) -> None:
    patch: dict[str, Any] = {
        "dispatch_status": status_value,
        "dispatched_at": datetime.now(timezone.utc).isoformat(),
    }
    if session_id is not None:
        patch["session_id"] = session_id
    if last_error is not None:
        patch["last_dispatch_error"] = last_error[:2000]
    if increment_attempt:
        # Read-modify-write — Supabase Python client has no native atomic inc.
        current = (
            supabase.table("webhook_events_raw")
            .select("dispatch_attempt_count")
            .eq("id", event_id)
            .limit(1)
            .execute()
        )
        prev = (current.data or [{}])[0].get("dispatch_attempt_count") or 0
        patch["dispatch_attempt_count"] = prev + 1

    supabase.table("webhook_events_raw").update(patch).eq("id", event_id).execute()


async def _dispatch_to_managed_agents(
    client: httpx.AsyncClient, cfg: EventConfig, event_id: str
) -> tuple[int, dict[str, Any] | None]:
    response = await client.post(
        f"{settings.OPEX_API_URL.rstrip('/')}/sessions/from-event",
        headers={
            "Authorization": f"Bearer {settings.OPEX_AUTH_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "source": "serx_scheduler",
            "event_name": cfg.event_name,
            "event_ref": {
                "store": "serx_webhook_events_raw",
                "id": event_id,
            },
        },
        timeout=settings.SCHEDULER_DISPATCH_TIMEOUT_SECONDS,
    )
    body: dict[str, Any] | None = None
    try:
        body = response.json()
    except Exception:  # noqa: BLE001
        body = None
    return response.status_code, body


async def _run_event_dispatch(cfg: EventConfig) -> DispatchSummary:
    if not settings.OPEX_API_URL or not settings.OPEX_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="managed-agents dispatch is not configured",
        )

    supabase = get_supabase()
    now = datetime.now(timezone.utc)

    due = _query_due_meetings(supabase, cfg, now)
    errors: list[DispatchError] = []
    inserted_ids: list[tuple[str, str]] = []  # (event_id, meeting_id)
    skipped_existing = 0

    for meeting in due:
        try:
            event_id, was_dup = _insert_webhook_event(supabase, cfg, meeting, now)
        except Exception as exc:  # noqa: BLE001 — dedup index violation lands here
            msg = str(exc)
            if "uq_webhook_events_raw_serx_scheduler" in msg or "duplicate key" in msg:
                skipped_existing += 1
                continue
            errors.append(
                DispatchError(meeting_id=meeting["id"], stage="insert", error=msg)
            )
            continue
        if was_dup or event_id is None:
            skipped_existing += 1
            continue
        inserted_ids.append((event_id, meeting["id"]))

    dispatched = 0
    no_route = 0
    failed = 0

    if inserted_ids:
        async with httpx.AsyncClient() as client:
            for event_id, meeting_id in inserted_ids:
                try:
                    code, body = await _dispatch_to_managed_agents(client, cfg, event_id)
                except Exception as exc:  # noqa: BLE001
                    failed += 1
                    _update_dispatch_outcome(
                        supabase,
                        event_id,
                        status_value="failed",
                        session_id=None,
                        increment_attempt=True,
                        last_error=f"request_error: {exc}",
                    )
                    errors.append(
                        DispatchError(
                            meeting_id=meeting_id, stage="dispatch", error=str(exc)
                        )
                    )
                    continue

                if 200 <= code < 300:
                    session_id = (body or {}).get("session_id") if body else None
                    _update_dispatch_outcome(
                        supabase,
                        event_id,
                        status_value="dispatched",
                        session_id=session_id,
                        increment_attempt=True,
                    )
                    dispatched += 1
                elif code == 404:
                    _update_dispatch_outcome(
                        supabase,
                        event_id,
                        status_value="no_route",
                        session_id=None,
                        increment_attempt=True,
                    )
                    no_route += 1
                else:
                    failed += 1
                    _update_dispatch_outcome(
                        supabase,
                        event_id,
                        status_value="failed",
                        session_id=None,
                        increment_attempt=True,
                        last_error=f"http_{code}: {body}",
                    )
                    errors.append(
                        DispatchError(
                            meeting_id=meeting_id,
                            stage="dispatch",
                            error=f"http_{code}",
                        )
                    )

    return DispatchSummary(
        ok=failed == 0,
        event_name=cfg.event_name,
        due_count=len(due),
        inserted=len(inserted_ids),
        dispatched=dispatched,
        no_route=no_route,
        failed=failed,
        skipped_existing=skipped_existing,
        errors=errors,
    )


# ────────────────────────────────────────────────────────────────────────────
# Routes
# ────────────────────────────────────────────────────────────────────────────

@router.post(
    "/dispatch-due-preframes",
    dependencies=[Depends(verify_scheduler_token)],
    response_model=DispatchSummary,
)
async def dispatch_due_preframes() -> DispatchSummary:
    """Find meetings due for a preframe and dispatch synthetic events to MAG."""
    return await _run_event_dispatch(PREFRAME_CONFIG)
