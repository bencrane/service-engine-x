"""Orders API router."""

import random
import string
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse, Response

from app.auth import AuthContext, get_current_org
from app.config import get_settings
from app.database import get_supabase
from app.models.orders import (
    OrderClientResponse,
    OrderCreate,
    OrderEmployeeResponse,
    OrderResponse,
    OrderUpdate,
)
from app.models.order_tasks import OrderTaskCreate, OrderTaskResponse, TaskEmployeeResponse
from app.models.order_messages import OrderMessageCreate, OrderMessageResponse
from app.models.services import MetadataItem
from app.utils import build_pagination_response, is_valid_uuid

router = APIRouter(prefix="/api/orders", tags=["Orders"])

STATUS_MAP = {
    0: "Unpaid",
    1: "In Progress",
    2: "Completed",
    3: "Cancelled",
    4: "On Hold",
}


def generate_order_number() -> str:
    """Generate a random 8-character order number."""
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(8))


def transform_metadata(metadata: list[MetadataItem] | None) -> dict[str, str]:
    """Transform metadata array to key-value object."""
    if not metadata:
        return {}
    return {item.title: item.value for item in metadata if item.title}


async def fetch_client(supabase, user_id: str) -> OrderClientResponse | None:
    """Fetch client data for an order."""
    result = (
        supabase.table("users")
        .select("id, name_f, name_l, email, company, phone, address_id, role_id, "
                "addresses(id, line_1, line_2, city, state, postcode, country), "
                "roles(id, name)")
        .eq("id", user_id)
        .execute()
    )

    if not result.data or len(result.data) == 0:
        return None

    user = result.data[0]
    addr = user.get("addresses")
    if isinstance(addr, list):
        addr = addr[0] if addr else None
    role = user.get("roles")
    if isinstance(role, list):
        role = role[0] if role else None

    return OrderClientResponse(
        id=user["id"],
        name=f"{user['name_f']} {user['name_l']}".strip(),
        name_f=user["name_f"],
        name_l=user["name_l"],
        email=user["email"],
        company=user.get("company"),
        phone=user.get("phone"),
        address=addr,
        role=role,
    )


async def fetch_order_employees(supabase, order_id: str) -> list[OrderEmployeeResponse]:
    """Fetch employees assigned to an order."""
    assignments = (
        supabase.table("order_employees")
        .select("employee_id")
        .eq("order_id", order_id)
        .execute()
    )

    if not assignments.data:
        return []

    emp_ids = [a["employee_id"] for a in assignments.data]
    employees = (
        supabase.table("users")
        .select("id, name_f, name_l, role_id")
        .in_("id", emp_ids)
        .execute()
    )

    return [
        OrderEmployeeResponse(
            id=e["id"],
            name_f=e.get("name_f"),
            name_l=e.get("name_l"),
            role_id=e.get("role_id"),
        )
        for e in (employees.data or [])
    ]


async def fetch_order_tags(supabase, order_id: str) -> list[str]:
    """Fetch tags for an order."""
    tag_links = (
        supabase.table("order_tags")
        .select("tag_id")
        .eq("order_id", order_id)
        .execute()
    )

    if not tag_links.data:
        return []

    tag_ids = [t["tag_id"] for t in tag_links.data]
    tags = supabase.table("tags").select("name").in_("id", tag_ids).execute()

    return [t["name"] for t in (tags.data or [])]


async def serialize_order(supabase, order: dict[str, Any]) -> OrderResponse:
    """Serialize order with related data."""
    client = await fetch_client(supabase, order["user_id"])
    employees = await fetch_order_employees(supabase, order["id"])
    tags = await fetch_order_tags(supabase, order["id"])

    return OrderResponse(
        id=order["id"],
        number=order["number"],
        created_at=order["created_at"],
        updated_at=order["updated_at"],
        last_message_at=order.get("last_message_at"),
        date_started=order.get("date_started"),
        date_completed=order.get("date_completed"),
        date_due=order.get("date_due"),
        client=client,
        tags=tags,
        status=STATUS_MAP.get(order["status"], "Unknown"),
        status_id=order["status"],
        price=order["price"],
        quantity=order["quantity"],
        invoice_id=order.get("invoice_id"),
        service=order["service_name"],
        service_id=order.get("service_id"),
        user_id=order["user_id"],
        employees=employees,
        note=order.get("note"),
        form_data=order.get("form_data", {}),
        paysys=order.get("paysys"),
    )


