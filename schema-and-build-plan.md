# Schema and Build Plan: service-engine-x

**Created:** January 19, 2026  
**Status:** Draft — Awaiting Approval  
**Purpose:** Define safe, staged build sequence for SPP-compatible database schema and API

---

## Executive Summary

This plan sequences the implementation of an SPP-compatible system across 6 phases. Each phase is designed to:
1. Unlock downstream work without rework
2. Preserve one-way dependencies (Orders are upstream truth)
3. Allow incremental testing and validation

**Core principle:** Build upstream entities first. Never implement something that references tables that don't exist.

---

## Global Design Decision: UUIDs

**All primary keys use UUID** (`id UUID PRIMARY KEY DEFAULT gen_random_uuid()`).

Rationale:
- API-first, multi-org system → avoids collisions and ID enumeration
- Safer for public APIs than sequential integers
- Easier for imports, async jobs, cross-environment work
- Aligns with Supabase/Postgres norms

Integers retained only for: enums, statuses, permission levels (0-3).

---

## 1. High-Level Phases

| Phase | Name | Purpose | Unlocks |
|-------|------|---------|---------|
| **1** | Foundation | Establish identity and configuration tables that everything references | User roles, team lookup, tag categorization |
| **2** | Clients | Create customer user infrastructure | All transactional entities (orders, invoices, tickets) |
| **3** | Services | Define purchasable products | Order creation |
| **4** | Orders | Implement the economic spine | Order-dependent work (tasks, messages, subscriptions) |
| **5** | Order Dependents | Attach downstream entities to orders | Full order lifecycle management |
| **6** | Financial Layer | Invoices, subscriptions, coupons | Payment processing, recurring billing |
| **7** | Support Layer | Tickets and ticket messages | Customer support workflows |
| **8** | Auxiliary | Form data, activities, logs, magic links | Complete API parity |

---

## 2. Per-Phase Scope

### Phase 1: Foundation

**Why this phase exists:**  
These are infrastructure tables that other entities reference. They exist independently of any transaction. Building them first means downstream tables can safely reference them from day one.

**Tables:**
- `roles`
- `users` (unified table for team + clients, differentiated by role)
- `tags`

**API Sections Enabled:**
- 12. Tags (read-only)
- 13. Team (read-only)

**Preconditions:**
- None — this is the starting point

**Notes:**
- `users` table is shared between Team and Clients (differentiated by `role_id`)
- Tags are read-only via API but must exist for Orders/Tickets to reference
- Permission integers (0-3) stored on roles, not enforced in v1

---

### Phase 2: Clients

**Why this phase exists:**  
Clients are required by Orders, Invoices, Tickets, and ClientActivities. Without the client infrastructure, no transactional entity can be created. This phase extends the `users` table with client-specific logic.

**Tables:**
- (Extends `users` table from Phase 1)
- `addresses` (billing/shipping for clients)

**API Sections Enabled:**
- 17. Clients (full CRUD)
- 6. MagicLink (generate — though can defer to Phase 8)

**Preconditions:**
- Phase 1 complete (roles, users table exists)

**Notes:**
- Client-specific fields: `balance`, `spent`, `stripe_id`, `employee_id`, `managers`, affiliate fields
- Address is a separate table (referenced by `address_id` or embedded JSON — decision point)

---

### Phase 3: Services

**Why this phase exists:**  
Orders require a service reference (`service_id` or fallback `service` name). Without services defined, orders cannot be created with proper pricing. This phase establishes the product catalog.

**Tables:**
- `services`
- `service_folders` (optional — for organization)

**API Sections Enabled:**
- 10. Services (full CRUD)

**Preconditions:**
- Phase 1 complete (roles exist for `employees` assignment)

**Notes:**
- Pricing complexity lives here: `f_price`, `r_price`, period types
- `recurring` field: 0=one-time, 1=recurring, 2=trial/setup
- Soft delete (`deleted_at`)

---

### Phase 4: Orders (Economic Core)

**Why this phase exists:**  
This is the central transaction entity. Everything downstream depends on it. Getting the Orders schema right is critical — changes here cascade everywhere.

**Tables:**
- `orders`

**API Sections Enabled:**
- 7. Orders (full CRUD)

**Preconditions:**
- Phase 1 complete (users/team for `employees` assignment)
- Phase 2 complete (clients for `user_id`)
- Phase 3 complete (services for `service_id`)

