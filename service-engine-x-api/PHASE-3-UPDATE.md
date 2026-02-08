# Phase 3 Complete: Services API

**Date:** 2026-02-07
**Status:** Complete

## Summary

Phase 3 implemented the full Services CRUD API with multi-tenant org_id filtering and soft delete pattern.

## What Was Built

### New Files

```
app/
├── models/
│   └── services.py         # Service request/response schemas
├── routers/
│   └── services.py         # Full CRUD endpoints
tests/
└── test_services.py        # Auth/validation tests
```

### Endpoints Implemented

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/services` | List services with pagination, sorting, filtering |
| POST | `/api/services` | Create a new service |
| GET | `/api/services/{id}` | Retrieve a single service |
| PUT | `/api/services/{id}` | Update a service |
| DELETE | `/api/services/{id}` | Soft delete a service |

### Key Features

1. **Multi-tenant Filtering**
   - All queries filter by `org_id` from authenticated token
   - Excludes soft-deleted records (`deleted_at IS NULL`)

2. **Soft Delete**
   - DELETE sets `deleted_at` timestamp instead of removing record
   - All queries filter out soft-deleted services

3. **Pagination & Sorting**
   - Same patterns as Clients API
   - Valid sort fields: id, name, price, recurring, public, sort_order, created_at

4. **Filtering**
   - Filterable fields: id, name, recurring, public, price, currency, folder_id, created_at
   - Supports boolean filters (`true`/`false` strings)
   - Supports null checks (`null` string)

5. **Metadata Handling**
   - Input: Array of `{title, value}` objects
   - Storage: Key-value object (title as key, value as value)
   - Transformed on create/update

6. **Employee Assignments**
   - Optional `employees` array of user IDs
   - Validates employees have dashboard access (not clients)
   - Stored in `service_employees` junction table
   - Replace semantics on update (delete all, insert new)

7. **Folder Validation**
   - Optional `folder_id` for organization
   - Validates folder exists in `service_folders` table

8. **Price Formatting**
   - `pretty_price` computed field with currency symbol
   - Supports USD, EUR, GBP, CAD, AUD

9. **Recurring Types**
   - `recurring`: 0 (one-time), 1 (subscription), 2 (both)
   - Period types: D (day), W (week), M (month), Y (year)

### Models

**ServiceCreate** (POST body):
- `name`, `recurring`, `currency` (required)
- `description`, `price`, `public`, `deadline` (optional)
- `f_price`, `f_period_l`, `f_period_t` (first payment config)
- `r_price`, `r_period_l`, `r_period_t` (recurring payment config)
- `employees`, `metadata`, `folder_id` (optional)
- `braintree_plan_id`, `hoth_*`, `provider_*` (integrations)

**ServiceUpdate** (PUT body):
- All fields optional
- Only provided fields are updated

**ServiceResponse**:
- All service fields
- `pretty_price` computed with currency symbol

## Differences from Clients API

| Aspect | Clients | Services |
|--------|---------|----------|
| Delete | Hard delete (with FK guard) | Soft delete (deleted_at) |
| Relations | Address, Role | Employees (junction), Folder |
| Computed | `spent` from invoices | `pretty_price` from price |
| Metadata | `custom_fields` dict | `metadata` array → dict |

## Tests

14 tests passing:
- 6 services authorization tests
- 6 clients authorization tests
- 2 health endpoint tests

## Next: Phase 4 - Orders API

Phase 4 will implement the Orders API with nested resources:
- `GET /api/orders` - List orders
- `POST /api/orders` - Create order
- `GET /api/orders/{id}` - Retrieve order
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Soft delete order
- Nested: `/api/orders/{id}/tasks`, `/api/orders/{id}/messages`
