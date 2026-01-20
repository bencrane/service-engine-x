# Phase 1 Schema Plan: Foundation

**Created:** January 19, 2026  
**Status:** Draft — Awaiting Approval  
**Scope:** `roles`, `users`, `tags` tables only

---

## Global Decision: UUIDs for Primary Keys

**Rationale:**
- API-first, multi-org system → UUIDs avoid collisions and ID enumeration
- Safer for public APIs than sequential integers
- Easier for future imports, async jobs, cross-environment work
- Aligns with Supabase/Postgres norms

**Implementation:**
- `id UUID PRIMARY KEY DEFAULT gen_random_uuid()` on all tables
- All foreign keys are UUIDs
- Keep integers for enums/statuses/permissions only

---

## Overview

Phase 1 establishes the identity and configuration foundation. These tables are referenced by virtually every downstream entity. Getting them right eliminates rework in later phases.

**API Sections Enabled:**
- 12. Tags (list only)
- 13. Team (list, retrieve)

**Downstream Unlocks:**
- Phase 2: Clients (extends `users`)
- Phase 4: Orders (references `users` for clients and employees)
- All phases: Role-based permission checks (stored, not enforced in v1)

---

## Table: `roles`

### Purpose
Defines permission sets for users. Both team members and clients have roles. Permissions are stored as integers 0-3 per the SPP model.

### Source Documentation
- Section 13. Team — Role object embedded in User responses
- Permission levels: 0=None, 1=Own, 2=Group, 3=All

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `name` | `VARCHAR(255)` | NO | — | Role name (e.g., "Administrator", "Client") |
| `dashboard_access` | `SMALLINT` | NO | `0` | Dashboard access level (0-3) |
| `order_access` | `SMALLINT` | NO | `0` | Order read access (0-3) |
| `order_management` | `SMALLINT` | NO | `0` | Order write access (0-3) |
| `ticket_access` | `SMALLINT` | NO | `0` | Ticket read access (0-3) |
| `ticket_management` | `SMALLINT` | NO | `0` | Ticket write access (0-3) |
| `invoice_access` | `SMALLINT` | NO | `0` | Invoice read access (0-3) |
| `invoice_management` | `SMALLINT` | NO | `0` | Invoice write access (0-3) |
| `clients` | `SMALLINT` | NO | `0` | Clients permission (0-3) |
| `services` | `SMALLINT` | NO | `0` | Services permission (0-3) |
| `coupons` | `SMALLINT` | NO | `0` | Coupons permission (0-3) |
| `forms` | `SMALLINT` | NO | `0` | Forms permission (0-3) |
| `messaging` | `SMALLINT` | NO | `0` | Messaging permission (0-3) |
| `affiliates` | `SMALLINT` | NO | `0` | Affiliates permission (0-3) |
| `settings_company` | `BOOLEAN` | NO | `false` | Company settings access |
| `settings_payments` | `BOOLEAN` | NO | `false` | Payment settings access |
| `settings_team` | `BOOLEAN` | NO | `false` | Team settings access |
| `settings_modules` | `BOOLEAN` | NO | `false` | Module settings access |
| `settings_integrations` | `BOOLEAN` | NO | `false` | Integration settings access |
| `settings_orders` | `BOOLEAN` | NO | `false` | Order settings access |
| `settings_tickets` | `BOOLEAN` | NO | `false` | Ticket settings access |
| `settings_accounts` | `BOOLEAN` | NO | `false` | Account settings access |
| `settings_messages` | `BOOLEAN` | NO | `false` | Message settings access |
| `settings_tags` | `BOOLEAN` | NO | `false` | Tag settings access |
| `settings_sidebar` | `BOOLEAN` | NO | `false` | Sidebar settings access |
| `settings_dashboard` | `BOOLEAN` | NO | `false` | Dashboard settings access |
| `settings_templates` | `BOOLEAN` | NO | `false` | Template settings access |
| `settings_emails` | `BOOLEAN` | NO | `false` | Email settings access |
| `settings_language` | `BOOLEAN` | NO | `false` | Language settings access |
| `settings_logs` | `BOOLEAN` | NO | `false` | Log settings access |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |

### Indexes
- `PRIMARY KEY (id)`

### Seed Data Required
Two default roles minimum (UUIDs auto-generated):
1. **Administrator** — all permissions set to 3/true
2. **Client** — all permissions set to 0/false (clients use client portal, not admin)

Note: Seed UUIDs can be hardcoded for test environments if deterministic IDs are needed.

### Notes
- `team` and `settings` boolean fields from SPP are marked deprecated in docs — omitted
- `rank_tracking` permission exists in SPP but appears domain-specific — omitted for v1
- Permissions stored but NOT enforced in v1 per plan

---

## Table: `users`

### Purpose
Unified table for all user types (team members and clients). Differentiated by `role_id`. Client-specific fields are nullable for team members and vice versa.