**Notes:**
- `user_id` (client) is required
- Either `service_id` OR `service` (string name) is required
- Status is integer in API, string in responses — need mapping table or enum
- Soft delete (`deleted_at`)
- `employees` is a many-to-many relationship (junction table needed)

---

### Phase 5: Order Dependents

**Why this phase exists:**  
These entities cannot exist without an order. They represent the work and communication that happens after an order is placed. Building them as a unit ensures the order lifecycle is complete.

**Tables:**
- `order_tasks`
- `order_messages`
- `order_employees` (junction table, may already exist from Phase 4)

**API Sections Enabled:**
- 1. Tasks (mark complete/incomplete — state mutations on `order_tasks`)
- 8. OrderMessages (create, list, delete — no update)
- 9. OrderTasks (full CRUD)

**Preconditions:**
- Phase 4 complete (orders exist)

**Notes:**
- Section 1 (Tasks) and Section 9 (OrderTasks) operate on the **same table**
- OrderMessages: hard delete, no update endpoint
- OrderTasks: hard delete
- `staff_only` flag on messages for internal notes

---

### Phase 6: Financial Layer

**Why this phase exists:**  
Invoices are first-class financial records. They can exist standalone (just client) OR linked to orders. Subscriptions are created implicitly via orders for recurring services. Coupons modify invoice totals.

**Tables:**
- `invoices`
- `invoice_items`
- `subscriptions`
- `coupons`

**API Sections Enabled:**
- 2. Coupons (full CRUD)
- 4. Invoices (full CRUD + charge + mark paid)
- 11. Subscriptions (read, update — no create/delete)

**Preconditions:**
- Phase 2 complete (clients for `user_id` on invoices)
- Phase 4 complete (orders for optional `order_id` linkage)

**Notes:**
- `invoices.order_id` is **nullable** — invoices can be standalone
- Subscriptions have no create endpoint — they're created when recurring orders are placed
- Subscription status values (0-4) not documented — store as-is
- Coupons reference service IDs in `discounts` array
- Soft delete on invoices and coupons

---

### Phase 7: Support Layer

**Why this phase exists:**  
Tickets are a parallel communication channel. They can exist independently OR be linked to orders. Building them after orders ensures the optional linkage works correctly.

**Tables:**
- `tickets`
- `ticket_messages`

**API Sections Enabled:**
- 14. Tickets (full CRUD)
- 15. TicketMessages (create, list, delete — no update)

**Preconditions:**
- Phase 2 complete (clients for `user_id`)
- Phase 4 complete (orders for optional `order_id` linkage)

**Notes:**
- `order_id` is optional on tickets
- TicketMessages: hard delete, no update endpoint
- `staff_only` flag on messages for internal notes
- Soft delete on tickets

---

### Phase 8: Auxiliary

**Why this phase exists:**  
These entities provide supporting functionality but are not critical to the core economic flow. They can be safely deferred and added last.

**Tables:**
- `filled_form_fields`
- `client_activities`
- `logs`

**API Sections Enabled:**
- 3. FilledFormFields (full CRUD)
- 5. Logs (read-only)
- 16. ClientActivities (full CRUD)
- 6. MagicLink (if not done in Phase 2)

**Preconditions:**
- Phase 2 complete (clients for `user_id`)
- Phase 4 complete (orders for form field linkage)
- Phase 7 complete (tickets for form field linkage)

**Notes:**
- FilledFormFields: hard delete, linked to either order OR ticket (mutually exclusive)
- Logs: pure audit trail, read-only, no write API
- ClientActivities: interaction tracking per client
- MagicLink: stateless generation, 2-hour expiry, no 2FA users

---

## 3. Dependency Justification

### Phase 1 → Everything
Roles and tags are referenced by virtually every other entity. Users (team) are assigned to orders, tasks, tickets. Without this foundation, foreign keys would be invalid.

### Phase 2 → Phases 4, 6, 7, 8
Clients are required by: Orders (`user_id`), Invoices (`user_id`), Tickets (`user_id`), ClientActivities (`user_id`). No transactional entity can exist without a client.

### Phase 3 → Phase 4
Orders require `service_id` (or fallback `service` name). The pricing model on services determines invoice amounts and subscription behavior.

### Phase 4 → Phases 5, 6, 7
Orders are the economic spine. OrderTasks, OrderMessages, Invoices (optionally), Tickets (optionally), and Subscriptions all reference orders.

