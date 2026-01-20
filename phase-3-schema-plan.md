# Phase 3 Schema Plan: Services

**Created:** January 19, 2026  
**Status:** Draft — Awaiting Approval  
**Scope:** `services` table and service-local supporting tables only

---

## Overview

Phase 3 implements the Services API (Section 10). Services are products/offerings that can be ordered. They define pricing models, recurring billing configurations, deadlines, and organizational structure.

**API Sections Enabled:**
- 10. Services (full CRUD)

**What This Phase Unlocks:**
- Orders can reference services via `service_id` (Phase 4)
- Subscriptions will be created for recurring services (Phase 6)

**What This Phase Does NOT Unlock:**
- Orders (Phase 4)
- Invoices (Phase 6)
- Subscriptions (Phase 6)
- Option variants / customization (deferred)

---

## Tables in This Phase

| Table | Purpose |
|-------|---------|
| `services` | Products/offerings with pricing configuration |
| `service_folders` | Organizational grouping for services |
| `service_employees` | Junction: services ↔ assigned team members |

---

## Table: `services`

### Purpose
Defines purchasable products/offerings. Contains pricing models (one-time, recurring, trial), deadlines, visibility settings, and metadata.

### Source Documentation
- Section 10.1–10.5 Services API
- Pricing model: `recurring` (0=one-time, 1=recurring, 2=trial/setup)

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `name` | `VARCHAR(255)` | NO | — | Service name |
| `description` | `TEXT` | YES | — | Service description |
| `image` | `VARCHAR(500)` | YES | — | Image URL |
| `recurring` | `SMALLINT` | NO | `0` | Billing type: 0=one-time, 1=recurring, 2=trial/setup |
| `price` | `DECIMAL(12,2)` | YES | — | Base price (one-time services) |
| `currency` | `VARCHAR(3)` | NO | `'USD'` | ISO 4217 currency code |
| `f_price` | `DECIMAL(12,2)` | YES | — | First payment price (recurring) |
| `f_period_l` | `INTEGER` | YES | — | First period length |
| `f_period_t` | `CHAR(1)` | YES | — | First period type: D/W/M/Y |
| `r_price` | `DECIMAL(12,2)` | YES | — | Recurring payment price |
| `r_period_l` | `INTEGER` | YES | — | Recurring period length |
| `r_period_t` | `CHAR(1)` | YES | — | Recurring period type: D/W/M/Y |
| `recurring_action` | `SMALLINT` | YES | — | Action on recurring cycle (values undocumented) |
| `deadline` | `INTEGER` | YES | — | Default deadline in days |
| `public` | `BOOLEAN` | NO | `true` | Publicly visible |
| `sort_order` | `INTEGER` | NO | `0` | Display order |
| `multi_order` | `BOOLEAN` | NO | `true` | Allow multiple orders of this service |
| `request_orders` | `BOOLEAN` | NO | `false` | Request-based ordering |
| `max_active_requests` | `INTEGER` | YES | — | Max active requests (if request_orders) |
| `group_quantities` | `BOOLEAN` | NO | `false` | Group quantities in cart |
| `folder_id` | `UUID` | YES | — | FK to service_folders.id |
| `metadata` | `JSONB` | NO | `'{}'` | Custom metadata (array of {title, value}) |
| `braintree_plan_id` | `VARCHAR(255)` | YES | — | Braintree integration (external) |
| `hoth_product_key` | `VARCHAR(255)` | YES | — | HOTH integration (external) |
| `hoth_package_name` | `VARCHAR(255)` | YES | — | HOTH integration (external) |
| `provider_id` | `INTEGER` | YES | — | External provider ID |
| `provider_service_id` | `INTEGER` | YES | — | External provider service ID |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | YES | — | Soft delete timestamp |

### Indexes
- `PRIMARY KEY (id)`
- `INDEX (folder_id)`
- `INDEX (public)` — for filtering visible services
- `INDEX (deleted_at)` — for soft delete filtering
- `INDEX (sort_order)` — for ordering

### Foreign Keys
- `folder_id` (UUID) → `service_folders(id)` ON DELETE SET NULL

### Soft Delete
Services use **soft delete**. When deleted:
- `deleted_at` is set to current timestamp
- Service is excluded from normal queries (`WHERE deleted_at IS NULL`)
- Existing orders referencing the service are unaffected

