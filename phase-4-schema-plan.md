# Phase 4 Schema Plan: Orders Core

**Created:** January 19, 2026  
**Status:** Draft — Awaiting Approval  
**Scope:** `orders` table and strictly required supporting tables only

---

## Overview

Phase 4 implements the Orders core (Section 7). Orders are the central transaction entity — everything downstream depends on them. This phase creates the minimal structure required for orders to exist.

**API Sections Enabled:**
- 7. Orders (full CRUD)

**What This Phase Unlocks:**
- Order creation, retrieval, update, delete
- Order ↔ Employee assignments
- Order ↔ Tag associations
- Phase 5: OrderTasks, OrderMessages (depend on orders)
- Phase 6: Invoices, Subscriptions (reference orders)

**What This Phase Does NOT Include:**
- Invoices (Phase 6)
- Subscriptions (Phase 6)
- OrderTasks (Phase 5)
- OrderMessages (Phase 5)
- Options/Addons (deferred)
- Ratings (deferred)

---

## Tables in This Phase

| Table | Purpose |
|-------|---------|
| `orders` | Central transaction entity |
| `order_employees` | Junction: orders ↔ assigned team members |
| `order_tags` | Junction: orders ↔ tags |

---

## Table: `orders`

### Purpose
Represents a purchased service. Contains client, service reference, pricing snapshot, status, dates, and metadata. Orders are the economic source of truth — downstream entities (tasks, messages, invoices) depend on orders, never vice versa.

### Source Documentation
- Section 7.1–7.5 Orders API
- IndexOrder object (list response)
- Extended Order object (retrieve response)

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `number` | `VARCHAR(50)` | NO | — | Order number (unique, human-readable) |
| `user_id` | `UUID` | NO | — | FK to users.id (the client) |
| `service_id` | `UUID` | YES | — | FK to services.id (if from catalog) |
| `service_name` | `VARCHAR(255)` | NO | — | Service name snapshot (required) |
| `status` | `SMALLINT` | NO | `0` | Order status (values undocumented) |
| `price` | `DECIMAL(12,2)` | NO | `0.00` | Order price (snapshot, not recomputed) |
| `quantity` | `INTEGER` | NO | `1` | Order quantity |
| `currency` | `VARCHAR(3)` | NO | `'USD'` | Currency code (ISO 4217) |
| `note` | `TEXT` | YES | — | Internal note (staff-visible) |
| `form_data` | `JSONB` | NO | `'{}'` | Submitted form data |
| `metadata` | `JSONB` | NO | `'{}'` | Custom metadata |
| `paysys` | `VARCHAR(50)` | YES | — | Payment system used (e.g., "Stripe") |
| `date_started` | `TIMESTAMPTZ` | YES | — | When work started |
| `date_completed` | `TIMESTAMPTZ` | YES | — | When work completed |
| `date_due` | `TIMESTAMPTZ` | YES | — | Due date |
| `last_message_at` | `TIMESTAMPTZ` | YES | — | Last message timestamp |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | YES | — | Soft delete timestamp |

### Indexes
- `PRIMARY KEY (id)`
- `UNIQUE (number)` — order number must be unique
- `INDEX (user_id)` — client lookup
- `INDEX (service_id)` — service lookup
- `INDEX (status)` — status filtering
- `INDEX (deleted_at)` — soft delete filtering
- `INDEX (created_at)` — chronological sorting

### Foreign Keys
- `user_id` (UUID) → `users(id)` ON DELETE RESTRICT
- `service_id` (UUID) → `services(id)` ON DELETE SET NULL

### Soft Delete
Orders use **soft delete**. When deleted:
- `deleted_at` is set to current timestamp
- Order is excluded from normal queries (`WHERE deleted_at IS NULL`)
- Associated invoices/subscriptions may remain (per SPP docs)

### Column Justifications

| Column | Why It Exists |
|--------|---------------|
| `number` | Human-readable identifier, can be custom or auto-generated |
| `service_id` | Links to catalog service (nullable — orders can exist without catalog link) |
| `service_name` | **Snapshot** — service name at time of order (required even if service_id exists) |
| `price` | **Snapshot** — price at time of order (never recomputed from service) |
| `quantity` | Number of units ordered |
| `currency` | Currency for this order (snapshot from service or explicit) |
| `status` | Integer status code (values undocumented, store as-is) |
| `form_data` | Customer-submitted form responses (intake forms) |
| `metadata` | Arbitrary key-value data for integrations |
| `paysys` | Which payment processor was used |
| `date_started` | When fulfillment began (nullable — may not have started) |
| `date_completed` | When fulfillment finished (nullable — may not be complete) |
| `date_due` | Deadline for completion (nullable — may not have deadline) |
| `last_message_at` | Denormalized for sorting by recent activity |

