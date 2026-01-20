# Phase 7 Schema Plan: Tickets & TicketMessages

**Created:** January 20, 2026  
**Status:** Draft — Awaiting Approval  
**Scope:** `tickets`, `ticket_employees`, `ticket_tags`, `ticket_messages`

---

## Overview

Phase 7 implements the ticket system — a parallel communication channel to orders. Tickets are first-class support entities that can exist independently of orders.

**API Sections Enabled:**
- 14. Tickets (full CRUD)
- 15. TicketMessages (list, create, delete)

**What This Phase Unlocks:**
- Support ticket creation and management
- Ticket-based client/staff communication
- Optional order linkage for order-related support
- Tag-based ticket categorization

**What This Phase Does NOT Include:**
- File attachments (deferred)
- Email integration / notifications
- SLA tracking
- Ticket templates

---

## Tables in This Phase

| Table | Purpose |
|-------|---------|
| `tickets` | Support tickets (first-class entity) |
| `ticket_employees` | Junction: tickets ↔ assigned team members |
| `ticket_tags` | Junction: tickets ↔ tags |
| `ticket_messages` | Communication thread on tickets |

---

## Table: `tickets`

### Purpose
Support tickets for client-staff communication. First-class entity that can exist with or without an associated order. Supports status tracking, employee assignment, and tagging.

### Source Documentation
- Section 14.1–14.5 Tickets API

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `number` | `VARCHAR(50)` | NO | — | Ticket number (unique, human-readable) |
| `subject` | `VARCHAR(255)` | NO | — | Ticket subject line |
| `user_id` | `UUID` | NO | — | FK to users.id (client who created) |
| `order_id` | `UUID` | YES | — | FK to orders.id (optional order link) |
| `status` | `SMALLINT` | NO | `0` | Status ID (values undocumented) |
| `source` | `VARCHAR(50)` | YES | — | Ticket source (e.g., "API", "Portal") |
| `form_data` | `JSONB` | NO | `'{}'` | Submitted form data |
| `metadata` | `JSONB` | NO | `'{}'` | Custom metadata |
| `note` | `TEXT` | YES | — | Internal note (staff-visible) |
| `last_message_at` | `TIMESTAMPTZ` | YES | — | Last message timestamp |
| `date_closed` | `TIMESTAMPTZ` | YES | — | When ticket was closed |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | YES | — | Soft delete timestamp |

### Indexes
- `PRIMARY KEY (id)`
- `UNIQUE (number)` — ticket numbers must be unique
- `INDEX (user_id)` — client tickets
- `INDEX (order_id)` — tickets for an order
- `INDEX (status)` — status filtering
- `INDEX (deleted_at)` — soft delete filtering
- `INDEX (created_at)` — chronological sorting

### Foreign Keys
- `user_id` (UUID) → `users(id)` ON DELETE RESTRICT
- `order_id` (UUID) → `orders(id)` ON DELETE SET NULL

### Soft Delete
Tickets use **soft delete**. Per SPP docs: "Soft delete - can be undone."

### Column Justifications

| Column | Why It Exists |
|--------|---------------|
| `number` | Human-readable identifier (like order numbers) |
| `user_id` | The client who created/owns the ticket (required) |
| `order_id` | **Optional** link to related order |
| `status` | Integer status code (undocumented values) |
| `source` | Where ticket originated (API, Portal, Email, etc.) |
| `form_data` | Intake form responses |
| `metadata` | Custom key-value data |
| `note` | Internal staff note (distinct from messages) |
| `last_message_at` | Denormalized for sorting by recent activity |
| `date_closed` | When ticket was resolved/closed |

### Why `order_id` Is Nullable

Tickets are **first-class entities** that can exist independently:
- General support inquiries (no order)
- Pre-sales questions (no order yet)
- Account issues (not order-specific)
- Billing questions (may or may not relate to specific order)

When `order_id` IS set:
- Ticket relates to a specific order
- API returns full `order` object in response
- Enables order-specific support workflows

---

## Table: `ticket_employees`

### Purpose
Junction table linking tickets to assigned team members. Represents the `employees` array in ticket responses.

### Source Documentation
- Section 14.1 Tickets — `employees: array[object]`
- Section 14.2 Create Ticket — `employees[]: array[integer]`

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `ticket_id` | `UUID` | NO | — | FK to tickets.id |
| `employee_id` | `UUID` | NO | — | FK to users.id (team member) |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | When assigned |

### Indexes
- `PRIMARY KEY (ticket_id, employee_id)` — composite key
- `INDEX (employee_id)` — for employee workload queries

