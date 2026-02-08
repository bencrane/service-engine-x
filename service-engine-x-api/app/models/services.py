"""Service models for request/response schemas."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class MetadataItem(BaseModel):
    """Metadata item for service configuration."""

    title: str
    value: str = ""


class ServiceCreate(BaseModel):
    """Request body for creating a service."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    recurring: int = Field(..., ge=0, le=2)
    currency: str = Field(..., min_length=1)
    price: float | None = None
    f_price: float | None = None
    f_period_l: int | None = None
    f_period_t: str | None = None
    r_price: float | None = None
    r_period_l: int | None = None
    r_period_t: str | None = None
    recurring_action: int | None = None
    deadline: int | None = None
    public: bool = True
    employees: list[str] | None = None
    group_quantities: bool = False
    multi_order: bool = True
    request_orders: bool = False
    max_active_requests: int | None = None
    metadata: list[MetadataItem] | None = None
    folder_id: str | None = None
    braintree_plan_id: str | None = None
    hoth_product_key: str | None = None
    hoth_package_name: str | None = None
    provider_id: int | None = None
    provider_service_id: int | None = None

    @field_validator("f_period_t", "r_period_t")
    @classmethod
    def validate_period_type(cls, v: str | None) -> str | None:
        if v is not None and v not in ["D", "W", "M", "Y"]:
            raise ValueError("Period type must be D, W, M, or Y")
        return v


class ServiceUpdate(BaseModel):
    """Request body for updating a service."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    recurring: int | None = Field(None, ge=0, le=2)
    currency: str | None = None
    price: float | None = None
    f_price: float | None = None
    f_period_l: int | None = None
    f_period_t: str | None = None
    r_price: float | None = None
    r_period_l: int | None = None
    r_period_t: str | None = None
    recurring_action: int | None = None
    deadline: int | None = None
    public: bool | None = None
    employees: list[str] | None = None
    group_quantities: bool | None = None
    multi_order: bool | None = None
    request_orders: bool | None = None
    max_active_requests: int | None = None
    metadata: list[MetadataItem] | None = None
    folder_id: str | None = None
    sort_order: int | None = None
    braintree_plan_id: str | None = None
    hoth_product_key: str | None = None
    hoth_package_name: str | None = None
    provider_id: int | None = None
    provider_service_id: int | None = None

    @field_validator("f_period_t", "r_period_t")
    @classmethod
    def validate_period_type(cls, v: str | None) -> str | None:
        if v is not None and v not in ["D", "W", "M", "Y"]:
            raise ValueError("Period type must be D, W, M, or Y")
        return v


class ServiceResponse(BaseModel):
    """Service response schema."""

    id: str
    name: str
    description: str | None
    image: str | None
    recurring: int
    price: str | None
    pretty_price: str
    currency: str
    f_price: str | None
    f_period_l: int | None
    f_period_t: str | None
    r_price: str | None
    r_period_l: int | None
    r_period_t: str | None
    recurring_action: int | None
    multi_order: bool
    request_orders: bool
    max_active_requests: int | None
    deadline: int | None
    public: bool
    sort_order: int
    group_quantities: bool
    folder_id: str | None
    metadata: dict[str, Any]
    braintree_plan_id: str | None
    hoth_product_key: str | None
    hoth_package_name: str | None
    provider_id: int | None
    provider_service_id: int | None
    created_at: str
    updated_at: str