### What Is NOT Stored

| Field | Reason |
|-------|--------|
| `invoice_id` | Added in Phase 6 when invoices exist |
| `subscription_id` | Added in Phase 6 when subscriptions exist |
| `options` | Deferred — option system not implemented |
| `addons` | Deferred — addon system not implemented |
| `ratings` | Deferred — rating system not implemented |
| `messages` | Separate table (Phase 5: OrderMessages) |
| `tasks` | Separate table (Phase 5: OrderTasks) |

---

## Table: `order_employees`

### Purpose
Junction table linking orders to assigned team members. Represents the `employees` array in order responses.

### Source Documentation
- Section 7.1 Orders — `employees: array[object]`
- Section 7.2 Create Order — `employees[]: array[integer]`

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `order_id` | `UUID` | NO | — | FK to orders.id |
| `employee_id` | `UUID` | NO | — | FK to users.id (team member) |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | When assigned |

### Indexes
- `PRIMARY KEY (order_id, employee_id)` — composite key
- `INDEX (employee_id)` — for employee workload queries

### Foreign Keys
- `order_id` (UUID) → `orders(id)` ON DELETE CASCADE
- `employee_id` (UUID) → `users(id)` ON DELETE CASCADE

### Notes
- `employee_id` should reference users with team role (`dashboard_access > 0`)
- Application layer enforces role constraint
- When order is soft-deleted, assignments remain (can be cleaned up)

---

## Table: `order_tags`

### Purpose
Junction table linking orders to tags. Represents the `tags` array in order responses.

### Source Documentation
- Section 7.1 Orders — `tags: array[string]`
- Section 7.2 Create Order — `tags[]: array[string]`

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `order_id` | `UUID` | NO | — | FK to orders.id |
| `tag_id` | `UUID` | NO | — | FK to tags.id |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | When tagged |

### Indexes
- `PRIMARY KEY (order_id, tag_id)` — composite key
- `INDEX (tag_id)` — for tag-based filtering

### Foreign Keys
- `order_id` (UUID) → `orders(id)` ON DELETE CASCADE
- `tag_id` (UUID) → `tags(id)` ON DELETE CASCADE

### Notes
- SPP API accepts tag names as strings in requests
- Application layer resolves tag names to IDs (create if not exists)
- When order is soft-deleted, tag associations remain

---

## Order Number Generation

### Source Documentation
- Section 7.2 Create Order — `number: string (optional)`

### Design Decision
- `number` is a required column (NOT NULL)
- If not provided in request, application layer generates one
- Format: 8-character alphanumeric (e.g., `E4A269FC`)
- Must be unique across all orders

### Implementation Note
Application layer responsibility:
```
IF number not provided:
  number = generate_unique_order_number()
```

Generation algorithm (suggested):
- 8 uppercase alphanumeric characters
- Check uniqueness before insert
- Retry on collision

---

## Explicit Deferrals

### Deferred to Phase 5: Order Downstream Entities

| Table | Reason |
|-------|--------|
| `order_tasks` | OrderTasks API (Section 9) — depends on orders |
| `order_messages` | OrderMessages API (Section 8) — depends on orders |

### Deferred to Phase 6: Financial Entities

| Field/Table | Reason |
|-------------|--------|
| `orders.invoice_id` | Invoices table doesn't exist yet |
| `orders.subscription_id` | Subscriptions table doesn't exist yet |
| `invoices` table | Phase 6 scope |
| `subscriptions` table | Phase 6 scope |

### Deferred Indefinitely: Optional Features

| Feature | Reason |
|---------|--------|
| Options system | Complex, not documented in detail |
| Addons system | Depends on service addons (deferred) |
| Ratings system | Not required for core flow |

---

## API Response Mapping

### GET /api/orders (List)

```json
{
  "data": [
    {
      "id": "uuid",
      "created_at": "2021-09-01T00:00:00+00:00",
      "updated_at": "2021-09-01T00:00:00+00:00",
      "last_message_at": null,
      "date_started": null,
      "date_completed": null,
      "date_due": "2021-09-08T00:00:00+00:00",
      "client": { ... },              // JOIN users ON orders.user_id = users.id
      "tags": ["tag1", "tag2"],       // JOIN order_tags + tags
      "status": "Unpaid",             // Transform integer to string at API layer
      "price": 100.00,
      "quantity": 1,
      "invoice_id": null,             // NULL until Phase 6
      "service": "Service name",      // orders.service_name
      "service_id": "uuid",
      "user_id": "uuid",
      "employees": [ ... ],           // JOIN order_employees + users
      "note": "Note",
      "form_data": {},
      "paysys": "Stripe"
    }
  ],
  "links": { ... },
  "meta": { ... }
}
```

