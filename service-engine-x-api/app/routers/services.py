"""Services API router."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse, Response

from app.auth import AuthContext, get_current_org
from app.config import get_settings
from app.database import get_supabase
from app.models.services import (
    MetadataItem,
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)
from app.utils import build_pagination_response, is_valid_uuid

router = APIRouter(prefix="/api/services", tags=["Services"])

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "CAD": "CA$",
    "AUD": "A$",
}


def format_pretty_price(price: str | None, currency: str) -> str:
    """Format price with currency symbol."""
    num_price = float(price or "0")
    symbol = CURRENCY_SYMBOLS.get(currency, f"{currency} ")
    return f"{symbol}{num_price:.2f}"


def transform_metadata(metadata: list[MetadataItem] | None) -> dict[str, str]:
    """Transform metadata array to key-value object."""
    if not metadata:
        return {}
    return {item.title: item.value for item in metadata if item.title}


def serialize_service(service: dict[str, Any]) -> ServiceResponse:
    """Serialize service data to response model."""
    return ServiceResponse(
        id=service["id"],
        name=service["name"],
        description=service.get("description"),
        image=service.get("image"),
        recurring=service["recurring"],
        price=service.get("price"),
        pretty_price=format_pretty_price(service.get("price"), service["currency"]),
        currency=service["currency"],
        f_price=service.get("f_price"),
        f_period_l=service.get("f_period_l"),
        f_period_t=service.get("f_period_t"),
        r_price=service.get("r_price"),
        r_period_l=service.get("r_period_l"),
        r_period_t=service.get("r_period_t"),
        recurring_action=service.get("recurring_action"),
        multi_order=service.get("multi_order", True),
        request_orders=service.get("request_orders", False),
        max_active_requests=service.get("max_active_requests"),
        deadline=service.get("deadline"),
        public=service.get("public", True),
        sort_order=service.get("sort_order", 0),
        group_quantities=service.get("group_quantities", False),
        folder_id=service.get("folder_id"),
        metadata=service.get("metadata", {}),
        braintree_plan_id=service.get("braintree_plan_id"),
        hoth_product_key=service.get("hoth_product_key"),
        hoth_package_name=service.get("hoth_package_name"),
        provider_id=service.get("provider_id"),
        provider_service_id=service.get("provider_service_id"),
        created_at=service["created_at"],
        updated_at=service["updated_at"],
    )


async def validate_employees(supabase, employee_ids: list[str]) -> str | None:
    """Validate employee IDs exist and have dashboard access. Returns error message or None."""
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


@router.get("")
async def list_services(
    request: Request,
    auth: AuthContext = Depends(get_current_org),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    sort: str = Query("created_at:desc"),
) -> dict[str, Any]:
    """
    List all services for the authenticated organization.

    Supports pagination, sorting, and filtering.
    """
    supabase = get_supabase()
    settings = get_settings()

    # Parse sort parameter
    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if sort_parts else "created_at"
    sort_dir = sort_parts[1] if len(sort_parts) > 1 else "desc"

    valid_sort_fields = ["id", "name", "price", "recurring", "public", "sort_order", "created_at"]
    if sort_field not in valid_sort_fields:
        sort_field = "created_at"
    ascending = sort_dir == "asc"

    # Build base query for count
    query = (
        supabase.table("services")
        .select("*", count="exact")
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
    )

    # Apply filters from query params
    filterable = ["id", "name", "recurring", "public", "price", "currency", "folder_id", "created_at"]
    for key, value in request.query_params.items():
        if key.startswith("filters["):
            import re
            match = re.match(r"filters\[(\w+)\]\[(\$\w+)\]", key)
            if match:
                field, op = match.groups()
                if field not in filterable:
                    continue
                if op == "$eq":
                    if value == "null":
                        query = query.is_(field, "null")
                    elif value in ("true", "false"):
                        query = query.eq(field, value == "true")
                    else:
                        query = query.eq(field, value)
                elif op == "$lt":
                    query = query.lt(field, value)
                elif op == "$gt":
                    query = query.gt(field, value)
                elif op == "$in":
                    values = request.query_params.getlist(f"filters[{field}][$in][]")
                    if values:
                        query = query.in_(field, values)

    # Get total count
    count_result = query.execute()
    total = count_result.count or 0

    # Build paginated query
    offset = (page - 1) * limit
    query = (
        supabase.table("services")
        .select("*")
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .order(sort_field, desc=not ascending)
        .range(offset, offset + limit - 1)
    )

    result = query.execute()
    services = result.data or []

    # Serialize services
    serialized = [serialize_service(s).model_dump() for s in services]

    # Build pagination response
    path = f"{settings.api_base_url}/api/services"
    return build_pagination_response(serialized, total, page, limit, path)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_service(
    body: ServiceCreate,
    auth: AuthContext = Depends(get_current_org),
) -> ServiceResponse:
    """Create a new service."""
    supabase = get_supabase()

    # Validate folder_id if provided
    if body.folder_id:
        if not is_valid_uuid(body.folder_id):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"folder_id": ["The specified folder does not exist."]},
                },
            )

        folder_result = (
            supabase.table("service_folders")
            .select("id")
            .eq("id", body.folder_id)
            .execute()
        )
        if not folder_result.data or len(folder_result.data) == 0:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"folder_id": ["The specified folder does not exist."]},
                },
            )

    # Validate employees if provided
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

    # Transform metadata
    metadata_obj = transform_metadata(body.metadata)

    # Create service
    service_data = {
        "org_id": auth.org_id,
        "name": body.name.strip(),
        "description": body.description,
        "recurring": body.recurring,
        "currency": body.currency.upper().strip(),
        "price": body.price,
        "f_price": body.f_price,
        "f_period_l": body.f_period_l,
        "f_period_t": body.f_period_t,
        "r_price": body.r_price,
        "r_period_l": body.r_period_l,
        "r_period_t": body.r_period_t,
        "recurring_action": body.recurring_action,
        "deadline": body.deadline,
        "public": body.public,
        "multi_order": body.multi_order,
        "request_orders": body.request_orders,
        "max_active_requests": body.max_active_requests,
        "group_quantities": body.group_quantities,
        "folder_id": body.folder_id,
        "metadata": metadata_obj,
        "braintree_plan_id": body.braintree_plan_id,
        "hoth_product_key": body.hoth_product_key,
        "hoth_package_name": body.hoth_package_name,
        "provider_id": body.provider_id,
        "provider_service_id": body.provider_service_id,
    }

    result = supabase.table("services").insert(service_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create service",
        )

    new_service = result.data[0]

    # Assign employees if provided
    if body.employees and len(body.employees) > 0:
        employee_rows = [
            {"service_id": new_service["id"], "employee_id": emp_id}
            for emp_id in body.employees
        ]
        emp_result = supabase.table("service_employees").insert(employee_rows).execute()

        if not emp_result.data:
            # Cleanup service on failure
            supabase.table("services").delete().eq("id", new_service["id"]).execute()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to assign employees",
            )

    return serialize_service(new_service)


@router.get("/{service_id}")
async def retrieve_service(
    service_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> ServiceResponse:
    """Retrieve a single service by ID."""
    if not is_valid_uuid(service_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    result = (
        supabase.table("services")
        .select("*")
        .eq("id", service_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    return serialize_service(result.data[0])


@router.put("/{service_id}")
async def update_service(
    service_id: str,
    body: ServiceUpdate,
    auth: AuthContext = Depends(get_current_org),
) -> ServiceResponse:
    """Update an existing service."""
    if not is_valid_uuid(service_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Get existing service
    existing_result = (
        supabase.table("services")
        .select("*")
        .eq("id", service_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not existing_result.data or len(existing_result.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Validate folder_id if provided
    if body.folder_id is not None and body.folder_id != "":
        if not is_valid_uuid(body.folder_id):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"folder_id": ["The specified folder does not exist."]},
                },
            )

        folder_result = (
            supabase.table("service_folders")
            .select("id")
            .eq("id", body.folder_id)
            .execute()
        )
        if not folder_result.data or len(folder_result.data) == 0:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "message": "The given data was invalid.",
                    "errors": {"folder_id": ["The specified folder does not exist."]},
                },
            )

    # Validate employees if provided
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

    if body.name is not None:
        update_payload["name"] = body.name.strip()
    if body.description is not None:
        update_payload["description"] = body.description
    if body.recurring is not None:
        update_payload["recurring"] = body.recurring
    if body.currency is not None:
        update_payload["currency"] = body.currency.upper().strip()
    if body.price is not None:
        update_payload["price"] = body.price
    if body.f_price is not None:
        update_payload["f_price"] = body.f_price
    if body.f_period_l is not None:
        update_payload["f_period_l"] = body.f_period_l
    if body.f_period_t is not None:
        update_payload["f_period_t"] = body.f_period_t
    if body.r_price is not None:
        update_payload["r_price"] = body.r_price
    if body.r_period_l is not None:
        update_payload["r_period_l"] = body.r_period_l
    if body.r_period_t is not None:
        update_payload["r_period_t"] = body.r_period_t
    if body.recurring_action is not None:
        update_payload["recurring_action"] = body.recurring_action
    if body.deadline is not None:
        update_payload["deadline"] = body.deadline
    if body.public is not None:
        update_payload["public"] = body.public
    if body.multi_order is not None:
        update_payload["multi_order"] = body.multi_order
    if body.request_orders is not None:
        update_payload["request_orders"] = body.request_orders
    if body.max_active_requests is not None:
        update_payload["max_active_requests"] = body.max_active_requests
    if body.group_quantities is not None:
        update_payload["group_quantities"] = body.group_quantities
    if body.folder_id is not None:
        update_payload["folder_id"] = body.folder_id if body.folder_id else None
    if body.sort_order is not None:
        update_payload["sort_order"] = body.sort_order
    if body.braintree_plan_id is not None:
        update_payload["braintree_plan_id"] = body.braintree_plan_id
    if body.hoth_product_key is not None:
        update_payload["hoth_product_key"] = body.hoth_product_key
    if body.hoth_package_name is not None:
        update_payload["hoth_package_name"] = body.hoth_package_name
    if body.provider_id is not None:
        update_payload["provider_id"] = body.provider_id
    if body.provider_service_id is not None:
        update_payload["provider_service_id"] = body.provider_service_id

    if body.metadata is not None:
        update_payload["metadata"] = transform_metadata(body.metadata)

    # Update service
    result = (
        supabase.table("services")
        .update(update_payload)
        .eq("id", service_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update service",
        )

    # Update employees if provided
    if body.employees is not None:
        # Remove existing assignments
        supabase.table("service_employees").delete().eq("service_id", service_id).execute()

        # Add new assignments
        if len(body.employees) > 0:
            employee_rows = [
                {"service_id": service_id, "employee_id": emp_id}
                for emp_id in body.employees
            ]
            supabase.table("service_employees").insert(employee_rows).execute()

    return serialize_service(result.data[0])


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: str,
    auth: AuthContext = Depends(get_current_org),
) -> Response:
    """Soft delete a service."""
    if not is_valid_uuid(service_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    supabase = get_supabase()

    # Verify service exists and belongs to org
    existing = (
        supabase.table("services")
        .select("id")
        .eq("id", service_id)
        .eq("org_id", auth.org_id)
        .is_("deleted_at", "null")
        .execute()
    )

    if not existing.data or len(existing.data) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    # Soft delete
    supabase.table("services").update(
        {"deleted_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", service_id).execute()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
