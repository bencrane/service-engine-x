# Phase 2 Complete: Clients API

**Date:** 2026-02-07
**Status:** Complete

## Summary

Phase 2 implemented the full Clients CRUD API with multi-tenant org_id filtering, serving as the template for all other resource APIs.

## What Was Built

### New Files

```
app/
├── models/
│   └── clients.py          # Client request/response schemas
├── routers/
│   └── clients.py          # Full CRUD endpoints
tests/
└── test_clients.py         # Auth/validation tests
```

### Endpoints Implemented

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/clients` | List clients with pagination, sorting, filtering |
| POST | `/api/clients` | Create a new client |
| GET | `/api/clients/{id}` | Retrieve a single client |
| PUT | `/api/clients/{id}` | Update a client |
| DELETE | `/api/clients/{id}` | Delete a client (with FK guard) |

### Key Features

1. **Multi-tenant Filtering**
   - All queries filter by `org_id` from authenticated token
   - Clients are identified by `role_id` with `dashboard_access = 0`

2. **Pagination**
   - Configurable `limit` (1-100, default 20)
   - Page-based navigation with `page` parameter
   - Full pagination links and meta in response

3. **Sorting**
   - Format: `sort=field:direction` (e.g., `sort=created_at:desc`)
   - Valid fields: id, email, name_f, name_l, status, balance, created_at

4. **Filtering**
   - Format: `filters[field][$op]=value`
   - Operators: `$eq`, `$lt`, `$gt`, `$in`
   - Filterable fields: id, email, status, balance, created_at

5. **Address Handling**
   - Create: Automatically creates address record if provided
   - Update: Updates existing or creates new address
   - Stored in separate `addresses` table with `address_id` reference

6. **Affiliate Generation**
   - Auto-generates 6-digit `aff_id`
   - Auto-generates `aff_link` URL

7. **FK Guard on Delete**
   - Checks for dependent: orders, invoices, tickets, subscriptions
   - Returns 409 Conflict if dependencies exist
   - Hard deletes if no dependencies

8. **Spent Calculation**
   - On retrieve/update, calculates total from paid invoices
   - Sums `total` from invoices where `date_paid` is not null

### Models

**ClientCreate** (POST body):
- `name_f`, `name_l`, `email` (required)
- `company`, `phone`, `tax_id`, `address`, `note` (optional)
- `optin`, `stripe_id`, `custom_fields`, `status_id` (optional)

**ClientUpdate** (PUT body):
- All fields optional
- Only provided fields are updated

**ClientResponse**:
- Full client data with computed `name` field
- Nested `address` and `role` objects
- `spent` calculated from paid invoices

### Supabase Join Handling

Properly handles array returns from Supabase joins:
```python
addr_data = client.get("address")
if isinstance(addr_data, list):
    addr_data = addr_data[0] if addr_data else None
```

## Dependencies Added

- `email-validator>=2.0.0` - For Pydantic EmailStr validation

## Tests

8 tests passing:
- 6 authorization tests (all endpoints require auth)
- 2 health endpoint tests

## Response Format

Matches Next.js API exactly:

**List Response:**
```json
{
  "data": [...],
  "links": {
    "first": "...",
    "last": "...",
    "prev": null,
    "next": "..."
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "to": 20,
    "last_page": 5,
    "per_page": 20,
    "total": 100,
    "path": "/api/clients"
  }
}
```

**Single Client Response:**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "name_f": "John",
  "name_l": "Doe",
  "email": "john@example.com",
  "address": { ... },
  "role": { ... },
  "balance": "0.00",
  "spent": "150.00",
  ...
}
```

## Next: Phase 3 - Services API

Phase 3 will implement the Services CRUD API:
- Similar pattern to Clients but simpler (no address/role relations)
- `GET /api/services` - List with pagination
- `POST /api/services` - Create service
- `GET /api/services/{id}` - Retrieve service
- `PUT /api/services/{id}` - Update service
- `DELETE /api/services/{id}` - Soft delete service
