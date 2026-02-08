"""API routers."""

from app.routers.health import router as health_router
from app.routers.clients import router as clients_router

__all__ = ["health_router", "clients_router"]
