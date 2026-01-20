# Phase 5 Schema Plan: Order Dependents

**Created:** January 19, 2026  
**Status:** Draft — Awaiting Approval  
**Scope:** `order_tasks`, `order_messages` — entities that cannot exist without an order

---

## Overview

Phase 5 implements entities that depend on orders: tasks and messages. These are downstream of orders — they reference orders, but orders never reference them.

**API Sections Enabled:**
- 1. Tasks (mark complete/incomplete)
- 8. OrderMessages (list, create, delete)
- 9. OrderTasks (list, create, update, delete)

**What This Phase Unlocks:**
- Task management on orders
- Communication threads on orders
- `orders.last_message_at` can be updated by message creation

**What This Phase Does NOT Include:**
- Invoices (Phase 6)
- Subscriptions (Phase 6)
- Tickets (Phase 7)
- TicketMessages (Phase 7)
- File storage / attachment handling (deferred)
- Ratings (deferred)

---

## Tables in This Phase

| Table | Purpose |
|-------|---------|
| `order_tasks` | Work items to complete for order fulfillment |
| `order_task_employees` | Junction: tasks ↔ assigned team members |
| `order_messages` | Communication thread on orders |

---

## Table: `order_tasks`

### Purpose
Represents work items that need to be completed as part of order fulfillment. Tasks can be assigned to team members or designated for client completion. Completion status is tracked and can be toggled via the Tasks API (Section 1).

### Source Documentation
- Section 9.1–9.4 OrderTasks API
- Section 1.1–1.2 Tasks API (mark complete/incomplete)

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `order_id` | `UUID` | NO | — | FK to orders.id |
| `name` | `VARCHAR(255)` | NO | — | Task name |
| `description` | `TEXT` | YES | — | Task description |
| `sort_order` | `INTEGER` | NO | `0` | Display order |
| `is_public` | `BOOLEAN` | NO | `false` | Visible on client portal |
| `for_client` | `BOOLEAN` | NO | `false` | Client can complete this task |
| `is_complete` | `BOOLEAN` | NO | `false` | Completion status |
| `completed_by` | `UUID` | YES | — | FK to users.id (who completed) |
| `completed_at` | `TIMESTAMPTZ` | YES | — | When completed |
| `deadline` | `INTEGER` | YES | — | Hours until deadline (mutually exclusive with due_at) |
| `due_at` | `TIMESTAMPTZ` | YES | — | Specific due date (mutually exclusive with deadline) |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |

### Indexes
- `PRIMARY KEY (id)`
- `INDEX (order_id)` — tasks for an order
- `INDEX (is_complete)` — filter by completion status
- `INDEX (completed_by)` — who completed tasks
- `INDEX (sort_order)` — ordering

### Foreign Keys
- `order_id` (UUID) → `orders(id)` ON DELETE CASCADE
- `completed_by` (UUID) → `users(id)` ON DELETE SET NULL

### Delete Behavior
**HARD DELETE** — per SPP documentation, task deletion is permanent and cannot be undone.

No `deleted_at` column.

### Column Justifications

| Column | Why It Exists |
|--------|---------------|
| `order_id` | Tasks belong to orders (one-way dependency) |
| `name` | Required task identifier |
| `description` | Optional detailed description |
| `sort_order` | Controls display order in UI |
| `is_public` | Whether client can see this task |
| `for_client` | Whether client (not staff) completes this task |
| `is_complete` | Completion status (toggled via Section 1 API) |
| `completed_by` | Who marked the task complete |
| `completed_at` | When the task was completed |
| `deadline` | Hours from previous task/order creation (calculated) |
| `due_at` | Absolute due date/time |

### Notes
- `deadline` and `due_at` are mutually exclusive — use one or the other
- `deadline` is in hours (use 24-hour increments for days: 24, 48, 72...)
- `for_client` and `employee_ids` (junction) are mutually exclusive
- `is_complete` is modified via `POST /api/order_tasks/{task}/complete` and `DELETE /api/order_tasks/{task}/complete`
- When `is_complete` becomes true, set `completed_by` and `completed_at`

---

## Table: `order_task_employees`

### Purpose
Junction table linking tasks to assigned team members. Represents the `employee_ids` array when creating/updating tasks.

