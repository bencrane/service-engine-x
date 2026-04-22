"""Internal read surface for serx-webhooks' webhook_events_raw table.

Exposed so serx-mcp (and the managed agents it serves) can fetch the full
webhook payload using the event_ref.id that serx-webhooks wrote into its
managed-agents dispatch body. Raw payloads are intentionally not forwarded
in the dispatch request — agents pull them here.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.database import get_supabase
from app.routers.internal_cal_events import verify_internal_key

router = APIRouter(
    prefix="/api/internal/webhook-events",
    tags=["Internal Webhook Events"],
)


@router.get("/{event_id}", dependencies=[Depends(verify_internal_key)])
async def get_webhook_event(event_id: UUID) -> dict[str, Any]:
    """Return a single webhook_events_raw row by id."""
    result = (
        get_supabase()
        .table("webhook_events_raw")
        .select("*")
        .eq("id", str(event_id))
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Webhook event not found")
    return result.data[0]
