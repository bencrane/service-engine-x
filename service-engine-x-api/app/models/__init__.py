"""Pydantic models for request/response schemas."""

from app.models.common import (
    ErrorResponse,
    ValidationErrorResponse,
    PaginatedResponse,
    PaginationLinks,
    PaginationMeta,
)
from app.models.clients import (
    AddressInput,
    AddressResponse,
    RoleResponse,
    ClientCreate,
    ClientUpdate,
    ClientResponse,
)

__all__ = [
    "ErrorResponse",
    "ValidationErrorResponse",
    "PaginatedResponse",
    "PaginationLinks",
    "PaginationMeta",
    "AddressInput",
    "AddressResponse",
    "RoleResponse",
    "ClientCreate",
    "ClientUpdate",
    "ClientResponse",
]