### Source Documentation
- Section 9.2 Create OrderTask — `employee_ids: array[integer]`
- Section 9.3 Update OrderTask — `employee_ids: array[integer]`

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `task_id` | `UUID` | NO | — | FK to order_tasks.id |
| `employee_id` | `UUID` | NO | — | FK to users.id (team member) |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | When assigned |

### Indexes
- `PRIMARY KEY (task_id, employee_id)` — composite key
- `INDEX (employee_id)` — for employee workload queries

### Foreign Keys
- `task_id` (UUID) → `order_tasks(id)` ON DELETE CASCADE
- `employee_id` (UUID) → `users(id)` ON DELETE CASCADE

### Notes
- `employee_id` should reference users with team role (`dashboard_access > 0`)
- If `for_client = true` on the task, this junction should be empty
- Application layer enforces mutual exclusivity

---

## Table: `order_messages`

### Purpose
Communication messages on orders. Messages can be from staff or clients. Staff-only messages are internal notes not visible to clients.

### Source Documentation
- Section 8.1–8.3 OrderMessages API

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `order_id` | `UUID` | NO | — | FK to orders.id |
| `user_id` | `UUID` | YES | — | FK to users.id (author, nullable if user deleted) |
| `message` | `TEXT` | NO | — | Message content |
| `staff_only` | `BOOLEAN` | NO | `false` | Internal note (not visible to client) |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |

### Indexes
- `PRIMARY KEY (id)`
- `INDEX (order_id)` — messages for an order
- `INDEX (user_id)` — messages by a user
- `INDEX (created_at)` — chronological ordering

### Foreign Keys
- `order_id` (UUID) → `orders(id)` ON DELETE CASCADE
- `user_id` (UUID) → `users(id)` ON DELETE SET NULL

### Delete Behavior
**HARD DELETE** — per SPP documentation, message deletion is permanent and cannot be undone.

No `deleted_at` column.

### Column Justifications

| Column | Why It Exists |
|--------|---------------|
| `order_id` | Messages belong to orders (one-way dependency) |
| `user_id` | Author of the message (nullable — preserved if user deleted) |
| `message` | Message content (required) |
| `staff_only` | If true, client cannot see this message |
| `created_at` | When message was created (no updated_at — messages immutable) |

### What Is NOT Stored

| Field | Reason |
|-------|--------|
| `files` | File attachments deferred — requires file storage system |
| `ticket` | Ticket association is Phase 7 |
| `updated_at` | Messages cannot be edited per SPP API |

### Notes
- **No update endpoint** — messages are immutable after creation
- `user_id` defaults to authenticated user if not specified in request
- Creating a message should update `orders.last_message_at`
- `files` array in SPP response will be empty until file storage is implemented

---

## Explicit Deferrals

### Deferred: File Attachments

**Fields:** `attachments` (request), `files` (response)

**Reason:**
- Requires file storage infrastructure (S3, Supabase Storage, etc.)
- File upload handling is separate concern
- Not required for core messaging functionality

**Future Implementation:**
- `order_message_files` table or JSONB column
- File upload endpoint
- URL generation for downloads

### Deferred: Ticket Association

**Field:** `ticket` in message response

**Reason:**
- Tickets don't exist yet (Phase 7)
- Messages can exist on orders without ticket association

**Future Implementation:**
- Add nullable `ticket_id` FK to `order_messages` in Phase 7

---

## Side Effects

### Message Creation → Update orders.last_message_at

When a message is created:
```sql
UPDATE orders 
SET last_message_at = NOW(), updated_at = NOW()
WHERE id = :order_id
```

This is an application-layer responsibility, not a database trigger.

### Task Completion → Update completed_by, completed_at

When `POST /api/order_tasks/{task}/complete` is called:
```sql
UPDATE order_tasks 
SET is_complete = true, 
    completed_by = :current_user_id, 
    completed_at = NOW(),
    updated_at = NOW()
WHERE id = :task_id
```

When `DELETE /api/order_tasks/{task}/complete` is called:
```sql
UPDATE order_tasks 
SET is_complete = false, 
    completed_by = NULL, 
    completed_at = NULL,
    updated_at = NOW()
WHERE id = :task_id
```

---

## API Response Mapping

### GET /api/order_tasks/{order}

