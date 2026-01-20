# Phase 6 Schema Plan: Financial Layer

**Created:** January 19, 2026  
**Status:** Draft — Awaiting Approval  
**Scope:** `invoices`, `invoice_items`, `subscriptions`, `coupons`

---

## Overview

Phase 6 implements the financial layer. Invoices and subscriptions are downstream of orders but have distinct lifecycles:
- **Invoices** are first-class entities that can exist with or without an order
- **Subscriptions** are created as a side effect of recurring orders, but orders don't require them

**API Sections Enabled:**
- 2. Coupons (full CRUD)
- 4. Invoices (full CRUD + charge + mark paid)
- 11. Subscriptions (list, retrieve, update — no create/delete)

**What This Phase Unlocks:**
- Invoice generation and payment tracking
- Coupon management and application
- Subscription status tracking
- `orders.invoice_id` and `orders.subscription_id` references

**What This Phase Does NOT Include:**
- Payment processor webhooks
- Transaction/payment tables
- Refund tracking
- Accounting ledger
- Stripe integration logic

---

## Tables in This Phase

| Table | Purpose |
|-------|---------|
| `coupons` | Discount codes with usage rules |
| `invoices` | Payment requests (first-class, may exist without order) |
| `invoice_items` | Line items on invoices |
| `subscriptions` | Recurring billing tracking |

---

## Table: `coupons`

### Purpose
Discount codes that can be applied to orders/invoices. Supports percentage and fixed discounts, usage limits, expiration dates, and service-specific targeting.

### Source Documentation
- Section 2.1–2.5 Coupons API

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `code` | `VARCHAR(100)` | NO | — | Coupon code (unique) |
| `type` | `VARCHAR(50)` | NO | — | Discount type (e.g., "percentage", "fixed") |
| `description` | `TEXT` | YES | — | Coupon description |
| `discounts` | `JSONB` | NO | `'[]'` | Discount config: `[{amount, services}]` |
| `date_expires` | `TIMESTAMPTZ` | YES | — | Expiration date |
| `new_customers` | `BOOLEAN` | NO | `false` | Only for new customers |
| `single_use` | `BOOLEAN` | NO | `false` | Single use per customer |
| `single_quantity` | `BOOLEAN` | NO | `false` | Single quantity only |
| `duration` | `BOOLEAN` | NO | `false` | Applies to subscription duration |
| `usage_limit` | `INTEGER` | YES | — | Maximum total uses |
| `min_cart_amount` | `DECIMAL(12,2)` | YES | — | Minimum cart value required |
| `used_count` | `INTEGER` | NO | `0` | Times used |
| `affiliate` | `JSONB` | YES | — | Affiliate info (structure undocumented) |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | YES | — | Soft delete timestamp |

### Indexes
- `PRIMARY KEY (id)`
- `UNIQUE (code)` — coupon codes must be unique
- `INDEX (deleted_at)` — soft delete filtering
- `INDEX (date_expires)` — expiration queries

### Soft Delete
Coupons use **soft delete**. Per SPP docs: "It can be undone."

### Notes
- `discounts` is JSONB array: `[{"amount": 10, "services": [uuid1, uuid2]}]`
- `type` values undocumented — store as string ("percentage", "fixed", etc.)
- `affiliate` structure undocumented — store as JSONB

---

## Table: `invoices`

### Purpose
Payment requests to clients. First-class entity that can exist independently of orders (e.g., manual invoices, adjustments). Contains billing snapshot data.

