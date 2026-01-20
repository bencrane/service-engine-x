# Phase 2 Schema Plan: Clients

**Created:** January 19, 2026  
**Status:** Draft — Awaiting Approval  
**Scope:** Client extensions to `users`, `addresses` table, manager relationships

---

## Overview

Phase 2 extends the Phase 1 foundation to fully support the Clients API (Section 17). This phase adds:
1. Addresses table for client billing/shipping information
2. Manager relationship junction table
3. FK from users to addresses

**API Sections Enabled:**
- 17. Clients (full CRUD)

**Downstream Unlocks:**
- Phase 4: Orders (clients can place orders)
- Phase 6: Invoices (clients can have invoices)
- Phase 7: Tickets (clients can submit tickets)

---

## Phase 1 Modifications

### Table: `users`

**New column to add:**

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `address_id` | `UUID` | YES | — | FK to addresses.id (client billing address) |

**New FK:**
- `address_id` (UUID) → `addresses(id)` ON DELETE SET NULL

**No other changes to users table.** All client fields were included in Phase 1.

---

## New Table: `addresses`

### Purpose
Stores billing/shipping addresses for clients. Each client can have one primary address (referenced via `users.address_id`). The address includes recipient information that may differ from the user's own name (e.g., company billing contact).

### Source Documentation
- Section 17.1 Clients — Address object in Client response
- Section 17.2 Create Client — Address request object (subset of fields)

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `line_1` | `VARCHAR(255)` | YES | — | Address line 1 |
| `line_2` | `VARCHAR(255)` | YES | — | Address line 2 |
| `city` | `VARCHAR(255)` | YES | — | City |
| `state` | `VARCHAR(255)` | YES | — | State/Province |
| `country` | `VARCHAR(10)` | YES | — | Country code (ISO 3166-1 alpha-2) |
| `postcode` | `VARCHAR(50)` | YES | — | Postal/ZIP code |
| `name_f` | `VARCHAR(255)` | YES | — | Recipient first name (may differ from user) |
| `name_l` | `VARCHAR(255)` | YES | — | Recipient last name (may differ from user) |
| `tax_id` | `VARCHAR(100)` | YES | — | Tax ID for this address |
| `company_name` | `VARCHAR(255)` | YES | — | Company name for billing |
| `company_vat` | `VARCHAR(100)` | YES | — | Company VAT number |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |

### Indexes
- `PRIMARY KEY (id)`

### Notes
- All address fields nullable — partial addresses are valid
- `country` is short (ISO code), not full country name
- `name_f`, `name_l` allow different recipient than the user themselves
- SPP Create Client API only accepts: `line_1`, `line_2`, `city`, `state`, `country`, `postcode`
- SPP Response includes additional fields: `name_f`, `name_l`, `tax_id`, `company_name`, `company_vat`
- These additional fields may be populated from user record or set separately

### Design Decision: Separate Table vs Embedded JSON
**Decision:** Separate table.

**Rationale:**
- SPP returns Address as a nested object with defined schema
- Future phases may need multiple addresses per user (shipping vs billing)
- Enables address validation and querying
- Invoices (Phase 6) also have `billing_address` — may reuse this table

---

## New Table: `user_managers`

### Purpose
Junction table linking clients to their assigned managers (team members). Represents the `managers` array in the Client object. Distinct from `employee_id` which is a single primary assignee.

### Source Documentation
- Section 17.1 Clients — `managers: array[UserManager]`
- Section 13. Team — Managers are team members

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `client_id` | `UUID` | NO | — | FK to users.id (the client) |
| `manager_id` | `UUID` | NO | — | FK to users.id (the team member) |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | When relationship was created |

### Indexes
- `PRIMARY KEY (client_id, manager_id)` — composite key
- `INDEX (manager_id)` — for lookups by manager

### Foreign Keys
- `client_id` (UUID) → `users(id)` ON DELETE CASCADE
- `manager_id` (UUID) → `users(id)` ON DELETE CASCADE

### Constraints
- `CHECK (client_id != manager_id)` — user cannot be their own manager

### Notes
- Both FKs reference `users` table (self-referential many-to-many)
- `client_id` should reference a user with client role (`dashboard_access = 0`)
- `manager_id` should reference a user with team role (`dashboard_access > 0`)
- Application layer enforces role constraints, not DB constraints

---

## Deferred: `user_team_members`

### Purpose
Would represent `team_owner_ids` and `team_member_ids` from Client object.

### Source Documentation
- Section 17.1 Clients — `team_owner_ids: array[integer]`, `team_member_ids: array[integer]`

### Decision: DEFER

**Rationale:**
1. Documentation is unclear on the meaning of these fields
2. Appears to be a "client teams" feature (clients who have sub-users)
3. Not required for core order/invoice/ticket flows
4. Can be added in a later phase if needed