### Notes
- `recurring` stored as SMALLINT (0, 1, 2), API may return as boolean for backward compat
- Period types: `D`=Day, `W`=Week, `M`=Month, `Y`=Year
- `f_` prefix = first payment configuration
- `r_` prefix = recurring payment configuration
- `pretty_price` is computed at API layer, not stored
- `option_categories`, `option_variants` deferred (see Deferrals section)
- `addon_to` / `parent_services` deferred (see Deferrals section)
- `media` array deferred (see Deferrals section)

---

## Table: `service_folders`

### Purpose
Organizational grouping for services. Services can optionally belong to a folder for categorization in admin UI.

### Source Documentation
- Section 10.1 Services — `folder_id` field references folders

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `name` | `VARCHAR(255)` | NO | — | Folder name |
| `sort_order` | `INTEGER` | NO | `0` | Display order |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |

### Indexes
- `PRIMARY KEY (id)`
- `INDEX (sort_order)`

### Notes
- No soft delete — folders are simple organizational units
- No nested folders in SPP documentation
- If folder deleted, services remain but `folder_id` becomes NULL

---

## Table: `service_employees`

### Purpose
Junction table linking services to assigned team members. Represents the `employees` array on service create/update.

### Source Documentation
- Section 10.2 Create Service — `employees: array[integer]`

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `service_id` | `UUID` | NO | — | FK to services.id |
| `employee_id` | `UUID` | NO | — | FK to users.id (team member) |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | When assigned |

### Indexes
- `PRIMARY KEY (service_id, employee_id)` — composite key
- `INDEX (employee_id)` — for employee workload queries

### Foreign Keys
- `service_id` (UUID) → `services(id)` ON DELETE CASCADE
- `employee_id` (UUID) → `users(id)` ON DELETE CASCADE

### Notes
- `employee_id` should reference users with team role (`dashboard_access > 0`)
- Application layer enforces role constraint
- When service is soft-deleted, assignments remain (can be cleaned up if needed)

---

## Pricing Model Reference

### One-Time Services (`recurring = 0`)
```
price: 100.00
currency: USD
```
Customer pays once. No subscription created.

### Recurring Services (`recurring = 1`)
```
f_price: 50.00      -- First payment
f_period_l: 1       -- First period: 1
f_period_t: M       -- First period type: Month
r_price: 100.00     -- Recurring payment
r_period_l: 1       -- Recurring period: 1
r_period_t: M       -- Recurring period type: Month
```
Customer pays `f_price` for first `f_period_l` `f_period_t`, then `r_price` every `r_period_l` `r_period_t`.

### Trial/Setup Fee Services (`recurring = 2`)
Initial fee (setup) followed by recurring payments.

---

## Explicit Deferrals

### Deferred: Option Categories & Variants

**Fields:** `option_categories`, `option_variants` (arrays in response)

**Reason:**
- Complex configuration system not documented in detail
- Requires additional tables: `option_categories`, `option_variants`, `service_option_categories`, etc.
- Not required for basic order flow

**Future Phase:** Would require:
- `option_categories` table
- `option_variants` table
- Junction tables for service-option relationships
- Possibly `order_option_selections` for capturing customer choices

### Deferred: Service Addons

**Fields:** `addon_to` (response), `parent_services` (request)

**Reason:**
- Self-referential many-to-many relationship
- Requires `service_addons` junction table
- Addon logic (pricing, constraints) not fully documented
- Can be added without breaking existing schema

**Future Phase:** Would require:
- `service_addons` junction table (`parent_service_id`, `addon_service_id`)

### Deferred: Media Attachments

**Fields:** `media` (array in response)

**Reason:**
- Media object structure not documented
- Likely requires file storage integration
- Not required for basic order flow

**Future Phase:** Would require:
- `service_media` table or JSONB array storage
- File upload handling

### Deferred: clear_variants

**Field:** `clear_variants` (boolean in create/update request)

**Reason:**
- Depends on option variants system which is deferred
- No-op until variants are implemented

---

## API Response Mapping

### GET /api/services

