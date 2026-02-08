"""API routers."""

from app.routers.health import router as health_router
from app.routers.clients import router as clients_router
from app.routers.services import router as services_router
from app.routers.orders import router as orders_router
from app.routers.order_tasks import router as order_tasks_router
from app.routers.order_messages import router as order_messages_router
from app.routers.proposals import router as proposals_router
from app.routers.invoices import router as invoices_router
from app.routers.tickets import router as tickets_router

__all__ = [
    "health_router",
    "clients_router",
    "services_router",
    "orders_router",
    "order_tasks_router",
    "order_messages_router",
    "proposals_router",
    "invoices_router",
    "tickets_router",
]
