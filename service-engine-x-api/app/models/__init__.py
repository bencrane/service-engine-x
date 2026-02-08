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
from app.models.services import (
    MetadataItem,
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
)
from app.models.orders import (
    OrderEmployeeResponse,
    OrderClientResponse,
    OrderCreate,
    OrderUpdate,
    OrderResponse,
)
from app.models.order_tasks import (
    TaskEmployeeResponse,
    OrderTaskCreate,
    OrderTaskUpdate,
    OrderTaskResponse,
)
from app.models.order_messages import (
    OrderMessageCreate,
    OrderMessageResponse,
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
    "MetadataItem",
    "ServiceCreate",
    "ServiceUpdate",
    "ServiceResponse",
    "OrderEmployeeResponse",
    "OrderClientResponse",
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "TaskEmployeeResponse",
    "OrderTaskCreate",
    "OrderTaskUpdate",
    "OrderTaskResponse",
    "OrderMessageCreate",
    "OrderMessageResponse",
]
