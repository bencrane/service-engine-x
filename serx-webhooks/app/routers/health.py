"""Health endpoints. /health/live is static; /health/ready pings Supabase."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.database import get_supabase

logger = logging.getLogger("serx_webhooks.health")

router = APIRouter(tags=["Health"])


@router.get("/health/live")
async def liveness() -> dict:
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness() -> JSONResponse:
    try:
        get_supabase().table("webhook_events_raw").select(
            "id", head=True, count="exact"
        ).limit(1).execute()
        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as exc:
        logger.exception("readiness check failed")
        return JSONResponse(status_code=503, content={"status": "unavailable", "error": str(exc)})
