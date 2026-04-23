"""API routers."""

from app.routers.accounts import router as accounts_router
from app.routers.bank_details import router as bank_details_router
from app.routers.cal_webhooks import router as cal_webhooks_router
from app.routers.calcom_webhooks import router as calcom_webhooks_router
from app.routers.clients import router as clients_router
from app.routers.contacts import router as contacts_router
from app.routers.conversations import router as conversations_router
from app.routers.engagements import router as engagements_router
from app.routers.health import router as health_router
from app.routers.internal import router as internal_router
from app.routers.internal_cal_events import router as internal_cal_events_router
from app.routers.internal_meetings_deals import router as internal_meetings_deals_router
from app.routers.internal_scheduler import router as internal_scheduler_router
from app.routers.internal_webhook_events import router as internal_webhook_events_router
from app.routers.invoices import router as invoices_router
from app.routers.meetings import router as meetings_router
from app.routers.order_messages import router as order_messages_router
from app.routers.order_tasks import router as order_tasks_router
from app.routers.orders import router as orders_router
from app.routers.orgs import router as orgs_router
from app.routers.projects import router as projects_router
from app.routers.proposals import public_router as public_proposals_router
from app.routers.proposals import router as proposals_router
from app.routers.proposals import webhook_router as webhooks_router
from app.routers.services import router as services_router
from app.routers.tickets import router as tickets_router
from app.routers.users import router as users_router

__all__ = [
    "health_router",
    "clients_router",
    "services_router",
    "orders_router",
    "order_tasks_router",
    "order_messages_router",
    "proposals_router",
    "public_proposals_router",
    "webhooks_router",
    "invoices_router",
    "tickets_router",
    "engagements_router",
    "projects_router",
    "conversations_router",
    "internal_router",
    "accounts_router",
    "contacts_router",
    "bank_details_router",
    "cal_webhooks_router",
    "calcom_webhooks_router",
    "internal_cal_events_router",
    "internal_meetings_deals_router",
    "internal_scheduler_router",
    "internal_webhook_events_router",
    "meetings_router",
    "orgs_router",
    "users_router",
]
