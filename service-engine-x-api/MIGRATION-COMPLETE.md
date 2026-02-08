# Service Engine X: FastAPI Migration Complete

**Project:** Service Engine X API Migration
**From:** Next.js API Routes
**To:** FastAPI (Python)
**Completed:** 2026-02-07
**Total Commits:** 6 phases

---

## Executive Summary

Successfully migrated the Service Engine X REST API from Next.js to FastAPI. The migration preserved all existing functionality while adding type safety, automatic OpenAPI documentation, and improved multi-tenant security patterns.

### Key Metrics

| Metric | Value |
|--------|-------|
| Total API Endpoints | 43 |
| Test Coverage | 45 tests |
| Model Files | 10 |
| Router Files | 10 |
| Lines of Python | ~6,500 |
| Migration Phases | 6 |

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Phase-by-Phase Breakdown](#phase-by-phase-breakdown)
4. [API Reference](#api-reference)
5. [Database Schema](#database-schema)
6. [Authentication](#authentication)
7. [Key Patterns](#key-patterns)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Files Created](#files-created)

---

## Project Overview

### Background

Service Engine X is a multi-tenant SaaS platform for service businesses. The original API was built with Next.js API routes. This migration moved all API functionality to a dedicated FastAPI backend for:

- **Separation of concerns** - Dedicated API service
- **Type safety** - Pydantic models with validation
- **Performance** - Async Python with uvicorn
- **Documentation** - Auto-generated OpenAPI/Swagger
- **Maintainability** - Structured Python codebase

### Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.109+ |
| Runtime | Python 3.11+ |
| Database | Supabase (PostgreSQL) |
| Validation | Pydantic 2.x |
| Auth | Bearer Token (SHA-256 hash) |
| Testing | pytest + pytest-asyncio |
| Deployment | Docker / Railway |

---

## Architecture

### Directory Structure

```
service-engine-x-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, middleware, error handlers
│   ├── config.py               # Environment settings (Pydantic Settings)
│   ├── database.py             # Supabase client initialization
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── dependencies.py     # get_current_org, AuthContext
│   │   └── utils.py            # hash_token, extract_bearer_token
│   │
│   ├── models/
│   │   ├── __init__.py         # Exports all models
│   │   ├── common.py           # PaginatedResponse, ErrorResponse
│   │   ├── clients.py          # Client request/response schemas
│   │   ├── services.py         # Service schemas
│   │   ├── orders.py           # Order schemas
│   │   ├── order_tasks.py      # Order task schemas
│   │   ├── order_messages.py   # Order message schemas
│   │   ├── proposals.py        # Proposal schemas
│   │   ├── invoices.py         # Invoice schemas
│   │   └── tickets.py          # Ticket schemas
│   │
│   └── routers/
│       ├── __init__.py         # Exports all routers
│       ├── health.py           # /api/health
│       ├── clients.py          # /api/clients/*
│       ├── services.py         # /api/services/*
│       ├── orders.py           # /api/orders/*
│       ├── order_tasks.py      # /api/order-tasks/*
│       ├── order_messages.py   # /api/order-messages/*
│       ├── proposals.py        # /api/proposals/*
│       ├── invoices.py         # /api/invoices/*
│       └── tickets.py          # /api/tickets/*
│
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── test_health.py
│   ├── test_clients.py
│   ├── test_services.py
│   ├── test_orders.py
│   ├── test_order_tasks.py
│   ├── test_order_messages.py
│   ├── test_proposals.py
│   ├── test_invoices.py
│   └── test_tickets.py
│
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── PHASE-*-UPDATE.md           # Phase documentation
```

### Request Flow

```
Client Request
     │
     ▼
┌─────────────┐
│   FastAPI   │
│  Middleware │  ◄── CORS, Exception Handlers
└─────────────┘
     │
     ▼
┌─────────────┐
│   Router    │  ◄── /api/clients, /api/orders, etc.
└─────────────┘
     │
     ▼
┌─────────────┐
│    Auth     │  ◄── get_current_org dependency
│ Dependency  │      Validates Bearer token
└─────────────┘
     │
     ▼
┌─────────────┐
│  Pydantic   │  ◄── Request body validation
│   Models    │
└─────────────┘
     │
     ▼
┌─────────────┐
│  Supabase   │  ◄── Database queries
│   Client    │      Multi-tenant filtering
└─────────────┘
     │
     ▼
┌─────────────┐
│  Response   │  ◄── Pydantic model serialization
│   Model     │
└─────────────┘
     │
     ▼
JSON Response
```

---

## Phase-by-Phase Breakdown

### Phase 1: Foundation
**Commit:** `7436762`

Established the core project structure:
- FastAPI application setup
- Pydantic Settings for environment configuration
- Supabase client initialization (lazy loading)
- Bearer token authentication with SHA-256 hashing
- Health check endpoint
- Custom error handler matching Next.js format

**Files Created:**
- `app/main.py`
- `app/config.py`
- `app/database.py`
- `app/auth/dependencies.py`
- `app/auth/utils.py`
- `app/models/common.py`
- `app/routers/health.py`

### Phase 2: Clients API
**Commit:** `d1d1a7d`

First full CRUD resource, establishing patterns for all subsequent resources:
- List with pagination, filtering, sorting
- Create with address handling
- Retrieve with nested relations
- Update with partial updates
- Soft delete

**Endpoints:** 5
**Key Features:**
- Address creation/update
- Role assignment
- Multi-tenant org_id filtering

### Phase 3: Services API
**Commit:** `706fa75`

Service catalog management:
- Full CRUD operations
- Metadata key-value pairs
- Currency and pricing
- Soft delete pattern

**Endpoints:** 5
**Key Features:**
- Flexible metadata storage
- Price/currency handling

### Phase 4: Orders API
**Commit:** `b3abfe6`

Complex resource with nested entities:
- Order CRUD (5 endpoints)
- Nested tasks (4 endpoints)
- Nested messages (1 endpoint)
- Standalone task operations (4 endpoints)

**Endpoints:** 14
**Key Features:**
- Order number generation
- Service snapshotting
- Employee assignments via junction table
- Tag find-or-create
- Task completion tracking
- Message timestamps

### Phase 5: Proposals & Invoices API
**Commit:** `e99e5f3`

Business workflow endpoints:
- Proposals with send/sign workflows
- Invoices with charge/mark_paid workflows

**Endpoints:** 12 (5 proposals + 7 invoices)
**Key Features:**
- Proposal → Order conversion on sign
- Client find-or-create on proposal sign
- Invoice number generation
- Billing address snapshotting
- Status transition validation
- Recurring invoice support
- Stripe payment stub

### Phase 6: Tickets API
**Commit:** `aa49617`

Support ticket system:
- Full CRUD operations
- Employee assignments
- Tag system
- Message fetching
- Order linking

**Endpoints:** 5
**Key Features:**
- Status-based date_closed handling
- Messages on retrieve only
- Multi-tenant security

---

## API Reference

### Health & Index

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api` | API index with available endpoints |

### Clients (`/api/clients`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/clients` | List clients with pagination |
| POST | `/api/clients` | Create client |
| GET | `/api/clients/{id}` | Retrieve client |
| PUT | `/api/clients/{id}` | Update client |
| DELETE | `/api/clients/{id}` | Soft delete client |

### Services (`/api/services`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/services` | List services with pagination |
| POST | `/api/services` | Create service |
| GET | `/api/services/{id}` | Retrieve service |
| PUT | `/api/services/{id}` | Update service |
| DELETE | `/api/services/{id}` | Soft delete service |

### Orders (`/api/orders`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/orders` | List orders with pagination |
| POST | `/api/orders` | Create order |
| GET | `/api/orders/{id}` | Retrieve order |
| PUT | `/api/orders/{id}` | Update order |
| DELETE | `/api/orders/{id}` | Soft delete order |
| GET | `/api/orders/{id}/tasks` | List tasks for order |
| POST | `/api/orders/{id}/tasks` | Create task for order |
| GET | `/api/orders/{id}/messages` | List messages for order |
| POST | `/api/orders/{id}/messages` | Create message for order |

### Order Tasks (`/api/order-tasks`)

| Method | Path | Description |
|--------|------|-------------|
| PUT | `/api/order-tasks/{id}` | Update task |
| DELETE | `/api/order-tasks/{id}` | Delete task |
| POST | `/api/order-tasks/{id}/complete` | Mark task complete |
| DELETE | `/api/order-tasks/{id}/complete` | Mark task incomplete |

### Order Messages (`/api/order-messages`)

| Method | Path | Description |
|--------|------|-------------|
| DELETE | `/api/order-messages/{id}` | Delete message |

### Proposals (`/api/proposals`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/proposals` | List proposals with pagination |
| POST | `/api/proposals` | Create proposal with items |
| GET | `/api/proposals/{id}` | Retrieve proposal with items |
| POST | `/api/proposals/{id}/send` | Send proposal (Draft → Sent) |
| POST | `/api/proposals/{id}/sign` | Sign proposal, create order |

### Invoices (`/api/invoices`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/invoices` | List invoices with pagination |
| POST | `/api/invoices` | Create invoice with items |
| GET | `/api/invoices/{id}` | Retrieve invoice |
| PUT | `/api/invoices/{id}` | Update invoice |
| DELETE | `/api/invoices/{id}` | Soft delete invoice |
| POST | `/api/invoices/{id}/charge` | Charge invoice (Stripe) |
| POST | `/api/invoices/{id}/mark_paid` | Mark invoice as paid |

### Tickets (`/api/tickets`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tickets` | List tickets with pagination |
| POST | `/api/tickets` | Create ticket |
| GET | `/api/tickets/{id}` | Retrieve ticket with messages |
| PUT | `/api/tickets/{id}` | Update ticket |
| DELETE | `/api/tickets/{id}` | Soft delete ticket |

---

## Database Schema

### Core Tables

| Table | Description |
|-------|-------------|
| `users` | Clients and employees |
| `roles` | User roles with permissions |
| `addresses` | Physical addresses |
| `services` | Service catalog |
| `orders` | Customer orders |
| `order_tasks` | Tasks within orders |
| `order_messages` | Messages on orders |
| `proposals` | Sales proposals |
| `proposal_items` | Line items on proposals |
| `invoices` | Customer invoices |
| `invoice_items` | Line items on invoices |
| `tickets` | Support tickets |
| `ticket_messages` | Messages on tickets |
| `api_tokens` | API authentication tokens |

### Junction Tables

| Table | Purpose |
|-------|---------|
| `order_employees` | Order ↔ Employee assignments |
| `order_tags` | Order ↔ Tag associations |
| `order_task_employees` | Task ↔ Employee assignments |
| `ticket_employees` | Ticket ↔ Employee assignments |
| `ticket_tags` | Ticket ↔ Tag associations |
| `tags` | Shared tag definitions |

### Status Systems

**Orders:**
- 0 = Unpaid
- 1 = In Progress
- 2 = Completed
- 3 = Cancelled
- 4 = On Hold

**Proposals:**
- 0 = Draft
- 1 = Sent
- 2 = Signed
- 3 = Rejected

**Invoices:**
- 0 = Draft
- 1 = Unpaid
- 3 = Paid
- 4 = Refunded
- 5 = Cancelled
- 7 = Partially Paid

**Tickets:**
- 1 = Open
- 2 = Pending
- 3 = Closed

---

## Authentication

### Token Format

```
Authorization: Bearer <api_token>
```

### Token Validation Flow

1. Extract token from `Authorization` header
2. Hash token with SHA-256
3. Query `api_tokens` table by hash
4. Verify token not expired
5. Update `last_used_at` timestamp
6. Return `AuthContext` with `org_id`, `user_id`, `token_id`

### AuthContext Dataclass

```python
@dataclass
class AuthContext:
    org_id: str
    user_id: str
    token_id: str
```

### Usage in Endpoints

```python
@router.get("/")
async def list_items(
    auth: AuthContext = Depends(get_current_org),
):
    # auth.org_id available for filtering
    result = await supabase.table("items").select("*").eq("org_id", auth.org_id).execute()
```

---

## Key Patterns

### 1. Multi-Tenant Security

All database queries include `org_id` filtering:

```python
result = await supabase.table("orders").select("*").eq(
    "org_id", auth.org_id
).is_("deleted_at", "null").execute()
```

### 2. Soft Delete

Resources use `deleted_at` timestamp instead of hard delete:

```python
await supabase.table("orders").update({
    "deleted_at": datetime.now(timezone.utc).isoformat()
}).eq("id", order_id).execute()
```

### 3. Pagination Response Format

Consistent structure matching Laravel/Next.js:

```json
{
  "data": [...],
  "links": {
    "first": "?page=1&limit=20",
    "last": "?page=5&limit=20",
    "prev": null,
    "next": "?page=2&limit=20"
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "to": 20,
    "last_page": 5,
    "per_page": 20,
    "total": 100,
    "path": "/api/orders"
  }
}
```

### 4. Error Response Format

Matches Next.js validation error format:

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "field_name": ["Error message here"]
  }
}
```

### 5. Junction Table Pattern

For many-to-many relationships:

```python
# Delete existing assignments
await supabase.table("order_employees").delete().eq("order_id", order_id).execute()

# Insert new assignments
employee_rows = [
    {"order_id": order_id, "employee_id": emp_id}
    for emp_id in employee_ids
]
await supabase.table("order_employees").insert(employee_rows).execute()
```

### 6. Tag Find-or-Create

```python
async def assign_tags(supabase, entity_id: str, tag_names: list[str], junction_table: str):
    for tag_name in tag_names:
        # Find existing tag
        result = await supabase.table("tags").select("id").eq("name", tag_name).execute()

        if result.data:
            tag_id = result.data[0]["id"]
        else:
            # Create new tag
            new_tag = await supabase.table("tags").insert({"name": tag_name}).select("id").execute()
            tag_id = new_tag.data[0]["id"]

        # Link to entity
        await supabase.table(junction_table).insert({
            "entity_id": entity_id,
            "tag_id": tag_id,
        }).execute()
```

### 7. Supabase Join Array Handling

Supabase returns joined relations as arrays:

```python
addresses = user.get("addresses")
if isinstance(addresses, list) and len(addresses) > 0:
    address = addresses[0]
elif isinstance(addresses, dict):
    address = addresses
else:
    address = None
```

---

## Testing

### Test Structure

Each resource has a test file with unauthorized access tests:

```python
def test_list_orders_unauthorized(client: TestClient) -> None:
    """Test that list orders requires authentication."""
    response = client.get("/api/orders")
    assert response.status_code == 401
```

### Running Tests

```bash
# With virtual environment
source venv/bin/activate

# Set required environment variables
export SUPABASE_URL="https://test.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="test-key"

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_orders.py -v
```

### Test Count by Resource

| Test File | Tests |
|-----------|-------|
| test_health.py | 2 |
| test_clients.py | 6 |
| test_services.py | 6 |
| test_orders.py | 9 |
| test_order_tasks.py | 4 |
| test_order_messages.py | 1 |
| test_proposals.py | 5 |
| test_invoices.py | 7 |
| test_tickets.py | 5 |
| **Total** | **45** |

---

## Deployment

### Environment Variables

```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Optional
API_BASE_URL=http://localhost:8000
DEBUG=true
APP_NAME=Service Engine X API
APP_VERSION=1.0.0
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
```

### Railway Deployment

The API is configured for Railway deployment:
1. Connect GitHub repository
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main

---

## Files Created

### Phase 1 (Foundation)
- `app/__init__.py`
- `app/main.py`
- `app/config.py`
- `app/database.py`
- `app/auth/__init__.py`
- `app/auth/dependencies.py`
- `app/auth/utils.py`
- `app/models/__init__.py`
- `app/models/common.py`
- `app/routers/__init__.py`
- `app/routers/health.py`
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_health.py`
- `requirements.txt`
- `pyproject.toml`
- `Dockerfile`
- `docker-compose.yml`
- `.env.example`
- `.gitignore`

### Phase 2 (Clients)
- `app/models/clients.py`
- `app/routers/clients.py`
- `tests/test_clients.py`
- `PHASE-2-UPDATE.md`

### Phase 3 (Services)
- `app/models/services.py`
- `app/routers/services.py`
- `tests/test_services.py`
- `PHASE-3-UPDATE.md`

### Phase 4 (Orders)
- `app/models/orders.py`
- `app/models/order_tasks.py`
- `app/models/order_messages.py`
- `app/routers/orders.py`
- `app/routers/order_tasks.py`
- `app/routers/order_messages.py`
- `tests/test_orders.py`
- `tests/test_order_tasks.py`
- `tests/test_order_messages.py`
- `PHASE-4-UPDATE.md`

### Phase 5 (Proposals & Invoices)
- `app/models/proposals.py`
- `app/models/invoices.py`
- `app/routers/proposals.py`
- `app/routers/invoices.py`
- `tests/test_proposals.py`
- `tests/test_invoices.py`
- `PHASE-5-UPDATE.md`

### Phase 6 (Tickets)
- `app/models/tickets.py`
- `app/routers/tickets.py`
- `tests/test_tickets.py`
- `PHASE-6-UPDATE.md`
- `MIGRATION-COMPLETE.md`

---

## Commit History

```
aa49617 Add Tickets API - Migration Complete (Phase 6)
e99e5f3 Add Proposals & Invoices API (Phase 5)
b3abfe6 Add Orders API with nested tasks/messages (Phase 4)
706fa75 Add Services CRUD API with soft delete (Phase 3)
d1d1a7d Add Clients CRUD API with multi-tenant filtering (Phase 2)
7436762 Add FastAPI project foundation (Phase 1)
bee2052 Fix Railway build: lazy-initialize Supabase client
```

---

## Future Enhancements

Potential improvements for future development:

1. **Ticket Messages API** - Add CRUD endpoints for ticket messages
2. **WebSocket Support** - Real-time updates for tickets and orders
3. **Rate Limiting** - Protect API from abuse
4. **API Versioning** - `/api/v1/` prefix for breaking changes
5. **Caching** - Redis caching for frequently accessed data
6. **Audit Logging** - Track all API changes
7. **File Uploads** - Attachment handling for messages
8. **Webhooks** - Notify external systems of events
9. **Batch Operations** - Bulk create/update endpoints
10. **GraphQL** - Alternative query interface

---

*Migration completed by Claude Opus 4.5*
