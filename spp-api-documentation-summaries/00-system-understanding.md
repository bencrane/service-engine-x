# SPP API System Understanding

This document confirms my understanding of the SPP API system based on the documentation processed.

---

## Core Economic Spine

### Primary Entities (Independent, Pre-exist Transactions)
1. **Services** - Products/offerings that can be ordered. Exist independently. Define pricing, recurring billing, deadlines.
2. **Clients** - Customer users who place orders. Exist independently. Have accounts, balances, addresses.
3. **Team** - Staff users who manage operations. Exist independently. Have roles and permissions.

### Transaction Entity (Central Hub)
4. **Orders** - The core transaction. Links a Client to a Service. Everything downstream flows from Orders.

### Financial Entities (First-Class)
5. **Invoices** - Financial records. Can be generated from Orders OR created standalone. Always belong to a Client. First-class authoritative financial truth.
6. **Subscriptions** - Recurring billing relationships. Created automatically when Orders are placed for recurring Services. Cannot be created directly via API.

### Communication Entities (Attached to Transactions)
7. **OrderMessages** - Messages on orders (client ↔ staff communication)
8. **OrderTasks** - Work items to complete for an order
9. **Tickets** - Support requests. Can exist independently but often linked to Orders.
10. **TicketMessages** - Messages on tickets

### Supporting Entities
11. **Tags** - Categorization labels. Applied to Orders, Tickets, Clients.
12. **Coupons** - Promotional discounts. Applied to Invoices at checkout.
13. **FilledFormFields** - Submitted form data. Attached to Orders or Tickets.
14. **ClientActivities** - Activity logs for clients (calls, interactions).
15. **Logs** - System-wide activity/audit trail.
16. **MagicLink** - Passwordless login tokens for clients.

---

## Pre-Client, Pre-Purchase Entities

These entities can exist before any client signs up or any purchase is made:

| Entity | Rationale |
|--------|-----------|
| **Services** | Products must be defined before they can be sold |
| **Team** | Staff users manage the system |
| **Tags** | Categorization system ready for use |
| **Coupons** | Promotional codes created in advance |

---

## One-Way Dependencies

### What Requires Orders (Order is upstream)
| Entity | Dependency |
|--------|------------|
| OrderMessages | Cannot exist without an Order |
| OrderTasks | Cannot exist without an Order |
| Subscriptions | Created through Orders for recurring Services |

**Note**: Invoices do NOT require Orders. They can optionally link to an Order (`order_id` nullable) but are first-class entities requiring only a Client.

### What Requires Clients (Client is upstream)
| Entity | Dependency |
|--------|------------|
| Orders | `user_id` required |
| Tickets | `user_id` required |
| Invoices | `user_id` required |
| ClientActivities | `user_id` required |
| MagicLink | Generated for specific client |

### What Requires Services (Service is upstream)
| Entity | Dependency |
|--------|------------|
| Orders | `service_id` required (or `service` name as fallback) |

### What Never Affects Orders (Downstream/Read-only)
| Entity | Rationale |
|--------|-----------|
| Tags | Read-only categorization, no write-back |
| Logs | Audit trail, purely observational |
| Team | Staff data, no impact on order data |
| MagicLink | Authentication utility, no order relationship |

---

## Endpoint Authority Classification

### Authoritative (Full CRUD)
| Section | Entity | Create | Read | Update | Delete |
|---------|--------|--------|------|--------|--------|
| 2 | Coupons | ✓ | ✓ | ✓ | ✓ |
| 3 | FilledFormFields | ✓ | ✓ | ✓ | ✓ |
| 4 | Invoices | ✓ | ✓ | ✓ | ✓ |
| 7 | Orders | ✓ | ✓ | ✓ | ✓ |
| 9 | OrderTasks | ✓ | ✓ | ✓ | ✓ |
| 10 | Services | ✓ | ✓ | ✓ | ✓ |
| 14 | Tickets | ✓ | ✓ | ✓ | ✓ |
| 16 | ClientActivities | ✓ | ✓ | ✓ | ✓ |
| 17 | Clients | ✓ | ✓ | ✓ | ✓ |

### Partial Authority (Limited Write)
| Section | Entity | Operations | Notes |
|---------|--------|------------|-------|
| 1 | Tasks | Mark complete/incomplete only | No CRUD, just state toggle |
| 8 | OrderMessages | Create, Delete | No Update |
| 11 | Subscriptions | Read, Update | No Create (via Orders), No Delete |
| 15 | TicketMessages | Create, Delete | No Update |

### Read-Only / Derivative
| Section | Entity | Operations | Notes |
|---------|--------|------------|-------|
| 5 | Logs | List only | Pure audit trail |
| 12 | Tags | List only | Managed outside API |
| 13 | Team | List, Retrieve | Staff managed outside API |

### Special Purpose
| Section | Entity | Operations | Notes |
|---------|--------|------------|-------|
| 4.1 | Invoice Charge | POST | Charges via Stripe payment method |
| 4.7 | Invoice Mark Paid | POST | Manual payment recording |
| 6 | MagicLink | GET (generates) | Creates login token |

