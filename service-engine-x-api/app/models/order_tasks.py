"""Order task models for request/response schemas."""

from pydantic import BaseModel, Field


class TaskEmployeeResponse(BaseModel):
    """Employee assigned to a task."""

    id: str
    name_f: str | None
    name_l: str | None


class OrderTaskCreate(BaseModel):
    """Request body for creating an order task."""

    name: str = Field(..., min_length=1)
    description: str | None = None
    employee_ids: list[str] | None = None
    sort_order: int | None = None
    is_public: bool = False
    for_client: bool = False
    deadline: int | None = None
    due_at: str | None = None


class OrderTaskUpdate(BaseModel):
    """Request body for updating an order task."""

    name: str | None = Field(None, min_length=1)
    description: str | None = None
    employee_ids: list[str] | None = None
    sort_order: int | None = None
    is_public: bool | None = None
    for_client: bool | None = None
    deadline: int | None = None
    due_at: str | None = None


class OrderTaskResponse(BaseModel):
    """Order task response schema."""

    id: str
    order_id: str
    name: str
    description: str | None
    sort_order: int
    is_public: bool
    for_client: bool
    is_complete: bool
    completed_by: str | None
    completed_at: str | None
    deadline: int | None
    due_at: str | None
    employees: list[TaskEmployeeResponse]