### Foreign Keys
- `ticket_id` (UUID) → `tickets(id)` ON DELETE CASCADE
- `employee_id` (UUID) → `users(id)` ON DELETE CASCADE

### Notes
- `employee_id` should reference users with team role (`dashboard_access > 0`)
- Application layer enforces role constraint

---

## Table: `ticket_tags`

### Purpose
Junction table linking tickets to tags. Represents the `tags` array in ticket responses.

### Source Documentation
- Section 14.1 Tickets — `tags: array[string]`
- Section 14.2 Create Ticket — `tags[]: array[string]`

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `ticket_id` | `UUID` | NO | — | FK to tickets.id |
| `tag_id` | `UUID` | NO | — | FK to tags.id |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | When tagged |

### Indexes
- `PRIMARY KEY (ticket_id, tag_id)` — composite key
- `INDEX (tag_id)` — for tag-based filtering

### Foreign Keys
- `ticket_id` (UUID) → `tickets(id)` ON DELETE CASCADE
- `tag_id` (UUID) → `tags(id)` ON DELETE CASCADE

### Notes
- SPP API accepts tag names as strings in requests
- Application layer resolves tag names to IDs (create if not exists)

---

## Table: `ticket_messages`

### Purpose
Communication messages on tickets. Functionally identical to `order_messages` but for tickets. Messages are immutable and hard-deleted.

### Source Documentation
- Section 15.1–15.3 TicketMessages API

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `ticket_id` | `UUID` | NO | — | FK to tickets.id |
| `user_id` | `UUID` | YES | — | FK to users.id (author, nullable if deleted) |
| `message` | `TEXT` | NO | — | Message content |
| `staff_only` | `BOOLEAN` | NO | `false` | Internal note (not visible to client) |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |

### Indexes
- `PRIMARY KEY (id)`
- `INDEX (ticket_id)` — messages for a ticket
- `INDEX (user_id)` — messages by a user
- `INDEX (created_at)` — chronological ordering

### Foreign Keys
- `ticket_id` (UUID) → `tickets(id)` ON DELETE CASCADE
- `user_id` (UUID) → `users(id)` ON DELETE SET NULL

### Delete Behavior
**HARD DELETE** — per SPP documentation: "WARNING: Hard delete - cannot be undone."

No `deleted_at` column.

### Column Justifications

| Column | Why It Exists |
|--------|---------------|
| `ticket_id` | Messages belong to tickets (one-way dependency) |
| `user_id` | Author of the message (nullable — preserved if user deleted) |
| `message` | Message content (required) |
| `staff_only` | If true, client cannot see this message |
| `created_at` | When message was created (no updated_at — immutable) |

### What Is NOT Stored

| Field | Reason |
|-------|--------|
| `files` | File attachments deferred — requires file storage |
| `updated_at` | Messages cannot be edited per SPP API |

### Notes
- **No update endpoint** — messages are immutable after creation
- `user_id` defaults to authenticated user if not specified in request
- Creating a message should update `tickets.last_message_at`
- Structurally identical to `order_messages` (parallel design)

---

## Side Effects

### Message Creation → Update tickets.last_message_at

When a ticket message is created:
```sql
UPDATE tickets 
SET last_message_at = NOW(), updated_at = NOW()
WHERE id = :ticket_id
```

Application layer responsibility, not a database trigger.

---

## One-Way Dependency Enforcement

**Critical Design Principle:**
- Tickets reference users (clients) and optionally orders
- Orders NEVER reference tickets
- Ticket messages reference tickets, not vice versa

| Entity | References Orders? | Orders References It? |
|--------|-------------------|----------------------|
| `tickets` | YES (nullable order_id) | **NO** |
| `ticket_messages` | NO (references tickets) | NO |

```
users ──┐
        ├──► tickets ──► ticket_messages
orders ─┘     (optional)
```

---

## API Response Mapping

### GET /api/tickets

```json
{
  "data": [
    {
      "id": "uuid",
      "subject": "Ticket subject",
      "status": "Open",              // Transform integer to string at API layer
      "source": "API",
      "user_id": "uuid",
      "client": { ... },             // JOIN users ON tickets.user_id = users.id
      "order_id": "uuid",            // May be null
      "form_data": {},
      "tags": ["tag1", "tag2"],      // JOIN ticket_tags + tags
      "note": "Internal note",
      "employees": [ ... ],          // JOIN ticket_employees + users
      "created_at": "2021-09-01T00:00:00+00:00",
      "updated_at": "2021-09-01T00:00:00+00:00",
      "last_message_at": null,
      "date_closed": null
    }
  ],
  "links": { ... },
  "meta": { ... }
}
```

### GET /api/tickets/{ticket} (Extended Response)

