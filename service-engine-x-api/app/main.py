"""FastAPI application entry point."""

import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import (
    accounts_router,
    auth_router,
    bank_details_router,
    calcom_webhooks_router,
    clients_router,
    contacts_router,
    conversations_router,
    engagements_router,
    health_router,
    internal_cal_events_router,
    internal_meetings_deals_router,
    internal_router,
    invoices_router,
    order_messages_router,
    order_tasks_router,
    orders_router,
    projects_router,
    proposals_router,
    public_proposals_router,
    services_router,
    tickets_router,
    webhooks_router,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Service Engine X REST API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Custom validation error handler to match Next.js format.

    Converts Pydantic validation errors to:
    {
        "message": "The given data was invalid.",
        "errors": {
            "field_name": ["Error message"]
        }
    }
    """
    errors: dict[str, list[str]] = {}

    for error in exc.errors():
        # Build field path from location, skipping 'body' prefix
        loc = error.get("loc", ())
        field_parts = [str(part) for part in loc if part != "body"]
        field = ".".join(field_parts) if field_parts else "root"

        if field not in errors:
            errors[field] = []

        # Use custom message or default
        msg = error.get("msg", "Invalid value")
        errors[field].append(msg)

    return JSONResponse(
        status_code=400,
        content={"message": "The given data was invalid.", "errors": errors},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch all unhandled exceptions and return actual error details.
    This makes debugging much easier.
    """
    error_detail = {
        "error": str(exc),
        "type": type(exc).__name__,
        "path": str(request.url.path),
        "method": request.method,
    }

    # Include traceback in response for debugging
    error_detail["traceback"] = traceback.format_exc()

    # Log it
    print(f"[ERROR] {request.method} {request.url.path}: {exc}")
    print(traceback.format_exc())

    return JSONResponse(
        status_code=500,
        content=error_detail,
    )


# Include routers
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(clients_router)
app.include_router(services_router)
app.include_router(orders_router)
app.include_router(order_tasks_router)
app.include_router(order_messages_router)
app.include_router(proposals_router)
app.include_router(public_proposals_router)  # Public proposal viewing (no auth)
app.include_router(webhooks_router)  # Stripe webhooks
app.include_router(invoices_router)
app.include_router(tickets_router)
app.include_router(engagements_router)
app.include_router(projects_router)
app.include_router(conversations_router)
app.include_router(internal_router)  # Internal admin API
app.include_router(accounts_router)  # Accounts (CRM companies)
app.include_router(contacts_router)  # Contacts (people at accounts)
app.include_router(bank_details_router)  # Org bank details (wire/ACH)
app.include_router(calcom_webhooks_router)  # Cal.com webhook payload capture
app.include_router(internal_cal_events_router)  # Internal Cal.com normalization API
app.include_router(internal_meetings_deals_router)  # Internal meetings/deals + org resolution


def custom_openapi() -> dict:
    """Generate custom OpenAPI schema with security definitions."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Service Engine X REST API - Multi-tenant SaaS platform for service businesses",
        routes=app.routes,
    )

    # Add security scheme for Bearer token authentication
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "API Token",
            "description": "API token authentication. Get your token from the dashboard.",
        }
    }

    # Add global security requirement (except for health and openapi endpoints)
    openapi_schema["security"] = [{"BearerAuth": []}]

    # Add common error responses to components
    openapi_schema["components"]["schemas"]["ErrorResponse"] = {
        "type": "object",
        "properties": {
            "message": {"type": "string", "example": "The given data was invalid."},
            "errors": {
                "type": "object",
                "additionalProperties": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "example": {"field_name": ["Error message"]}
            }
        },
        "required": ["message"]
    }

    openapi_schema["components"]["schemas"]["NotFoundResponse"] = {
        "type": "object",
        "properties": {
            "detail": {"type": "string", "example": "Not Found"}
        }
    }

    openapi_schema["components"]["schemas"]["UnauthorizedResponse"] = {
        "type": "object",
        "properties": {
            "detail": {"type": "string", "example": "Unauthorized"}
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/api/openapi.json", tags=["OpenAPI"], include_in_schema=False)
async def get_openapi_spec() -> dict:
    """Return the OpenAPI specification as JSON."""
    return app.openapi()


@app.get("/api", tags=["Index"])
async def api_index() -> dict:
    """API index endpoint listing available resources."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "auth_login": "/api/auth/login",
            "auth_me": "/api/auth/me",
            "health": "/api/health",
            "clients": "/api/clients",
            "services": "/api/services",
            "orders": "/api/orders",
            "proposals": "/api/proposals",
            "invoices": "/api/invoices",
            "tickets": "/api/tickets",
            "engagements": "/api/engagements",
            "projects": "/api/projects",
            "conversations": "/api/conversations",
            "accounts": "/api/accounts",
            "contacts": "/api/contacts",
            "bank_details": "/api/bank-details",
            "openapi": "/api/openapi.json",
        },
    }