### If Implemented Later
Would require a `user_team_memberships` table with:
- `team_owner_id` (UUID) → users.id
- `team_member_id` (UUID) → users.id
- Possibly a `team_id` if teams are first-class entities

---

## API Response Mapping

### GET /api/clients

```json
{
  "data": [
    {
      "id": "uuid",
      "name": "John Doe",          // Computed: name_f + ' ' + name_l
      "name_f": "John",
      "name_l": "Doe",
      "email": "user@example.org",
      "company": "Example Inc.",
      "tax_id": "123456789",
      "phone": "123456789",
      "address": {                 // JOIN addresses ON users.address_id = addresses.id
        "line_1": "123 Main St",
        "line_2": "Suite 100",
        "city": "New York",
        "state": "NY",
        "country": "US",
        "postcode": "10001",
        "name_f": "John",
        "name_l": "Doe",
        "tax_id": "123456789",
        "company_name": "Acme Inc.",
        "company_vat": "123456789"
      },
      "note": "Note",
      "balance": 10.00,
      "spent": "10.00",
      "optin": "Yes",
      "stripe_id": "cus_xxx",
      "custom_fields": {},
      "status": 1,
      "role_id": "uuid",
      "role": { ... },             // JOIN roles ON users.role_id = roles.id
      "aff_id": 1,
      "aff_link": "https://...",
      "ga_cid": "123456789.xxx",
      "employee_id": "uuid",
      "managers": [ ... ],         // JOIN user_managers ON users.id = user_managers.client_id
      "team_owner_ids": [],        // DEFERRED
      "team_member_ids": [],       // DEFERRED
      "created_at": "2021-09-01T00:00:00+00:00"
    }
  ],
  "links": { ... },
  "meta": { ... }
}
```

### Filtering Clients (not Team)

```sql
SELECT * FROM users 
WHERE role_id IN (
  SELECT id FROM roles WHERE dashboard_access = 0
)
```

---

## Validation Rules

### Addresses
- All fields optional (partial addresses allowed)
- `country`: If provided, should be valid ISO 3166-1 alpha-2 code (application validation)
- `postcode`: Format varies by country (no DB constraint)

### User Managers
- `client_id` must reference a user with client role
- `manager_id` must reference a user with team role
- Same user cannot be both client and manager in same relationship
- Application layer enforces role constraints

---

## Migration Sequence

1. Create `addresses` table
2. Add `address_id` column to `users` table
3. Add FK constraint `users.address_id` → `addresses.id`
4. Create `user_managers` junction table
5. Create indexes

---

## Dependency Diagram

```
Phase 1                          Phase 2
─────────                        ─────────
┌─────────┐                     ┌───────────┐
│  roles  │                     │ addresses │
└────┬────┘                     └─────┬─────┘
     │                                │
     │ role_id                        │ address_id
     ▼                                ▼
┌─────────┐◄─────────────────────────────────────┐
│  users  │                                      │
└────┬────┘                                      │
     │                                           │
     │ employee_id (self-ref)                    │
     │                                           │
     └───────────────────────────────────────────┘
                    │
                    │ client_id, manager_id
                    ▼
            ┌───────────────┐
            │ user_managers │
            └───────────────┘
```

---

## Open Questions (Require Decision)

### 1. Address Ownership
**Question:** Should addresses be owned by users (1:1) or reusable across users?  
**Current Design:** 1:1 via `users.address_id`. Each user has at most one address.  
**Alternative:** Address could have `user_id` FK instead, allowing multiple addresses per user.  
**Recommendation:** Keep 1:1 for v1. If multiple addresses needed later, can add `user_addresses` junction table.

### 2. Address on Create
**Question:** When creating a client with address, create address first or in same transaction?  
**Recommendation:** Same transaction. API accepts nested address object.

### 3. Empty Managers Array
**Question:** How to represent clients with no managers?  
**Answer:** No rows in `user_managers` for that client. Return empty array `[]` in API response.

### 4. team_owner_ids / team_member_ids
**Question:** Should these be implemented now?  
**Decision:** Deferred. Meaning unclear, not required for core flows.

---

## Explicit Deferrals

| Item | Reason | Phase |
|------|--------|-------|
| `user_team_memberships` table | Meaning unclear, not in core flow | Future |
| Multiple addresses per user | Not required by SPP API | Future |
| Address soft delete | Not in SPP model | N/A |
| Address validation rules | Application layer concern | N/A |

---

## Approval Checklist

- [ ] `addresses` table structure approved
- [ ] `user_managers` junction table approved
- [ ] FK `users.address_id` → `addresses.id` approved
- [ ] Deferral of `team_owner_ids` / `team_member_ids` approved
- [ ] 1:1 address ownership model approved
- [ ] Ready to generate SQL migration

---

*This document specifies Phase 2 schema only. Services (Phase 3) and Orders (Phase 4) are out of scope.*
