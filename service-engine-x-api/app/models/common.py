"""Common models used across the API."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str


class ValidationErrorResponse(BaseModel):
    """Validation error response matching Next.js format."""

    message: str = "The given data was invalid."
    errors: dict[str, list[str]]


class PaginationLinks(BaseModel):
    """Pagination links for navigating result sets."""

    first: str
    last: str
    prev: str | None
    next: str | None


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    current_page: int
    from_: int = Field(alias="from", serialization_alias="from")
    to: int
    last_page: int
    per_page: int
    total: int
    path: str

    model_config = {"populate_by_name": True}


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    data: list[T]
    links: PaginationLinks
    meta: PaginationMeta
