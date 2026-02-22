# Multi-Tenant Architecture Guide

This document defines the multi-tenant architecture patterns used in this system. It serves as a canonical reference for building tenant-isolated SaaS applications.

---

## Table of Contents

1. [Core Concepts](#1-core-concepts)
2. [Database Design](#2-database-design)
3. [Authentication & Tenant Context](#3-authentication--tenant-context)
4. [Query Patterns](#4-query-patterns)
5. [API Implementation](#5-api-implementation)
6. [Nested Resources](#6-nested-resources)
7. [Common Patterns](#7-common-patterns)
8. [Security Checklist](#8-security-checklist)

---

## 1. Core Concepts

### What is Multi-Tenancy?

Multi-tenancy allows a single application instance to serve multiple isolated customers (tenants). Each tenant's data is logically separated, ensuring they can only access their own records.

### Tenant Isolation Model

This system uses **row-level isolation** with an `org_id` column:

```
┌─────────────────────────────────────────────────────────┐
│                    Single Database                       │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Org A     │  │   Org B     │  │   Org C     │     │
│  │  org_id=1   │  │  org_id=2   │  │  org_id=3   │     │
│  │             │  │             │  │             │     │
│  │ - accounts  │  │ - accounts  │  │ - accounts  │     │
│  │ - contacts  │  │ - contacts  │  │ - contacts  │     │
│  │ - orders    │  │ - orders    │  │ - orders    │     │
│  │ - invoices  │  │ - invoices  │  │ - invoices  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### Key Principle

> **Every database query must filter by `org_id`.**

This is non-negotiable. A query without `org_id` filtering is a data breach waiting to happen.

---

## 2. Database Design

### The `org_id` Column

Every tenant-scoped table must include:

```sql
org_id UUID NOT NULL REFERENCES organizations(id)
```

**Index it:**
```sql
CREATE INDEX idx_tablename_org_id ON tablename(org_id);
```

### Example Schema

```sql
-- Top-level entity
CREATE TABLE accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  name VARCHAR(255) NOT NULL,
  domain VARCHAR(255),
  lifecycle INTEGER NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_accounts_org_id ON accounts(org_id);

-- Child entity (still has org_id for query efficiency)
CREATE TABLE contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  account_id UUID REFERENCES accounts(id),
  name_f VARCHAR(100),
  name_l VARCHAR(100),
  email VARCHAR(255),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_contacts_org_id ON contacts(org_id);
CREATE INDEX idx_contacts_account_id ON contacts(account_id);
```

### Denormalization Strategy

Child tables include `org_id` even when they reference a parent that already has it:

| Table | Parent | Has own `org_id`? | Why? |
|-------|--------|-------------------|------|
| `accounts` | organizations | Yes | Primary tenant key |
| `contacts` | accounts | Yes | Query efficiency, direct filtering |
| `orders` | accounts | Yes | Query efficiency, direct filtering |
| `order_tasks` | orders | Yes | Can query tasks directly by org |
| `order_messages` | orders | Yes | Can query messages directly by org |

**Benefits:**
- No joins required just to filter by tenant
- Simpler queries
- Better index utilization
- Defense in depth (multiple isolation points)

### Cascade Behavior

Define explicit cascade rules for tenant consistency:

| Parent | Child | On Delete |
|--------|-------|-----------|
| accounts | contacts | CASCADE (contacts belong to account) |
| accounts | orders | SET NULL (orders are financial records) |
| orders | order_tasks | CASCADE |
| orders | order_messages | CASCADE |

---

## 3. Authentication & Tenant Context

### The AuthContext Pattern

Create a context object that carries tenant identity through the request:

```python
from dataclasses import dataclass

@dataclass
class AuthContext:
    """Authentication context containing org and user info."""
    org_id: str      # The tenant identifier
    user_id: str     # The authenticated user
    token_id: str | None = None
    auth_method: str = "api_token"  # "api_token" or "session"
```

### Extracting Tenant from Authentication

**From API Token (machine-to-machine):**
```python
def _validate_api_token(token: str) -> AuthContext | None:
    token_hash = hash_token(token)

    result = (
        supabase.table("api_tokens")
        .select("id, user_id, org_id, expires_at")
        .eq("token_hash", token_hash)
        .execute()
    )

    if not result.data:
        return None

    token_data = result.data[0]

    # Check expiration
    if token_data.get("expires_at"):
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        if expires_at < datetime.now(timezone.utc):
            return None

    return AuthContext(
        org_id=token_data["org_id"],
        user_id=token_data["user_id"],
        token_id=token_data["id"],
        auth_method="api_token",
    )
```

**From JWT Session (user login):**
```python
def _validate_jwt(token: str) -> AuthContext | None:
    try:
        payload = decode_access_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

    if payload.get("type") != "session":
        return None

    user_id = payload.get("sub")
    org_id = payload.get("org_id")  # org_id embedded in JWT

    if not user_id or not org_id:
        return None

    return AuthContext(
        org_id=org_id,
        user_id=user_id,
        auth_method="session",
    )
```

### Dependency Injection

Use framework dependency injection to ensure every endpoint receives tenant context:

```python
from fastapi import Depends

async def get_current_auth(
    authorization: str | None = Header(None),
) -> AuthContext:
    """Validate token and return auth context."""
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Try JWT first (no DB call)
    auth = _validate_jwt(token)
    if auth:
        return auth

    # Fall back to API token
    auth = _validate_api_token(token)
    if auth:
        return auth

    raise HTTPException(status_code=401, detail="Unauthorized")
```

---

## 4. Query Patterns

### The Cardinal Rule

Every query that accesses tenant data must include:

```python
.eq("org_id", auth.org_id)
```

### List Endpoint Pattern

```python
@router.get("")
async def list_resources(
    auth: AuthContext = Depends(get_current_auth),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    # Count query - includes org_id
    count_query = (
        supabase.table("resources")
        .select("*", count="exact")
        .eq("org_id", auth.org_id)           # <-- REQUIRED
        .is_("deleted_at", "null")           # Exclude soft-deleted
    )

    count_result = count_query.execute()
    total = count_result.count or 0

    # Data query - includes org_id
    offset = (page - 1) * limit
    data_query = (
        supabase.table("resources")
        .select("*")
        .eq("org_id", auth.org_id)           # <-- REQUIRED
        .is_("deleted_at", "null")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
    )

    result = data_query.execute()
    return build_pagination_response(result.data, total, page, limit)
```

### Retrieve Endpoint Pattern

```python
@router.get("/{resource_id}")
async def retrieve_resource(
    resource_id: str,
    auth: AuthContext = Depends(get_current_auth),
):
    result = (
        supabase.table("resources")
        .select("*")
        .eq("id", resource_id)
        .eq("org_id", auth.org_id)           # <-- REQUIRED
        .is_("deleted_at", "null")
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Not Found")

    return result.data[0]
```

### Create Endpoint Pattern

```python
@router.post("")
async def create_resource(
    body: ResourceCreate,
    auth: AuthContext = Depends(get_current_auth),
):
    # Always set org_id from auth context, never from request body
    resource_data = {
        "org_id": auth.org_id,               # <-- SET FROM AUTH
        "name": body.name,
        "description": body.description,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = supabase.table("resources").insert(resource_data).execute()
    return result.data[0]
```

### Update Endpoint Pattern

```python
@router.put("/{resource_id}")
async def update_resource(
    resource_id: str,
    body: ResourceUpdate,
    auth: AuthContext = Depends(get_current_auth),
):
    # First verify resource exists and belongs to this org
    existing = (
        supabase.table("resources")
        .select("*")
        .eq("id", resource_id)
        .eq("org_id", auth.org_id)           # <-- REQUIRED
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=404, detail="Not Found")

    # Update with org_id filter (defense in depth)
    result = (
        supabase.table("resources")
        .update({"name": body.name, "updated_at": datetime.now().isoformat()})
        .eq("id", resource_id)
        .eq("org_id", auth.org_id)           # <-- REQUIRED (again!)
        .execute()
    )

    return result.data[0]
```

### Delete Endpoint Pattern

```python
@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: str,
    auth: AuthContext = Depends(get_current_auth),
):
    # Verify ownership
    existing = (
        supabase.table("resources")
        .select("id")
        .eq("id", resource_id)
        .eq("org_id", auth.org_id)           # <-- REQUIRED
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=404, detail="Not Found")

    # Soft delete with org_id filter
    supabase.table("resources").update({
        "deleted_at": datetime.now(timezone.utc).isoformat()
    }).eq("id", resource_id).eq("org_id", auth.org_id).execute()

    return Response(status_code=204)
```

---

## 5. API Implementation

### Router Structure

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/resources", tags=["Resources"])

@router.get("")
async def list_resources(auth: AuthContext = Depends(get_current_auth)):
    ...

@router.post("")
async def create_resource(auth: AuthContext = Depends(get_current_auth)):
    ...

@router.get("/{id}")
async def retrieve_resource(auth: AuthContext = Depends(get_current_auth)):
    ...

@router.put("/{id}")
async def update_resource(auth: AuthContext = Depends(get_current_auth)):
    ...

@router.delete("/{id}")
async def delete_resource(auth: AuthContext = Depends(get_current_auth)):
    ...
```

### Validating Related Resources

When creating/updating records that reference other tables, validate those references are within the same org:

```python
@router.post("/orders")
async def create_order(
    body: OrderCreate,
    auth: AuthContext = Depends(get_current_auth),
):
    # Validate client belongs to this org
    client = (
        supabase.table("users")
        .select("id")
        .eq("id", body.client_id)
        .eq("org_id", auth.org_id)           # <-- Validates within org
        .execute()
    )

    if not client.data:
        raise HTTPException(status_code=400, detail="Invalid client_id")

    # Validate service belongs to this org
    if body.service_id:
        service = (
            supabase.table("services")
            .select("id, name, price")
            .eq("id", body.service_id)
            .eq("org_id", auth.org_id)       # <-- Validates within org
            .execute()
        )

        if not service.data:
            raise HTTPException(status_code=400, detail="Invalid service_id")

    # Validate employees belong to this org
    if body.employee_ids:
        employees = (
            supabase.table("users")
            .select("id")
            .in_("id", body.employee_ids)
            .eq("org_id", auth.org_id)       # <-- Validates within org
            .gt("dashboard_access", 0)        # Must be team member
            .execute()
        )

        if len(employees.data) != len(body.employee_ids):
            raise HTTPException(status_code=400, detail="Invalid employee_ids")

    # Now safe to create the order
    ...
```

---

## 6. Nested Resources

### Parent-Child Relationships

For nested resources (e.g., `/orders/{order_id}/tasks`), always verify the parent belongs to the org:

```python
@router.get("/{order_id}/tasks")
async def list_order_tasks(
    order_id: str,
    auth: AuthContext = Depends(get_current_auth),
):
    # Verify order belongs to this org
    order = (
        supabase.table("orders")
        .select("id")
        .eq("id", order_id)
        .eq("org_id", auth.org_id)           # <-- Parent validation
        .is_("deleted_at", "null")
        .execute()
    )

    if not order.data:
        raise HTTPException(status_code=404, detail="Order not found")

    # Now fetch tasks (can also filter by org_id for defense in depth)
    tasks = (
        supabase.table("order_tasks")
        .select("*")
        .eq("order_id", order_id)
        .eq("org_id", auth.org_id)           # <-- Defense in depth
        .execute()
    )

    return tasks.data
```

### Standalone Child Operations

When operating directly on child resources (e.g., `PUT /api/order-tasks/{id}`), verify the parent chain:

```python
@router.put("/{task_id}")
async def update_task(
    task_id: str,
    body: TaskUpdate,
    auth: AuthContext = Depends(get_current_auth),
):
    # Get task and verify org
    task = (
        supabase.table("order_tasks")
        .select("*, order:orders(id, org_id, deleted_at)")
        .eq("id", task_id)
        .execute()
    )

    if not task.data:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task.data[0]
    order = task_data.get("order")

    # Verify parent order belongs to this org and isn't deleted
    if not order or order["org_id"] != auth.org_id:
        raise HTTPException(status_code=404, detail="Task not found")

    if order.get("deleted_at"):
        raise HTTPException(status_code=404, detail="Order has been deleted")

    # Now safe to update
    ...
```

---

## 7. Common Patterns

### Soft Delete

Use `deleted_at` timestamp instead of hard deletes:

```python
# Soft delete
supabase.table("resources").update({
    "deleted_at": datetime.now(timezone.utc).isoformat()
}).eq("id", resource_id).eq("org_id", auth.org_id).execute()

# All queries must exclude soft-deleted records
.is_("deleted_at", "null")
```

### Junction Tables

For many-to-many relationships, include `org_id` on junction tables:

```sql
CREATE TABLE order_employees (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  employee_id UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(order_id, employee_id)
);

CREATE INDEX idx_order_employees_org_id ON order_employees(org_id);
```

**Update pattern (full replacement):**
```python
# Delete existing assignments
supabase.table("order_employees").delete().eq("order_id", order_id).execute()

# Insert new assignments
for employee_id in body.employee_ids:
    supabase.table("order_employees").insert({
        "org_id": auth.org_id,
        "order_id": order_id,
        "employee_id": employee_id,
    }).execute()
```

### Find-or-Create Tags

```python
def get_or_create_tag(supabase, org_id: str, tag_name: str) -> str:
    """Get existing tag or create new one. Returns tag ID."""
    # Try to find existing
    existing = (
        supabase.table("tags")
        .select("id")
        .eq("org_id", org_id)
        .eq("name", tag_name)
        .execute()
    )

    if existing.data:
        return existing.data[0]["id"]

    # Create new tag
    result = supabase.table("tags").insert({
        "org_id": org_id,
        "name": tag_name,
    }).execute()

    return result.data[0]["id"]
```

### Status Maps

Use integer IDs internally, return friendly labels in API:

```python
STATUS_MAP = {
    0: "Unpaid",
    1: "In Progress",
    2: "Completed",
    3: "Cancelled",
    4: "On Hold",
}

# In serialization
def serialize_order(order: dict) -> dict:
    return {
        "id": order["id"],
        "status_id": order["status"],
        "status": STATUS_MAP.get(order["status"], "Unknown"),
        ...
    }
```

---

## 8. Security Checklist

Use this checklist when implementing or reviewing multi-tenant code:

### Database Layer
- [ ] Every tenant-scoped table has `org_id` column
- [ ] `org_id` column has NOT NULL constraint
- [ ] `org_id` column has foreign key to organizations
- [ ] Index exists on `org_id` for all tenant tables
- [ ] Child tables have denormalized `org_id` for query efficiency

### Authentication Layer
- [ ] AuthContext includes `org_id`
- [ ] Token validation extracts `org_id` from token/JWT
- [ ] All endpoints require authentication dependency
- [ ] No endpoint allows `org_id` to be passed in request body

### Query Layer
- [ ] All SELECT queries filter by `org_id`
- [ ] All UPDATE queries filter by `org_id`
- [ ] All DELETE queries filter by `org_id`
- [ ] INSERT operations set `org_id` from auth context
- [ ] Soft-deleted records are excluded (`.is_("deleted_at", "null")`)

### Relationship Validation
- [ ] Related resource IDs are validated within the same org
- [ ] Parent resources are verified before child operations
- [ ] Junction table operations include `org_id`

### Response Layer
- [ ] No `org_id` leaked in API responses (or intentionally included)
- [ ] Error messages don't reveal existence of other org's data

### Testing
- [ ] Tests verify 401 for unauthenticated requests
- [ ] Tests verify 404 for accessing another org's resources
- [ ] Tests verify resources are created with correct `org_id`

---

## Summary

| Layer | Responsibility |
|-------|----------------|
| **Database** | `org_id` column + index on every tenant table |
| **Authentication** | Extract `org_id` into AuthContext from token |
| **Dependency Injection** | Pass AuthContext to every endpoint |
| **Queries** | Filter by `org_id` on every operation |
| **Validation** | Verify related resources belong to same org |
| **Testing** | Verify isolation between orgs |

The system is only as secure as its weakest query. **Every query must filter by `org_id`.**
