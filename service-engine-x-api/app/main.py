"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers import health_router, clients_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Service Engine X REST API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        },
    }