```json
{
  "data": [
    {
      "id": "uuid",
      "order_id": "ABC12345",       // orders.number, not orders.id
      "name": "Design Logo",
      "description": "Create a new logo",
      "sort_order": 1,
      "is_public": true,
      "for_client": false,
      "is_complete": false,
      "completed_by": null,         // user_id or null
      "completed_at": null,
      "deadline": 7,                // hours
      "due_at": null
    }
  ],
  "links": { ... },
  "meta": { ... }
}
```

**Note:** `order_id` in response is the order **number** (string), not the UUID.

### GET /api/order_messages/{order}

```json
{
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "created_at": "2021-09-01T00:00:00+00:00",
      "message": "Hello world!",
      "staff_only": false,
      "files": [],                  // Empty until file storage implemented
      "order": { ... },             // Full order object (JOIN)
      "ticket": null                // Null until Phase 7
    }
  ],
  "links": { ... },
  "meta": { ... }
}
```

---

## Validation Rules

### Order Tasks
- `name`: Required, max 255 chars
- `order_id`: Required, must exist in orders table
- `sort_order`: Integer, default 0
- `deadline`: If set, `due_at` must be null
- `due_at`: If set, `deadline` must be null
- `for_client`: If true, `employee_ids` must be empty
- `employee_ids`: If set, `for_client` must be false

### Order Messages
- `message`: Required, non-empty
- `order_id`: Required, must exist in orders table
- `user_id`: Optional, if set must exist in users table (becomes NULL if user deleted)

---

## Migration Sequence

1. Create `order_tasks` table with FKs to `orders` and `users`
2. Create `order_task_employees` junction table with FKs to `order_tasks` and `users`
3. Create `order_messages` table with FKs to `orders` and `users`
4. Create indexes

---

## Dependency Diagram

```
Phase 4                           Phase 5
─────────                         ─────────
┌──────────┐                     
│  orders  │                     
└────┬─────┘                     
     │                           
     │ order_id                  
     │                           
     ├─────────────────────────────────────────┐
     │                                         │
     ▼                                         ▼
┌─────────────┐                         ┌──────────────┐
│ order_tasks │                         │order_messages│
└──────┬──────┘                         └──────────────┘
       │                                       │
       │ task_id                               │ user_id
       ▼                                       ▼
┌────────────────────┐                  ┌──────────┐
│order_task_employees│                  │  users   │
└────────────────────┘                  └──────────┘
       │
       │ employee_id
       ▼
┌──────────┐
│  users   │
└──────────┘
```

---

## One-Way Dependency Enforcement

**Critical Design Principle:**
- Tasks and messages reference orders
- Orders NEVER reference tasks or messages
- `orders.last_message_at` is denormalized for sorting, updated by application layer

| Entity | References Orders? | Orders References It? |
|--------|-------------------|----------------------|
| `order_tasks` | YES (order_id) | NO |
| `order_messages` | YES (order_id) | NO (last_message_at is denormalized) |

---

## Open Questions (Require Decision)

### 1. Deadline Calculation
**Question:** How is `deadline` (hours) calculated from previous task or order creation?  
**Recommendation:** Application layer calculates `due_at` from `deadline` at read time. Store raw `deadline` value.

### 2. order_id in Task Response
**Question:** SPP returns order **number** (string) as `order_id`, not the UUID.  
**Recommendation:** Store UUID as FK, transform to order number at API layer.

### 3. Message Author Fallback
**Question:** If `user_id` not provided in request, default to authenticated user?  
**Recommendation:** Yes, application layer sets `user_id` to current user if not specified.

### 4. Cascade on Order Soft Delete
**Question:** Should tasks/messages cascade when order is soft-deleted?  
**Decision:** No. Tasks/messages have CASCADE on DELETE, but orders use soft delete. They remain until order is hard-deleted.

---

## Approval Checklist

- [ ] `order_tasks` table structure approved
- [ ] `order_task_employees` junction table approved
- [ ] `order_messages` table structure approved
- [ ] **HARD DELETE** for tasks and messages approved
- [ ] No `updated_at` on messages approved (immutable)
- [ ] File attachments deferred approved
- [ ] Ticket association deferred to Phase 7 approved
- [ ] FK delete behaviors approved (CASCADE for order_id, SET NULL for user_id on messages)
- [ ] One-way dependency model confirmed
- [ ] Ready to generate SQL migration

---

*This document specifies Phase 5 schema only. Invoices/Subscriptions (Phase 6) and Tickets (Phase 7) are out of scope.*