async def validate_employees(supabase, employee_ids: list[str]) -> str | None:
    """Validate employee IDs. Returns error message or None."""
    for emp_id in employee_ids:
        if not is_valid_uuid(emp_id):
            return f"Employee with ID {emp_id} does not exist."

        result = (
            supabase.table("users")
            .select("id, role:roles(dashboard_access)")
            .eq("id", emp_id)
            .execute()
        )

        if not result.data or len(result.data) == 0:
            return f"Employee with ID {emp_id} does not exist."

        emp = result.data[0]
        role = emp.get("role")
        if isinstance(role, list):
            role = role[0] if role else None

        if not role or role.get("dashboard_access") == 0:
            return f"Employee with ID {emp_id} does not exist."

    return None


async def assign_tags(supabase, order_id: str, tag_names: list[str]) -> None:
    """Assign tags to an order (find or create)."""
    for tag_name in tag_names:
        # Find existing tag
        existing = supabase.table("tags").select("id").eq("name", tag_name).execute()

        if existing.data and len(existing.data) > 0:
            tag_id = existing.data[0]["id"]
        else:
            # Create new tag
            new_tag = supabase.table("tags").insert({"name": tag_name}).execute()
            if new_tag.data:
                tag_id = new_tag.data[0]["id"]
            else:
                continue

        # Link to order
        supabase.table("order_tags").insert({
            "order_id": order_id,
            "tag_id": tag_id,
        }).execute()


@router.get("")
async def list_orders(
    request: Request,
    auth: AuthContext = Depends(get_current_org),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    sort: str = Query("created_at:desc"),
) -> dict[str, Any]:
    """List all orders for the authenticated organization."""
    supabase = get_supabase()
    settings = get_settings()

    # Parse sort
    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if sort_parts else "created_at"
    sort_dir = sort_parts[1] if len(sort_parts) > 1 else "desc"

    valid_sort = ["id", "number", "status", "price", "quantity", "user_id", "service_id", "created_at", "date_due"]
    if sort_field not in valid_sort:
        sort_field = "created_at"
    ascending = sort_dir == "asc"

    # Get total count
    count_query = (
        supabase.table("orders")
        .select("*", count="exact")
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
    )
    count_result = count_query.execute()
    total = count_result.count or 0

    # Get paginated data
    offset = (page - 1) * limit
    query = (
        supabase.table("orders")
        .select("*")
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .order(sort_field, desc=not ascending)
        .range(offset, offset + limit - 1)
    )

    result = query.execute()
    orders = result.data or []

    # Serialize orders
    serialized = []
    for o in orders:
        order_resp = await serialize_order(supabase, o)
        serialized.append(order_resp.model_dump())

    path = f"{settings.api_base_url}/api/orders"
    return build_pagination_response(serialized, total, page, limit, path)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderCreate,
    auth: AuthContext = Depends(get_current_org),
) -> OrderResponse:
    """Create a new order."""
    supabase = get_supabase()

    # Validate user_id
    if not is_valid_uuid(body.user_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "The given data was invalid.",
                "errors": {"user_id": ["The user_id must be a valid UUID."]},
            },
        )

    # Check user exists
    user_check = supabase.table("users").select("id").eq("id", body.user_id).execute()
    if not user_check.data or len(user_check.data) == 0:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "The given data was invalid.",
                "errors": {"user_id": ["The specified client does not exist."]},
            },
        )

    # Require service_id or service
    if not body.service_id and not body.service:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "The given data was invalid.",
                "errors": {"service": ["Either service_id or service must be provided."]},
            },
        )

    # Snapshot from service
    service_name = body.service or "Custom Order"
    price = "0.00"
    currency = "USD"

    if body.service_id:
        if not is_valid_uuid(body.service_id):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"service_id": ["The specified service does not exist."]},
                },
            )

        svc = (
            supabase.table("services")
            .select("id, name, price, currency")
            .eq("id", body.service_id)
            .is_("deleted_at", "null")
            .execute()
        )

        if not svc.data or len(svc.data) == 0:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"service_id": ["The specified service does not exist."]},
                },
            )

        service_name = body.service or svc.data[0]["name"]
        price = svc.data[0].get("price") or "0.00"
        currency = svc.data[0].get("currency") or "USD"

    # Validate employees
    if body.employees:
        error = await validate_employees(supabase, body.employees)
        if error:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"employees": [error]},
                },
            )

    # Check unique number
    order_number = body.number or generate_order_number()
    if body.number:
        existing = supabase.table("orders").select("id").eq("number", body.number).execute()
        if existing.data and len(existing.data) > 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"number": ["The order number has already been taken."]},
                },
            )

    # Create order
    order_data = {
        "org_id": auth.org_id,
        "number": order_number,
        "user_id": body.user_id,
        "service_id": body.service_id,
        "service_name": service_name,
        "price": price,
        "currency": currency,
        "quantity": 1,
        "status": body.status if body.status is not None else 0,
        "note": body.note,
        "form_data": {},
        "metadata": transform_metadata(body.metadata),
        "created_at": body.created_at or datetime.now(timezone.utc).isoformat(),
        "date_started": body.date_started,
        "date_completed": body.date_completed,
        "date_due": body.date_due,
    }

    result = supabase.table("orders").insert(order_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order",
        )

    new_order = result.data[0]

    # Assign employees
    if body.employees:
        emp_rows = [{"order_id": new_order["id"], "employee_id": e} for e in body.employees]
        supabase.table("order_employees").insert(emp_rows).execute()

    # Assign tags
    if body.tags:
        await assign_tags(supabase, new_order["id"], body.tags)

    return await serialize_order(supabase, new_order)


