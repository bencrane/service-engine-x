"""Stub handlers for routed Cal.com webhook events.

Each handler receives the raw event row (dict from cal_raw_events) and will
eventually create a managed agent session via the Anthropic API.
"""

import logging
from typing import Any

from app.database import get_supabase

logger = logging.getLogger("cal_event_handlers")

# Map trigger_event → (handler function, agent type label)
_ROUTED_EVENTS: dict[str, tuple[Any, str]] = {}


def _register(trigger: str, agent_type: str):
    """Decorator to register a handler for a trigger event."""
    def decorator(fn):
        _ROUTED_EVENTS[trigger] = (fn, agent_type)
        return fn
    return decorator


def _mark_processed(event_id: str, agent_type: str) -> None:
    """Mark a cal_raw_events row as processed."""
    supabase = get_supabase()
    supabase.table("cal_raw_events").update(
        {"processed": True, "processed_by": agent_type}
    ).eq("id", event_id).execute()


def route_cal_event(event_row: dict[str, Any]) -> None:
    """Dispatch an event row to the appropriate handler, or log as unhandled."""
    trigger = event_row.get("trigger_event", "unknown")
    event_id = event_row.get("id", "?")

    handler_entry = _ROUTED_EVENTS.get(trigger)
    if handler_entry is None:
        logger.info("unhandled trigger=%s id=%s — stored only", trigger, event_id)
        return

    handler_fn, agent_type = handler_entry
    handler_fn(event_row)


# ---------------------------------------------------------------------------
# Stub handlers — each will eventually create an Anthropic agent session.
# ---------------------------------------------------------------------------


@_register("BOOKING_CREATED", agent_type="booking_created_agent")
def handle_booking_created(event_row: dict[str, Any]) -> None:
    event_id = event_row.get("id")
    logger.info("BOOKING_CREATED handler — event_id=%s", event_id)

    # ---------------------------------------------------------------
    # TODO: Create managed agent session (Anthropic API)
    #
    # from anthropic import Anthropic
    # client = Anthropic()
    # session = client.beta.sessions.create(
    #     model="claude-sonnet-4-20250514",
    #     instructions="...",
    #     tools=[...],
    # )
    # ---------------------------------------------------------------

    _mark_processed(event_id, "booking_created_agent")


@_register("BOOKING_RESCHEDULED", agent_type="booking_rescheduled_agent")
def handle_booking_rescheduled(event_row: dict[str, Any]) -> None:
    event_id = event_row.get("id")
    logger.info("BOOKING_RESCHEDULED handler — event_id=%s", event_id)

    # ---------------------------------------------------------------
    # TODO: Create managed agent session (Anthropic API)
    #
    # session = client.beta.sessions.create(...)
    # ---------------------------------------------------------------

    _mark_processed(event_id, "booking_rescheduled_agent")


@_register("BOOKING_CANCELLED", agent_type="booking_cancelled_agent")
def handle_booking_cancelled(event_row: dict[str, Any]) -> None:
    event_id = event_row.get("id")
    logger.info("BOOKING_CANCELLED handler — event_id=%s", event_id)

    # ---------------------------------------------------------------
    # TODO: Create managed agent session (Anthropic API)
    #
    # session = client.beta.sessions.create(...)
    # ---------------------------------------------------------------

    _mark_processed(event_id, "booking_cancelled_agent")


@_register("MEETING_ENDED", agent_type="meeting_ended_agent")
def handle_meeting_ended(event_row: dict[str, Any]) -> None:
    event_id = event_row.get("id")
    logger.info("MEETING_ENDED handler — event_id=%s", event_id)

    # ---------------------------------------------------------------
    # TODO: Create managed agent session (Anthropic API)
    #
    # session = client.beta.sessions.create(...)
    # ---------------------------------------------------------------

    _mark_processed(event_id, "meeting_ended_agent")
