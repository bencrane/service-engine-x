"""Order Tasks API router for standalone task operations."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response

from app.auth import AuthContext, get_current_org
from app.database import get_supabase
from app.models.order_tasks import OrderTaskResponse, OrderTaskUpdate, TaskEmployeeResponse
from app.utils import is_valid_uuid

router = APIRouter(prefix="/api/order-tasks", tags=["Order Tasks"])


async def fetch_task_employees(supabase, task_id: str) -> list[TaskEmployeeResponse]:
    """Fetch employees assigned to a task."""
    assignments = (
        supabase.table("order_task_employees")
        .select("employee_id")
        .eq("task_id", task_id)
        .execute()
    )

    if not assignments.data:
        return []

    emp_ids = [a["employee_id"] for a in assignments.data]
    employees = (
        supabase.table("users")
        .select("id, name_f, name_l")
        .in_("id", emp_ids)
        .execute()
    )

    return [
        TaskEmployeeResponse(
            id=e["id"],
            name_f=e.get("name_f"),
            name_l=e.get("name_l"),
        )
        for e in (employees.data or [])
    ]


async def serialize_task(supabase, task: dict[str, Any]) -> OrderTaskResponse:
    """Serialize a task with employees."""
    employees = await fetch_task_employees(supabase, task["id"])

    return OrderTaskResponse(
        id=task["id"],
        order_id=task["order_id"],
        name=task["name"],
        description=task.get("description"),
        sort_order=task.get("sort_order", 0),
        is_public=task.get("is_public", False),
        for_client=task.get("for_client", False),
        is_complete=task.get("is_complete", False),
        completed_by=task.get("completed_by"),
        completed_at=task.get("completed_at"),
        deadline=task.get("deadline"),
        due_at=task.get("due_at"),
        employees=employees,
    )


async def get_task_with_order(supabase, task_id: str, org_id: str) -> dict[str, Any] | None:
    """Get task and verify parent order belongs to org and isn't deleted."""
    result = (
        supabase.table("order_tasks")
        .select("*, orders!inner(id, org_id, deleted_at)")
        .eq("id", task_id)
        .execute()
    )

    if not result.data or len(result.data) == 0:
        return None

    task = result.data[0]
    order = task.get("orders")
    if isinstance(order, list):
        order = order[0] if order else None

    if not order:
        return None

    # Check org_id and deleted_at
    if order.get("org_id") != org_id or order.get("deleted_at") is not None:
        return None

    return task


@router.put("/{task_id}")
async def update_order_task(
    task_id: str,
    body: OrderTaskUpdate,
    auth: AuthContext = Depends(get_current_org),
) -> OrderTaskResponse:
    """Update an order task."""
    if not is_valid_uuid(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get task with order verification
    task = await get_task_with_order(supabase, task_id, auth.org_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Determine effective values for validation
    effective_for_client = body.for_client if body.for_client is not None else task.get("for_client", False)
    effective_employee_ids = body.employee_ids if body.employee_ids is not None else []

    # Validate mutual exclusion
    if effective_for_client and effective_employee_ids:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "The given data was invalid.",
                "errors": {"for_client": ["Cannot assign employees when for_client is true."]},
            },
        )

    effective_deadline = body.deadline if body.deadline is not None else task.get("deadline")
    effective_due_at = body.due_at if body.due_at is not None else task.get("due_at")

    if effective_deadline is not None and effective_due_at is not None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "The given data was invalid.",
                "errors": {"deadline": ["Cannot specify both deadline and due_at."]},
            },
        )

    # Validate employee_ids
    if body.employee_ids:
        for emp_id in body.employee_ids:
            if not is_valid_uuid(emp_id):
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={
                        "message": "The given data was invalid.",
                        "errors": {"employee_ids": ["All employee_ids must be valid UUIDs."]},
                    },
                )

    # Build update payload
    update_payload: dict[str, Any] = {}

    if body.name is not None:
        update_payload["name"] = body.name.strip()
    if body.description is not None:
        update_payload["description"] = body.description
    if body.sort_order is not None:
        update_payload["sort_order"] = body.sort_order
    if body.is_public is not None:
        update_payload["is_public"] = body.is_public
    if body.for_client is not None:
        update_payload["for_client"] = body.for_client
    if body.deadline is not None:
        update_payload["deadline"] = body.deadline
    if body.due_at is not None:
        update_payload["due_at"] = body.due_at

    # Update task
    if update_payload:
        result = supabase.table("order_tasks").update(update_payload).eq("id", task_id).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task",
            )
        task = result.data[0]

    # Replace employees if provided
    if body.employee_ids is not None:
        supabase.table("order_task_employees").delete().eq("task_id", task_id).execute()
        if body.employee_ids:
            emp_rows = [{"task_id": task_id, "employee_id": e} for e in body.employee_ids]
            supabase.table("order_task_employees").insert(emp_rows).execute()

    # Refetch task for response
    updated = supabase.table("order_tasks").select("*").eq("id", task_id).execute()
    return await serialize_task(supabase, updated.data[0])


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_task(
    task_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> Response:
    """Delete an order task."""
    if not is_valid_uuid(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get task with order verification
    task = await get_task_with_order(supabase, task_id, auth.org_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Delete employee assignments
    supabase.table("order_task_employees").delete().eq("task_id", task_id).execute()

    # Delete task
    supabase.table("order_tasks").delete().eq("id", task_id).execute()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{task_id}/complete", status_code=status.HTTP_200_OK)
async def mark_task_complete(
    task_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> OrderTaskResponse:
    """Mark a task as complete."""
    if not is_valid_uuid(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get task with order verification
    task = await get_task_with_order(supabase, task_id, auth.org_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Update task
    result = (
        supabase.table("order_tasks")
        .update({
            "is_complete": True,
            "completed_by": auth.user_id,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", task_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark task complete",
        )

    return await serialize_task(supabase, result.data[0])


@router.delete("/{task_id}/complete", status_code=status.HTTP_200_OK)
async def mark_task_incomplete(
    task_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> OrderTaskResponse:
    """Mark a task as incomplete."""
    if not is_valid_uuid(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get task with order verification
    task = await get_task_with_order(supabase, task_id, auth.org_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Update task
    result = (
        supabase.table("order_tasks")
        .update({
            "is_complete": False,
            "completed_by": None,
            "completed_at": None,
        })
        .eq("id", task_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark task incomplete",
        )

    return await serialize_task(supabase, result.data[0])