### Phase 5 → None (terminal)
Order dependents are leaf nodes. Nothing references them except through the order.

### Phase 6 → None (mostly terminal)
Invoices can reference orders but are not referenced by anything else. Subscriptions are read from orders. Coupons are applied to invoices.

### Phase 7 → Phase 8
Tickets must exist before FilledFormFields can be attached to them.

### Phase 8 → None (terminal)
Auxiliary entities are leaf nodes with no downstream dependents.

---

## 4. Deferred Work

### Intentionally Deferred Tables

| Table/Concept | Reason for Deferral |
|---------------|---------------------|
| `service_options` / `option_variants` | Not documented in detail. API shows `option_categories` and `option_variants` arrays but schema is unclear. Safe to add later. |
| `service_addons` | Referenced via `addon_to` array. Relationship model unclear. Defer until core services work. |
| `form_schemas` | FilledFormFields exist but form definitions are not in API scope. Likely managed outside API. |
| `notification_settings` | Notifications mentioned in side effects but no API. Out of scope. |
| `stripe_webhooks` | Payment integration exists but webhook handling not documented. Implement during payment work. |
| `audit_log_retention` | Logs exist but retention policy not specified. Operational concern. |

### Intentionally Deferred Endpoints

| Endpoint | Reason |
|----------|--------|
| Coupon restore | Soft delete mentioned but no restore endpoint documented |
| Subscription cancel | No delete endpoint — status update only |
| Bulk operations | No batch endpoints documented |

---

## 5. Risk Notes

### High-Risk Phases (Hard to Reverse)

#### Phase 1: User Model Decision
**Risk:** Unified `users` table vs separate `team`/`clients` tables.  
**Recommendation:** Use unified table with `role_id` discriminator. SPP API returns same User object structure for both.  
**Mitigation:** Design role system carefully before implementation.

#### Phase 4: Order Schema
**Risk:** Orders are referenced by everything. Schema changes here require migrations across all dependent tables.  
**Recommendation:** Spend extra time validating order schema against all 7. Orders documentation before implementation.  
**Key decisions:**
- Status enum/mapping table design
- `employees` junction table structure
- `form_data` storage (JSON vs normalized)
- `metadata` storage approach

#### Phase 6: Invoice-Order Relationship
**Risk:** The nullable `order_id` on invoices is critical. Getting this wrong breaks the "invoices are first-class" principle.  
**Recommendation:** Explicitly test standalone invoice creation before moving on.

### Medium-Risk Areas

#### Status Value Mappings
Multiple entities use integer status in API but return string status in responses. The mapping is not documented.  
**Recommendation:** Create a `status_mappings` reference table or enum, but accept that values may need adjustment based on real SPP behavior.

#### Subscription Creation Trigger
Documentation says subscriptions are "created through orders" but the trigger mechanism isn't specified.  
**Recommendation:** Initially create subscriptions manually when orders are placed for recurring services. Refine automation later.

#### Soft Delete Consistency
Some entities soft delete, others hard delete. Mixed patterns can cause confusion.  
**Recommendation:** Add `deleted_at` column to all soft-delete tables from the start. Create a tracking document listing which entities are soft vs hard delete.

### Low-Risk Areas

- Tags (read-only, simple)
- Logs (read-only, append-only)
- MagicLink (stateless generation)
- ClientActivities (isolated from core flow)

---

## 6. Approval Checklist

Before proceeding to schema implementation:

- [x] Phase sequence approved
- [x] User model decision confirmed (unified table, role-based filtering)
- [x] **UUID primary keys** — Confirmed globally
- [ ] Status mapping strategy confirmed
- [ ] Address storage strategy confirmed (separate table vs embedded)
- [ ] `form_data` / `metadata` storage strategy confirmed
- [x] Soft delete column naming confirmed (`deleted_at`)

---

## 7. Next Steps

Upon approval of this plan:

1. **Phase 1 Schema Design** — Full column specification for `roles`, `users`, `tags`
2. **Phase 1 Migration** — SQL migration files
3. **Phase 1 API Implementation** — Tags (12), Team (13) endpoints
4. **Phase 1 Validation** — Test against expected SPP API behavior
5. Repeat for subsequent phases

---

*This document is a sequencing artifact. It does not contain final schema specifications.*