### Source Documentation
- Section 4.1–4.7 Invoices API

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `number` | `VARCHAR(50)` | NO | — | Invoice number (unique) |
| `number_prefix` | `VARCHAR(20)` | YES | — | Number prefix (e.g., "SPP-") |
| `user_id` | `UUID` | NO | — | FK to users.id (client) |
| `employee_id` | `UUID` | YES | — | FK to users.id (who created) |
| `coupon_id` | `UUID` | YES | — | FK to coupons.id (applied coupon) |
| `billing_address` | `JSONB` | YES | — | Billing address snapshot |
| `status_id` | `SMALLINT` | NO | `0` | Status ID (values undocumented) |
| `currency` | `VARCHAR(3)` | NO | `'USD'` | Currency code (ISO 4217) |
| `subtotal` | `DECIMAL(12,2)` | NO | `0.00` | Subtotal before tax/discount |
| `tax` | `DECIMAL(12,2)` | NO | `0.00` | Tax amount |
| `tax_name` | `VARCHAR(100)` | YES | — | Tax label (e.g., "VAT") |
| `tax_percent` | `DECIMAL(5,2)` | YES | — | Tax percentage |
| `credit` | `DECIMAL(12,2)` | NO | `0.00` | Credit applied |
| `total` | `DECIMAL(12,2)` | NO | `0.00` | Final total |
| `date_due` | `TIMESTAMPTZ` | YES | — | Due date |
| `date_paid` | `TIMESTAMPTZ` | YES | — | When paid |
| `reason` | `VARCHAR(255)` | YES | — | Invoice reason |
| `note` | `TEXT` | YES | — | Internal note |
| `ip_address` | `VARCHAR(45)` | YES | — | Client IP at creation |
| `loc_confirm` | `BOOLEAN` | NO | `false` | Location confirmed flag |
| `recurring` | `JSONB` | YES | — | Recurring config: `{r_period_l, r_period_t}` |
| `paysys` | `VARCHAR(50)` | YES | — | Payment system used |
| `transaction_id` | `VARCHAR(255)` | YES | — | External transaction ID |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | YES | — | Soft delete timestamp |

### Indexes
- `PRIMARY KEY (id)`
- `UNIQUE (number)` — invoice numbers must be unique
- `INDEX (user_id)` — client invoices
- `INDEX (status_id)` — status filtering
- `INDEX (date_due)` — due date queries
- `INDEX (deleted_at)` — soft delete filtering

### Foreign Keys
- `user_id` (UUID) → `users(id)` ON DELETE RESTRICT
- `employee_id` (UUID) → `users(id)` ON DELETE SET NULL
- `coupon_id` (UUID) → `coupons(id)` ON DELETE SET NULL

### Soft Delete
Invoices use **soft delete**. Per SPP docs: "Deletion is soft delete (can be undone)."

### Column Justifications

| Column | Why It Exists |
|--------|---------------|
| `billing_address` | **Snapshot** — preserved even if client address changes |
| `status_id` | Integer status (values undocumented) |
| `subtotal`, `tax`, `total` | Computed once, stored as snapshots |
| `recurring` | Config for recurring invoice generation |
| `paysys`, `transaction_id` | Payment tracking |
| `ip_address`, `loc_confirm` | Fraud/compliance fields |

### What Is NOT Stored

| Field | Reason |
|-------|--------|
| `status` (string) | Computed from `status_id` at API layer |
| `view_link`, `download_link`, `thanks_link` | Generated at API layer |
| `client` | Joined from `user_id` |

---

## Table: `invoice_items`

### Purpose
Line items on invoices. Each item represents a product/service being billed. Items may optionally reference an order and/or service.

### Source Documentation
- Section 4.2 Invoices API — InvoiceItem object

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `invoice_id` | `UUID` | NO | — | FK to invoices.id |
| `order_id` | `UUID` | YES | — | FK to orders.id (if from order) |
| `service_id` | `UUID` | YES | — | FK to services.id (if from catalog) |
| `name` | `VARCHAR(255)` | NO | — | Item name |
| `description` | `TEXT` | YES | — | Item description |
| `amount` | `DECIMAL(12,2)` | NO | `0.00` | Unit price |
| `quantity` | `INTEGER` | NO | `1` | Quantity |
| `discount` | `DECIMAL(12,2)` | NO | `0.00` | Primary discount |
| `discount2` | `DECIMAL(12,2)` | NO | `0.00` | Secondary discount |
| `total` | `DECIMAL(12,2)` | NO | `0.00` | Line total |
| `options` | `JSONB` | NO | `'{}'` | Selected options snapshot |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |

### Indexes
- `PRIMARY KEY (id)`
- `INDEX (invoice_id)` — items for an invoice
- `INDEX (order_id)` — items from an order
- `INDEX (service_id)` — items for a service

### Foreign Keys
- `invoice_id` (UUID) → `invoices(id)` ON DELETE CASCADE
- `order_id` (UUID) → `orders(id)` ON DELETE SET NULL
- `service_id` (UUID) → `services(id)` ON DELETE SET NULL

### Notes
- `order_id` nullable — invoice items can exist without an order
- `service_id` nullable — items can be custom line items
- `options` stores selected service options as snapshot
- `discount` and `discount2` purpose undocumented — store both

---

## Table: `subscriptions`

### Purpose
Tracks recurring billing for services. Created as side effect of orders for recurring services. Managed through status changes, not CRUD.

### Source Documentation
- Section 11.1–11.3 Subscriptions API

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | NO | `gen_random_uuid()` | Primary key |
| `number` | `VARCHAR(50)` | YES | — | Subscription number |
| `user_id` | `UUID` | NO | — | FK to users.id (client) |
| `status` | `SMALLINT` | NO | `1` | Status (0-4, values undocumented) |
| `processor_id` | `VARCHAR(255)` | YES | — | External processor ID (Stripe) |
| `current_period_end` | `TIMESTAMPTZ` | YES | — | Current billing period end |
| `payment_count` | `INTEGER` | NO | `0` | Total payments made |
| `created_at` | `TIMESTAMPTZ` | NO | `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NO | `now()` | Last update timestamp |

### Indexes
- `PRIMARY KEY (id)`
- `UNIQUE (number)` — subscription numbers unique (if set)
- `INDEX (user_id)` — client subscriptions
- `INDEX (status)` — status filtering
- `INDEX (processor_id)` — external ID lookup

### Foreign Keys
- `user_id` (UUID) → `users(id)` ON DELETE RESTRICT

### No Soft Delete
Subscriptions are managed through status changes (0=Canceled, 1=Active, etc.), not deletion. No `deleted_at` column.

### Notes
- **No create/delete API endpoints** — subscriptions created via order processing
- `status` values 0-4 are allowed but meanings undocumented
- `processor_id` is the Stripe subscription ID
- `payments` array in API response is derived from invoices, not stored
- `orders` array in API response comes from FK on orders table

---

## Orders Table Modification

### New Columns to Add

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `invoice_id` | `UUID` | YES | — | FK to invoices.id |
| `subscription_id` | `UUID` | YES | — | FK to subscriptions.id |

### New Foreign Keys
- `invoice_id` (UUID) → `invoices(id)` ON DELETE SET NULL
- `subscription_id` (UUID) → `subscriptions(id)` ON DELETE SET NULL

### Why Nullable
- Orders can exist without an invoice (e.g., free orders, pending)
- Orders can exist without a subscription (one-time purchases)
- These are convenience references, not required dependencies

### One-Way Dependency Preserved
- Orders reference invoices/subscriptions
- Invoices/subscriptions exist independently
- Deleting an invoice/subscription sets the order's FK to NULL

---

## Dependency Diagram

```
Phase 1                    Phase 6
─────────                  ─────────
┌─────────┐               ┌─────────────┐
│  users  │◄──────────────┤   coupons   │ (no FK, but referenced)
└────┬────┘               └──────┬──────┘
     │                           │
     │ user_id                   │ coupon_id
     │                           │
     │                    ┌──────▼──────┐
     ├───────────────────►│  invoices   │◄─────┐
     │                    └──────┬──────┘      │
     │                           │             │
     │                           │ invoice_id  │
     │                           ▼             │
     │                    ┌─────────────┐      │
     │                    │invoice_items│      │
     │                    └─────────────┘      │
     │                                         │
     │                    ┌─────────────┐      │
     ├───────────────────►│subscriptions│      │
     │                    └──────┬──────┘      │
     │                           │             │
     │                           │             │