### Status Transformation (API Layer)

| DB Value | API Response (assumed) |
|----------|------------------------|
| `0` | `"Draft"` or `"Unpaid"` |
| `1` | `"Pending"` |
| `2` | `"In Progress"` |
| `3` | `"Completed"` |
| `...` | Unknown values pass through |

**Note:** Status mapping is undocumented. Store integer, transform at API layer when mapping is discovered.

---

## Validation Rules

### Orders
- `number`: Required, unique, max 50 chars
- `user_id`: Required, must exist in users table, should be a client
- `service_id`: If set, must exist in services table
- `service_name`: Required, max 255 chars (snapshot)
- `price`: Required, >= 0
- `quantity`: Required, >= 1
- `currency`: Required, 3 chars (ISO 4217)
- `status`: Integer (no constraint on values)

### Order Employees
- `employee_id`: Must reference a team member (application validation)

### Order Tags
- `tag_id`: Must exist in tags table (FK enforced)

---

## Migration Sequence

1. Create `orders` table with FKs to `users` and `services`
2. Create `order_employees` junction table with FKs to `orders` and `users`
3. Create `order_tags` junction table with FKs to `orders` and `tags`
4. Create indexes

---

## Dependency Diagram

```
Phase 1                    Phase 3                    Phase 4
─────────                  ─────────                  ─────────
┌─────────┐               ┌──────────┐               
│  users  │               │ services │               
└────┬────┘               └────┬─────┘               
     │                         │                     
     │ user_id                 │ service_id          
     │                         │                     
     └─────────────┬───────────┘                     
                   │                                  
                   ▼                                  
            ┌────────────┐                           
            │   orders   │                           
            └──────┬─────┘                           
                   │                                  
      ┌────────────┼────────────┐                    
      │            │            │                    
      ▼            ▼            ▼                    
┌───────────┐ ┌───────────┐ ┌──────────┐            
│order_emps │ │order_tags │ │ (Phase 5)│            
└───────────┘ └───────────┘ │tasks/msgs│            
                            └──────────┘            

Phase 1
─────────
┌─────────┐
│  tags   │◄──────────────────────┐
└─────────┘                       │
                                  │ tag_id
                            ┌─────┴─────┐
                            │order_tags │
                            └───────────┘
```

---

## One-Way Dependency Enforcement

**Critical Design Principle:**
- Orders reference users (clients) and services
- Orders NEVER reference downstream entities (tasks, messages, invoices)
- Downstream entities reference orders, not vice versa

| Entity | References Orders? | Orders References It? |
|--------|-------------------|----------------------|
| Users (clients) | NO | YES (user_id) |
| Services | NO | YES (service_id) |
| OrderTasks | YES (Phase 5) | NO |
| OrderMessages | YES (Phase 5) | NO |
| Invoices | YES (Phase 6) | **NO** (invoice_id added later as optional) |
| Subscriptions | YES (Phase 6) | **NO** |

**Exception:** `invoice_id` will be added to orders in Phase 6 as an optional denormalized reference for convenience. This is acceptable because:
1. It's nullable (orders can exist without invoices)
2. Invoice is created as a side effect of order, not the other way around
3. SPP API returns invoice_id in order responses

---

## Open Questions (Require Decision)

### 1. Order Number Generation
**Question:** Auto-generate on insert (DB trigger) or application layer?  
**Recommendation:** Application layer. More control, easier testing, can accept custom numbers.

### 2. Status Values
**Question:** Create status reference table or store raw integer?  
**Decision:** Store raw `SMALLINT`. Values undocumented — accept any integer.

### 3. Service Name Snapshot
**Question:** Always require `service_name` even when `service_id` is provided?  
**Decision:** Yes. Snapshot ensures order remains readable if service is deleted.

### 4. Soft Delete Cascade
**Question:** Should soft-deleting an order cascade to employees/tags?  
**Decision:** No. Junction tables remain. They reference the order ID which still exists.

---

## Approval Checklist

- [ ] `orders` table structure approved
- [ ] `order_employees` junction table approved
- [ ] `order_tags` junction table approved
- [ ] Pricing snapshot approach approved (no recomputation)
- [ ] Status as raw SMALLINT approved
- [ ] Soft delete via `deleted_at` approved
- [ ] One-way dependency model approved
- [ ] Deferred items acknowledged (invoice_id, subscription_id, tasks, messages)
- [ ] Ready to generate SQL migration

---

*This document specifies Phase 4 schema only. OrderTasks/OrderMessages (Phase 5) and Invoices/Subscriptions (Phase 6) are out of scope.*
