"""Order message models for request/response schemas."""

from pydantic import BaseModel, Field


class OrderMessageCreate(BaseModel):
    """Request body for creating an order message."""

    message: str = Field(..., min_length=1)
    is_public: bool = True


class OrderMessageResponse(BaseModel):
    """Order message response schema."""

    id: str
    order_id: str
    user_id: str | None
    message: str
    is_public: bool
    created_at: str
    user: dict | None = None