Includes additional nested objects:
- `messages` — Array of ticket messages
- `order` — Full order object (if `order_id` is set)
- `client` — Full client user object with role and address
- `metadata` — Custom metadata object

### GET /api/ticket_messages/{ticket}

```json
{
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "created_at": "2021-09-01T00:00:00+00:00",
      "message": "Hello world!",
      "staff_only": false,
      "files": []                    // Empty until file storage implemented
    }
  ],
  "links": { ... },
  "meta": { ... }
}
```

---

## Status Values (Undocumented)

| Value | Likely Meaning |
|-------|----------------|
| 0 | Open |
| 1 | In Progress |
| 2 | Waiting on Client |
| 3 | Resolved |
| 4 | Closed |

**Note:** Store raw integers. Map to strings at API layer when confirmed.

---

## Explicit Deferrals

### Deferred: File Attachments

**Fields:** `attachments` (request), `files` (response)

**Reason:**
- Requires file storage infrastructure
- Same deferral as `order_messages.files`
- Can be added without schema changes

### Deferred: Email Integration

**Reason:**
- Ticket creation via email not in scope
- Notification logic is application concern

### Deferred: SLA Tracking

**Reason:**
- Response time / resolution time tracking not in SPP API
- Can be added as separate table if needed

---

## Validation Rules

### Tickets
- `number`: Required, unique, max 50 chars
- `subject`: Required, max 255 chars
- `user_id`: Required, must exist in users table (client)
- `order_id`: If set, must exist in orders table
- `status`: Integer (no constraint on values)

### Ticket Employees
- `employee_id`: Must reference a team member (application validation)

### Ticket Tags
- `tag_id`: Must exist in tags table (FK enforced)

### Ticket Messages
- `message`: Required, non-empty
- `ticket_id`: Required, must exist in tickets table
- `user_id`: Optional, if set must exist in users table

---

## Migration Sequence

1. Create `tickets` table with FKs to `users` and `orders`
2. Create `ticket_employees` junction table with FKs to `tickets` and `users`
3. Create `ticket_tags` junction table with FKs to `tickets` and `tags`
4. Create `ticket_messages` table with FKs to `tickets` and `users`
5. Create indexes

---

## Dependency Diagram

```
Phase 1                    Phase 4                    Phase 7
─────────                  ─────────                  ─────────
┌─────────┐               ┌──────────┐               
│  users  │               │  orders  │               
└────┬────┘               └────┬─────┘               
     │                         │                     
     │ user_id                 │ order_id (optional) 
     │                         │                     
     └─────────────┬───────────┘                     
                   │                                  
                   ▼                                  
            ┌────────────┐                           
            │  tickets   │                           
            └──────┬─────┘                           
                   │                                  
      ┌────────────┼────────────┬───────────────┐    
      │            │            │               │    
      ▼            ▼            ▼               ▼    
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐
│ticket_   │ │ticket_   │ │ticket_   │ │            │
│employees │ │tags      │ │messages  │ │            │
└──────────┘ └──────────┘ └──────────┘ └────────────┘

Phase 1
─────────
┌─────────┐
│  tags   │◄──────────────────────┐
└─────────┘                       │
                                  │ tag_id
                            ┌─────┴──────┐
                            │ticket_tags │
                            └────────────┘
```

---

## Comparison: Tickets vs Orders

| Aspect | Orders | Tickets |
|--------|--------|---------|
| **Primary purpose** | Transaction | Support |
| **Client required** | Yes | Yes |
| **Service required** | Yes (or name) | No |
| **Pricing** | Yes | No |
| **Messages** | `order_messages` | `ticket_messages` |
| **Tasks** | `order_tasks` | No |
| **Invoice** | Yes (optional) | No |
| **Subscription** | Yes (optional) | No |
| **Tags** | Yes | Yes |
| **Employees** | Yes | Yes |
| **Soft delete** | Yes | Yes |
| **Order link** | N/A (is the order) | Optional |

---

## Approval Checklist

- [ ] `tickets` table structure approved
- [ ] `ticket_employees` junction table approved
- [ ] `ticket_tags` junction table approved
- [ ] `ticket_messages` table structure approved
- [ ] Nullable `order_id` approved (tickets are first-class)
- [ ] Soft delete for tickets approved
- [ ] Hard delete for ticket_messages approved
- [ ] No `updated_at` on messages approved (immutable)
- [ ] `user_id` nullable on messages approved (SET NULL on user delete)
- [ ] File attachments deferred approved
- [ ] One-way dependencies preserved (tickets → orders, not reverse)
- [ ] Ready to generate SQL migration

---

*This document specifies Phase 7 schema only. No further phases are planned in the current build sequence.*