### Source Documentation
- Section 13. Team — User object for team members
- Section 17. Clients — Client object (same structure with client-specific fields)

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `email` | `VARCHAR(255)` | NO | — | Email address (unique) |
| `password_hash` | `VARCHAR(255)` | YES | — | Hashed password (null for magic-link-only users) |
| `name_f` | `VARCHAR(255)` | NO | — | First name |
| `name_l` | `VARCHAR(255)` | NO | — | Last name |
| `company` | `VARCHAR(255)` | YES | — | Company name |
| `phone` | `VARCHAR(50)` | YES | — | Phone number |
| `tax_id` | `VARCHAR(100)` | YES | — | Tax ID |
| `note` | `TEXT` | YES | — | Internal note (staff-visible) |
| `role_id` | `UUID` | NO | — | FK to roles.id |
| `status` | `SMALLINT` | NO | `1` | Account status (values undocumented, store as-is) |
| `balance` | `DECIMAL(12,2)` | NO | `0.00` | Account credit balance (clients) |
| `spent` | `DECIMAL(12,2)` | NO | `0.00` | Total spent (clients) |
| `optin` | `VARCHAR(50)` | YES | — | Marketing consent |
| `stripe_id` | `VARCHAR(255)` | YES | — | Stripe customer ID (clients) |
| `custom_fields` | `JSONB` | NO | `'{}'` | Custom field data |
| `aff_id` | `INTEGER` | YES | — | Affiliate ID (clients — legacy field) |
| `aff_link` | `VARCHAR(255)` | YES | — | Affiliate link (clients) |
| `ga_cid` | `VARCHAR(255)` | YES | — | Google Analytics client ID |
| `employee_id` | `UUID` | YES | — | Assigned employee (clients) — FK to users.id |
| `two_factor_enabled` | `BOOLEAN` | NO | `false` | 2FA status (blocks magic link if true) |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |

### Indexes
- `PRIMARY KEY (id)`
- `UNIQUE (email)`
- `INDEX (role_id)`
- `INDEX (status)`
- `INDEX (employee_id)` — for client assignment lookups

### Foreign Keys
- `role_id` (UUID) → `roles(id)` ON DELETE RESTRICT
- `employee_id` (UUID) → `users(id)` ON DELETE SET NULL (self-referential)

### Notes
- `name` (full name) is computed: `name_f || ' ' || name_l` — not stored
- `address` is Phase 2 (separate table, FK added then)
- `managers` array from SPP becomes junction table in Phase 2
- `team_owner_ids` / `team_member_ids` from SPP are client-team relationships — defer to Phase 2
- `is_team_member` can be derived from role, no separate column needed
- `password_hash` nullable to support magic-link-only authentication

### Team vs Client Distinction
Team members: `role_id` references a role with `dashboard_access > 0`  
Clients: `role_id` references a role with `dashboard_access = 0`

API filtering for Team endpoint: `WHERE role_id IN (SELECT id FROM roles WHERE dashboard_access > 0)`  
API filtering for Clients endpoint: `WHERE role_id IN (SELECT id FROM roles WHERE dashboard_access = 0)`

---

## Table: `tags`

### Purpose
Categorization labels applied to orders, tickets, and potentially clients. Managed outside API (admin UI), read-only via API.

### Source Documentation
- Section 12. Tags — List endpoint only, simple structure

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `name` | `VARCHAR(255)` | NO | — | Tag name (unique) |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |

### Indexes
- `PRIMARY KEY (id)`
- `UNIQUE (name)`

### Notes
- No color or category fields in SPP API — keep minimal
- Tags are referenced by name (string) in Orders/Tickets, not by ID
- Junction tables for tag assignments created in later phases (Orders, Tickets)

---

## Junction Tables (Deferred)

These will be created in later phases when the referencing entities exist:

| Table | Created In | Purpose |
|-------|------------|---------|
| `order_tags` | Phase 4 | Orders ↔ Tags |
| `ticket_tags` | Phase 7 | Tickets ↔ Tags |
| `user_managers` | Phase 2 | Clients ↔ Team (managers array) |

---

## API Response Mapping

### GET /api/tags
```json
[
  {
    "id": 1,
    "name": "Tag name",
    "created_at": "2021-09-01T00:00:00+00:00",
    "updated_at": "2021-09-01T00:00:00+00:00"
  }
]
```
**Note:** Returns plain array, not paginated wrapper.

### GET /api/team
```json
{
  "data": [User],
  "links": {...},
  "meta": {...}
}
```
User object includes nested `role` object (full role data).

### GET /api/team/{id}
Returns single User object with nested `role`.

---

## Validation Rules

### Users
- `email`: Valid email format, unique
- `name_f`: Required, max 255 chars
- `name_l`: Required, max 255 chars
- `role_id`: Must exist in roles table
- `employee_id`: If set, must reference a team member (user with dashboard_access > 0)

### Roles
- `name`: Required, max 255 chars
- Permission integers: 0-3 only
- Permission booleans: true/false only

### Tags
- `name`: Required, unique, max 255 chars

---

## Migration Sequence

1. Create `roles` table
2. Seed default roles (Administrator, Client)
3. Create `users` table with FK to `roles`
4. Create `tags` table
5. Create indexes

---

## Open Questions (Require Decision)

### 1. Password Storage
**Question:** Use `bcrypt` or `argon2id` for password hashing?  
**Recommendation:** `argon2id` (modern, memory-hard)  
**Impact:** Application code only, no schema impact

### 2. Status Values
**Question:** Should we create a `user_statuses` reference table or use CHECK constraint?  
**Recommendation:** Store as `SMALLINT` with no constraint. Values undocumented in SPP — accept any integer, validate in application if needed later.  
**Impact:** Flexibility over strictness for v1

### 3. Custom Fields Schema
**Question:** Should `custom_fields` JSONB have any validation?  
**Recommendation:** No schema validation. Store arbitrary JSON. SPP doesn't document custom field structure.  
**Impact:** None — JSONB handles this naturally

---

## Approval Checklist

- [x] **UUID primary keys** — Confirmed
- [ ] Column types approved
- [ ] Nullable decisions approved
- [ ] Index strategy approved
- [ ] Team/Client distinction approach approved (role-based filtering)
- [ ] Deferred items acknowledged (address, managers, team relationships)
- [ ] Password hashing algorithm decided (`argon2id` recommended)
- [ ] Ready to generate SQL migration

---

*This document specifies Phase 1 schema only. Address table and client-specific junction tables are Phase 2.*
