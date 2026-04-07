"""Health check endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: str


@router.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/health/live")
async def liveness() -> dict:
    """Liveness probe for Railway health checks."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness() -> dict:
    """Readiness probe."""
    return {"status": "ok"}