@router.get("/{order_id}")
async def retrieve_order(
    order_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> OrderResponse:
    """Retrieve a single order by ID."""
    if not is_valid_uuid(order_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    result = (
        supabase.table("orders")
        .select("*")
        .eq("id", order_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    return await serialize_order(supabase, result.data[0])


@router.put("/{order_id}")
async def update_order(
    order_id: str,
    body: OrderUpdate,
    auth: AuthContext = Depends(get_current_org),
) -> OrderResponse:
    """Update an existing order."""
    if not is_valid_uuid(order_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get existing
    existing = (
        supabase.table("orders")
        .select("*")
        .eq("id", order_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not existing.data or len(existing.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Validate service_id if provided
    if body.service_id is not None:
        if body.service_id and not is_valid_uuid(body.service_id):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"service_id": ["The specified service does not exist."]},
                },
            )

        if body.service_id:
            svc = (
                supabase.table("services")
                .select("id")
                .eq("id", body.service_id)
                .is_("deleted_at", "null")
                .execute()
            )
            if not svc.data or len(svc.data) == 0:
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={
                        "message": "The given data was invalid.",
                        "errors": {"service_id": ["The specified service does not exist."]},
                    },
                )

    # Validate employees
    if body.employees is not None:
        error = await validate_employees(supabase, body.employees)
        if error:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"employees": [error]},
                },
            )

    # Build update payload
    update_payload: dict[str, Any] = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    if body.service_id is not None:
        update_payload["service_id"] = body.service_id if body.service_id else None
    if body.service is not None:
        update_payload["service_name"] = body.service
    if body.status is not None:
        update_payload["status"] = body.status
    if body.note is not None:
        update_payload["note"] = body.note
    if body.metadata is not None:
        update_payload["metadata"] = transform_metadata(body.metadata)
    if body.date_started is not None:
        update_payload["date_started"] = body.date_started
    if body.date_completed is not None:
        update_payload["date_completed"] = body.date_completed
    if body.date_due is not None:
        update_payload["date_due"] = body.date_due

    # Update order
    result = supabase.table("orders").update(update_payload).eq("id", order_id).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order",
        )

    # Replace employees if provided
    if body.employees is not None:
        supabase.table("order_employees").delete().eq("order_id", order_id).execute()
        if body.employees:
            emp_rows = [{"order_id": order_id, "employee_id": e} for e in body.employees]
            supabase.table("order_employees").insert(emp_rows).execute()

    # Replace tags if provided
    if body.tags is not None:
        supabase.table("order_tags").delete().eq("order_id", order_id).execute()
        if body.tags:
            await assign_tags(supabase, order_id, body.tags)

    return await serialize_order(supabase, result.data[0])


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> Response:
    """Soft delete an order."""
    if not is_valid_uuid(order_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    existing = (
        supabase.table("orders")
        .select("id")
        .eq("id", order_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not existing.data or len(existing.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase.table("orders").update(
        {"deleted_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", order_id).execute()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# =============================================================================
# Nested: Order Tasks
# =============================================================================

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


@router.get("/{order_id}/tasks")
async def list_order_tasks(
    order_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> list[OrderTaskResponse]:
    """List all tasks for an order."""
    if not is_valid_uuid(order_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify order exists
    order = (
        supabase.table("orders")
        .select("id")
        .eq("id", order_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not order.data or len(order.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Get tasks
    tasks = (
        supabase.table("order_tasks")
        .select("*")
        .eq("order_id", order_id)
        .order("sort_order")
        .execute()
    )

    result = []
    for t in (tasks.data or []):
        result.append(await serialize_task(supabase, t))

    return result


@router.post("/{order_id}/tasks", status_code=status.HTTP_201_CREATED)
async def create_order_task(
    order_id: str,
    body: OrderTaskCreate,
    auth: AuthContext = Depends(get_current_org),
) -> OrderTaskResponse:
    """Create a task for an order."""
    if not is_valid_uuid(order_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify order exists
    order = (
        supabase.table("orders")
        .select("id")
        .eq("id", order_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not order.data or len(order.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Validate mutual exclusion
    if body.for_client and body.employee_ids:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "The given data was invalid.",
                "errors": {"for_client": ["Cannot assign employees when for_client is true."]},
            },
        )

    if body.deadline is not None and body.due_at is not None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "The given data was invalid.",
                "errors": {"deadline": ["Cannot specify both deadline and due_at."]},
            },
        )

    # Validate employees
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

    # Create task
    task_data = {
        "order_id": order_id,
        "name": body.name.strip(),
        "description": body.description,
        "sort_order": body.sort_order or 0,
        "is_public": body.is_public,
        "for_client": body.for_client,
        "is_complete": False,
        "deadline": body.deadline,
        "due_at": body.due_at,
    }

    result = supabase.table("order_tasks").insert(task_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task",
        )

    new_task = result.data[0]

    # Assign employees
    if body.employee_ids:
        emp_rows = [{"task_id": new_task["id"], "employee_id": e} for e in body.employee_ids]
        supabase.table("order_task_employees").insert(emp_rows).execute()

    return await serialize_task(supabase, new_task)


# =============================================================================
# Nested: Order Messages
# =============================================================================

@router.get("/{order_id}/messages")
async def list_order_messages(
    order_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> list[OrderMessageResponse]:
    """List all messages for an order."""
    if not is_valid_uuid(order_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify order exists
    order = (
        supabase.table("orders")
        .select("id")
        .eq("id", order_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not order.data or len(order.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Get messages
    messages = (
        supabase.table("order_messages")
        .select("*, user:users(id, name_f, name_l, email)")
        .eq("order_id", order_id)
        .order("created_at")
        .execute()
    )

    result = []
    for m in (messages.data or []):
        user_data = m.get("user")
        if isinstance(user_data, list):
            user_data = user_data[0] if user_data else None

        result.append(OrderMessageResponse(
            id=m["id"],
            order_id=m["order_id"],
            user_id=m.get("user_id"),
            message=m["message"],
            is_public=m.get("is_public", True),
            created_at=m["created_at"],
            user=user_data,
        ))

    return result


@router.post("/{order_id}/messages", status_code=status.HTTP_201_CREATED)
async def create_order_message(
    order_id: str,
    body: OrderMessageCreate,
    auth: AuthContext = Depends(get_current_org),
) -> OrderMessageResponse:
    """Create a message for an order."""
    if not is_valid_uuid(order_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify order exists
    order = (
        supabase.table("orders")
        .select("id")
        .eq("id", order_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not order.data or len(order.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Create message
    msg_data = {
        "order_id": order_id,
        "user_id": auth.user_id,
        "message": body.message.strip(),
        "is_public": body.is_public,
    }

    result = supabase.table("order_messages").insert(msg_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create message",
        )

    new_msg = result.data[0]

    # Update order's last_message_at
    supabase.table("orders").update(
        {"last_message_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", order_id).execute()

    return OrderMessageResponse(
        id=new_msg["id"],
        order_id=new_msg["order_id"],
        user_id=new_msg.get("user_id"),
        message=new_msg["message"],
        is_public=new_msg.get("is_public", True),
        created_at=new_msg["created_at"],
        user=None,
    )