---

## Ambiguities and Assumptions

### Status Values Not Documented
- **Orders**: `status` is integer in requests, string in responses. Values not mapped.
- **Subscriptions**: Allowed values `0, 1, 2, 3, 4` but meanings not documented.
- **Tickets**: `status` is integer in requests, string in responses.
- **Clients**: `status` integer values not documented.
- **Invoices**: `status_id` values not mapped to `status` strings.

### Tasks vs OrderTasks Relationship
- Section 1 (Tasks) provides `mark complete/incomplete` endpoints.
- Section 9 (OrderTasks) provides full CRUD for tasks on orders.
- **CONFIRMED**: Tasks (Section 1) are state mutations on OrderTasks, not a separate entity. Section 1 endpoints are convenience endpoints for toggling completion status on the same underlying records.
- **Schema Implication**: One table (`order_tasks`). Do NOT create a separate `tasks` table.

### Subscription Creation
- Documentation states subscriptions are "created through orders."
- No explicit documentation on the trigger mechanism.
- **Assumption**: When an Order is created for a recurring Service, a Subscription is automatically generated.

### Invoice-Order Relationship
- Invoices can be created standalone with `user_id` and `items`.
- Invoices can also be generated from Orders.
- **CONFIRMED**: Invoices are first-class financial records regardless of origin. They always belong to a client. Order linkage is optional.
- **Schema Implication**: `invoices.order_id` is nullable. Invoices remain authoritative financial truth whether standalone or order-derived.

### Form Data Origin
- `form_data` appears on Orders and Tickets as submitted data.
- FilledFormFields API manages this data.
- **Ambiguity**: How form schemas are defined (likely in Services/Tickets config) is not documented in these API sections.

### Soft vs Hard Deletes
- Orders: "can be undone" → Soft delete
- Services: "can be undone" → Soft delete
- Tickets: "can be undone" → Soft delete
- Invoices: "can be undone" → Soft delete
- FilledFormFields: "cannot be undone" → Hard delete
- OrderMessages: "cannot be undone" → Hard delete
- TicketMessages: "cannot be undone" → Hard delete
- OrderTasks: "cannot be undone" → Hard delete
- **CONFIRMED**: Soft deletes use `deleted_at` timestamp. Hard deletes physically remove records.
- **Schema Implication**: Add `deleted_at TIMESTAMPTZ NULL` column to soft-delete entities (orders, services, tickets, invoices). Physical DELETE only where docs say "cannot be undone".

### Payment Processing
- Invoice charge requires Stripe `payment_method_id` (format: `pm_xxx`).
- Invoice mark paid is for manual/offline payments.
- **Assumption**: System is tightly coupled to Stripe for payment processing. Braintree fields exist on Services but integration not documented.

### Permission Levels
- Role permissions use integers 0-3.
- **Documented**: 0=None, 1=Own, 2=Group, 3=All
- **Assumption**: "Own" means user's own records, "Group" means team/department, "All" means full access.
- **CONFIRMED**: We do not need to fully replicate SPP's permission model. Integers 0-3 can be stored, but enforcement can be minimal in v1.
- **Schema Implication**: Store permission integers as-is. Full enforcement is not required for initial implementation.

### Period Type Codes
- Services use `f_period_t` and `r_period_t` with values like `D`, `M`.
- **Assumption**: D=Day, W=Week, M=Month, Y=Year (not explicitly documented).

---

## Entity Relationship Summary

```
┌─────────────┐     ┌─────────────┐
│   Service   │     │   Client    │
└──────┬──────┘     └──────┬──────┘
       │                   │
       │    ┌──────────────┤
       │    │              │
       ▼    ▼              │
    ┌──────────┐           │
    │  Order   │◄──────────┤
    └────┬─────┘           │
         │                 │
    ┌────┴────┬────────┐   │
    ▼         ▼        ▼   │
┌────────┐ ┌──────┐ ┌─────────────┐
│Invoice │ │Tasks │ │  Messages   │
└────────┘ └──────┘ └─────────────┘
    │
    ▼
┌──────────────┐
│ Subscription │ (if recurring)
└──────────────┘

┌─────────────┐
│   Ticket    │◄─── Client (required)
└──────┬──────┘◄─── Order (optional)
       │
       ▼
┌─────────────┐
│  Messages   │
└─────────────┘
```

---

## Schema Implications Summary (Validated)

Based on clarifications received, the following schema decisions are confirmed:

| Decision | Implication |
|----------|-------------|
| Tasks = OrderTasks | Single `order_tasks` table. No separate `tasks` table. |
| Invoices first-class | `invoices.order_id` is nullable. Invoices are authoritative regardless of order linkage. |
| Permissions minimal v1 | Store permission integers 0-3 as-is. Full enforcement not required initially. |
| Soft delete pattern | `deleted_at TIMESTAMPTZ NULL` on: orders, services, tickets, invoices |
| Hard delete entities | Physical DELETE on: filled_form_fields, order_messages, ticket_messages, order_tasks |

---

*Document generated from SPP API documentation analysis. Validated with clarifications.*