```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Service name",
      "description": "Description",
      "image": "https://...",
      "recurring": true,           // API transforms: 0→false, 1/2→true
      "price": 100.00,
      "pretty_price": "$100.00",   // Computed at API layer
      "currency": "USD",
      "f_price": 50.00,
      "f_period_l": 1,
      "f_period_t": "M",           // Or "day", "week", "month", "year" (API transforms)
      "r_price": 100.00,
      "r_period_l": 1,
      "r_period_t": "M",
      "recurring_action": "Cancel",
      "multi_order": true,
      "request_orders": false,
      "option_categories": [],     // Empty until implemented
      "option_variants": [],       // Empty until implemented
      "deadline": 7,
      "public": true,
      "sort_order": 1,
      "braintree_plan_id": null,
      "group_quantities": false,
      "addon_to": [],              // Empty until implemented
      "folder_id": "uuid",
      "metadata": {},
      "hoth_product_key": null,
      "hoth_package_name": null,
      "created_at": "2021-09-01T00:00:00+00:00",
      "updated_at": "2021-09-01T00:00:00+00:00",
      "provider_id": null,
      "provider_service_id": null,
      "deleted_at": null,
      "media": []                  // Empty until implemented
    }
  ],
  "links": { ... },
  "meta": { ... }
}
```

### Field Transformations (API Layer)
| DB Value | API Response |
|----------|--------------|
| `recurring = 0` | `"recurring": false` |
| `recurring = 1` | `"recurring": true` |
| `recurring = 2` | `"recurring": true` |
| `f_period_t = 'D'` | `"f_period_t": "day"` |
| `f_period_t = 'W'` | `"f_period_t": "week"` |
| `f_period_t = 'M'` | `"f_period_t": "month"` |
| `f_period_t = 'Y'` | `"f_period_t": "year"` |

---

## Validation Rules

### Services
- `name`: Required, max 255 chars
- `recurring`: Required, must be 0, 1, or 2
- `currency`: Required, 3 chars (ISO 4217)
- `f_period_t`, `r_period_t`: If set, must be one of D, W, M, Y
- `price`: If `recurring = 0`, should be set
- `f_price`, `r_price`: If `recurring > 0`, should be set
- `folder_id`: If set, must exist in service_folders

### Service Folders
- `name`: Required, max 255 chars

### Service Employees
- `employee_id`: Must reference a team member (application validation)

---

## Migration Sequence

1. Create `service_folders` table (no dependencies)
2. Create `services` table with FK to `service_folders`
3. Create `service_employees` junction table with FKs to `services` and `users`
4. Create indexes

---

## Dependency Diagram

```
Phase 1                    Phase 3
─────────                  ─────────
┌─────────┐               ┌──────────────────┐
│  users  │               │  service_folders │
└────┬────┘               └────────┬─────────┘
     │                             │
     │ employee_id                 │ folder_id
     │                             ▼
     │                    ┌────────────────┐
     │                    │    services    │
     │                    └───────┬────────┘
     │                            │
     │ service_id, employee_id    │
     ▼                            ▼
┌────────────────────────────────────┐
│         service_employees          │
└────────────────────────────────────┘
```

---

## Open Questions (Require Decision)

### 1. Period Type Storage
**Question:** Store as `CHAR(1)` (D/W/M/Y) or `VARCHAR(10)` (day/week/month/year)?  
**Recommendation:** `CHAR(1)` in DB, transform to full word at API layer. Matches SPP request format.

### 2. Recurring Action Values
**Question:** `recurring_action` is integer in request, string in response. Values undocumented.  
**Recommendation:** Store as `SMALLINT`. Transform to string at API layer when mapping is discovered.

### 3. multi_order / request_orders Type
**Question:** Integer in request, boolean in response per docs.  
**Recommendation:** Store as `BOOLEAN`. Treat any truthy integer as true on input.

### 4. Metadata Structure
**Question:** Array of `{title, value}` objects or flat key-value?  
**Recommendation:** Store as `JSONB`. Accept SPP's array format `[{title: "key", value: "val"}]`.

---

## Approval Checklist

- [ ] `services` table structure approved
- [ ] `service_folders` table approved
- [ ] `service_employees` junction table approved
- [ ] Soft delete via `deleted_at` approved
- [ ] Pricing fields (f_*, r_*) approved
- [ ] Deferred items acknowledged (options, addons, media)
- [ ] Period type storage (`CHAR(1)`) approved
- [ ] Ready to generate SQL migration

---

*This document specifies Phase 3 schema only. Orders (Phase 4) and beyond are out of scope.*
