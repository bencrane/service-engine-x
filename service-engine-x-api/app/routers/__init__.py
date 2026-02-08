"""API routers."""

from app.routers.health import router as health_router
from app.routers.clients import router as clients_router
from app.routers.services import router as services_router

__all__ = ["health_router", "clients_router", "services_router"]
