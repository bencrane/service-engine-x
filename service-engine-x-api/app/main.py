"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers import (
    health_router,
    clients_router,
    services_router,
    orders_router,
    order_tasks_router,
    order_messages_router,
    proposals_router,
    public_proposals_router,
    webhooks_router,
    invoices_router,
    tickets_router,
    engagements_router,
    projects_router,
    conversations_router,
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Service Engine X REST API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware - allowed origins
ALLOWED_ORIGINS = [
    # Localhost development
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
    "http://localhost:3005",
    "http://localhost:3006",
    "http://localhost:3007",
    "http://localhost:3008",
    "http://localhost:3009",
    "http://localhost:3010",
    "http://localhost:4000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3003",
    "http://127.0.0.1:3004",
    "http://127.0.0.1:3005",
    "http://127.0.0.1:3006",
    "http://127.0.0.1:3007",
    "http://127.0.0.1:3008",
    "http://127.0.0.1:3009",
    "http://127.0.0.1:3010",
    "http://127.0.0.1:4000",
    "http://127.0.0.1:8000",
    # Production
    "https://client.revenueactivation.com",
    "https://revenueactivation.com",
    "https://api.serviceengine.xyz",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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


# Include routers
app.include_router(health_router)
app.include_router(clients_router)
app.include_router(services_router)
app.include_router(orders_router)
app.include_router(order_tasks_router)
app.include_router(order_messages_router)
app.include_router(proposals_router)
app.include_router(public_proposals_router)  # Public proposal viewing (no auth)
app.include_router(webhooks_router)  # Documenso webhooks
app.include_router(invoices_router)
app.include_router(tickets_router)
app.include_router(engagements_router)
app.include_router(projects_router)
app.include_router(conversations_router)


def custom_openapi() -> dict:
    """Generate custom OpenAPI schema with security definitions."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
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
        "name": settings.app_name,
        "version": settings.app_version,
        "endpoints": {
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
            "openapi": "/api/openapi.json",
        },
    }
