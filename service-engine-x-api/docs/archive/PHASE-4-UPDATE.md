# Phase 4 Complete: Orders API with Nested Resources

**Date:** 2026-02-07
**Status:** Complete

## Summary

Phase 4 implemented the full Orders API including nested task and message resources, plus standalone operation endpoints.

## What Was Built

### New Files

```
app/
├── models/
│   ├── orders.py           # Order request/response schemas
│   ├── order_tasks.py      # Task request/response schemas
│   └── order_messages.py   # Message request/response schemas
├── routers/
│   ├── orders.py           # Orders CRUD + nested endpoints
│   ├── order_tasks.py      # Standalone task operations
│   └── order_messages.py   # Standalone message operations
tests/
├── test_orders.py          # 10 order endpoint tests
├── test_order_tasks.py     # 4 task endpoint tests
└── test_order_messages.py  # 1 message endpoint test
```

### Endpoints Implemented (16 total)

#### Orders Router (`/api/orders`)
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

#### Order Tasks Router (`/api/order-tasks`)
| Method | Path | Description |
|--------|------|-------------|
| PUT | `/api/order-tasks/{id}` | Update task |
| DELETE | `/api/order-tasks/{id}` | Delete task |
| POST | `/api/order-tasks/{id}/complete` | Mark complete |
| DELETE | `/api/order-tasks/{id}/complete` | Mark incomplete |

#### Order Messages Router (`/api/order-messages`)
| Method | Path | Description |
|--------|------|-------------|
| DELETE | `/api/order-messages/{id}` | Delete message |

### Key Features

1. **Order Relations**
   - `client` - Fetched from users table with address/role
   - `employees` - Junction table `order_employees`
   - `tags` - Junction table `order_tags` (find-or-create)
   - `tasks` - Child table `order_tasks`
   - `messages` - Child table `order_messages`

2. **Service Snapshotting**
   - On create, copies `service_name`, `price`, `currency` from service
   - Allows custom service name override

3. **Status System**
   - 0 = Unpaid
   - 1 = In Progress
   - 2 = Completed
   - 3 = Cancelled
   - 4 = On Hold
   - Response includes both `status` (string) and `status_id` (int)

4. **Order Number Generation**
   - Auto-generates 8-character alphanumeric number
   - Can be overridden (validates uniqueness)

5. **Task Features**
   - `for_client` / `employee_ids` mutual exclusion
   - `deadline` / `due_at` mutual exclusion
   - Completion tracking: `is_complete`, `completed_by`, `completed_at`
   - Employee assignments via `order_task_employees`

6. **Message Features**
   - Public/private visibility (`is_public`)
   - Updates `last_message_at` on order
   - Includes user info in response

7. **Multi-tenant Security**
   - All operations filter by `org_id`
   - Task/message operations verify parent order's org
   - Checks parent order not soft-deleted

### Data Flow

**Order Create:**
```
1. Validate user_id exists
2. Validate service_id (if provided) or require service name
3. Snapshot price/currency from service
4. Validate employees (dashboard_access > 0)
5. Generate order number (or validate uniqueness)
6. Create order
7. Create order_employees assignments
8. Create order_tags (find-or-create tags)
9. Return serialized order with relations
```

**Task Complete:**
```
1. Verify task exists
2. Verify parent order belongs to auth.org_id
3. Verify parent order not soft-deleted
4. Set is_complete=true, completed_by=auth.user_id, completed_at=now
```

## Tests

28 tests passing:
- 10 orders tests
- 4 order-tasks tests
- 1 order-messages test
- 6 services tests
- 6 clients tests
- 2 health tests

## Response Examples

**Order Response:**
```json
{
  "id": "uuid",
  "number": "ABC12345",
  "status": "In Progress",
  "status_id": 1,
  "client": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "address": {...},
    "role": {...}
  },
  "employees": [
    {"id": "uuid", "name_f": "Jane", "name_l": "Smith", "role_id": "uuid"}
  ],
  "tags": ["urgent", "premium"],
  "service": "Web Development",
  "service_id": "uuid",
  "price": "1500.00",
  "quantity": 1,
  ...
}
```

**Task Response:**
```json
{
  "id": "uuid",
  "order_id": "uuid",
  "name": "Design mockups",
  "is_complete": true,
  "completed_by": "uuid",
  "completed_at": "2026-02-07T...",
  "employees": [
    {"id": "uuid", "name_f": "Jane", "name_l": "Smith"}
  ],
  ...
}
```

## Next: Phase 5 - Proposals & Invoices

Phase 5 will implement:
- Proposals API (5 endpoints + send/sign workflows)
- Invoices API (7 endpoints + charge/mark_paid workflows)