Phase 4                          │             │
─────────                        │             │
┌─────────┐                      │             │
│  orders │──────────────────────┴─────────────┘
└─────────┘     invoice_id, subscription_id (added)
```

---

## One-Way Dependency Enforcement

**Critical Design Principle:**
- Invoices exist independently of orders (user_id required, order references optional)
- Subscriptions exist independently of orders (created as side effect, but self-sufficient)
- Orders can reference invoices/subscriptions via nullable FKs
- Invoice items can reference orders, but orders don't require items

| Entity | References Orders? | Orders References It? |
|--------|-------------------|----------------------|
| `invoices` | NO | YES (nullable invoice_id) |
| `invoice_items` | YES (nullable order_id) | NO |
| `subscriptions` | NO | YES (nullable subscription_id) |
| `coupons` | NO | NO (referenced by invoices) |

---

## Explicit Deferrals

### Deferred: Payments/Transactions Table

**Fields:** `payments` array in subscription, `transaction_id` in invoice

**Reason:**
- Payment history requires separate table
- Depends on webhook integration with Stripe
- `transaction_id` on invoice handles single-payment case

**Future Implementation:**
- `payments` table with invoice_id, amount, paysys, processor_transaction_id, created_at

### Deferred: Refunds

**Reason:**
- Refund logic not documented in SPP API
- Requires payment processor integration
- Can be added without schema changes (new table)

### Deferred: Stripe Webhooks

**Reason:**
- Webhook handling is application logic, not schema
- Subscription status sync handled via API updates

### Deferred: Invoice PDF Generation

**Fields:** `view_link`, `download_link`

**Reason:**
- URL generation is application concern
- Requires file storage / PDF generation service

---

## Status Values (Undocumented)

### Invoice Status (`status_id`)
| Value | Likely Meaning |
|-------|----------------|
| 0 | Draft |
| 1 | Unpaid |
| 2 | Paid |
| 3 | Partially Paid |
| 4 | Cancelled |

### Subscription Status (`status`)
| Value | Likely Meaning |
|-------|----------------|
| 0 | Inactive/Canceled |
| 1 | Active |
| 2 | Paused |
| 3 | Past Due |
| 4 | Expired |

**Note:** Store raw integers. Map to strings at API layer when confirmed.

---

## Validation Rules

### Coupons
- `code`: Required, unique, max 100 chars
- `type`: Required, max 50 chars
- `discounts`: Valid JSON array

### Invoices
- `number`: Required, unique, max 50 chars
- `user_id`: Required, must exist in users table (client)
- `currency`: Required, 3 chars (ISO 4217)
- `total`, `subtotal`, `tax`: Non-negative

### Invoice Items
- `invoice_id`: Required, must exist
- `name`: Required, max 255 chars
- `amount`: Non-negative
- `quantity`: Positive integer

### Subscriptions
- `user_id`: Required, must exist in users table (client)
- `status`: Integer 0-4

---

## Migration Sequence

1. Create `coupons` table (no dependencies)
2. Create `invoices` table with FKs to `users` and `coupons`
3. Create `invoice_items` table with FKs to `invoices`, `orders`, `services`
4. Create `subscriptions` table with FK to `users`
5. Add `invoice_id` and `subscription_id` columns to `orders` table
6. Create indexes

---

## Approval Checklist

- [ ] `coupons` table structure approved
- [ ] `invoices` table structure approved
- [ ] `invoice_items` table structure approved
- [ ] `subscriptions` table structure approved
- [ ] `orders.invoice_id` (nullable) approved
- [ ] `orders.subscription_id` (nullable) approved
- [ ] Soft delete for coupons and invoices approved
- [ ] No soft delete for subscriptions (status-managed) approved
- [ ] `billing_address` as JSONB snapshot approved
- [ ] One-way dependencies preserved
- [ ] Deferred items acknowledged (payments, refunds, webhooks)
- [ ] Ready to generate SQL migration

---

*This document specifies Phase 6 schema only. Tickets (Phase 7) and beyond are out of scope.*
