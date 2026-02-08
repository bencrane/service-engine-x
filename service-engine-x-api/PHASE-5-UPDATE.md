# Phase 5 Complete: Proposals & Invoices API

**Date:** 2026-02-07
**Status:** Complete

## Summary

Phase 5 implemented the full Proposals and Invoices APIs including workflow actions (send/sign for proposals, charge/mark_paid for invoices).

## What Was Built

### New Files

```
app/
├── models/
│   ├── proposals.py      # Proposal request/response schemas
│   └── invoices.py       # Invoice request/response schemas
├── routers/
│   ├── proposals.py      # Proposals CRUD + send/sign workflows
│   └── invoices.py       # Invoices CRUD + charge/mark_paid workflows
tests/
├── test_proposals.py     # 5 proposal endpoint tests
└── test_invoices.py      # 7 invoice endpoint tests
```

### Endpoints Implemented (12 total)

#### Proposals Router (`/api/proposals`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/proposals` | List proposals with pagination |
| POST | `/api/proposals` | Create proposal with items |
| GET | `/api/proposals/{id}` | Retrieve proposal with items |
| POST | `/api/proposals/{id}/send` | Send proposal (Draft → Sent) |
| POST | `/api/proposals/{id}/sign` | Sign proposal (Sent → Signed), creates order |

#### Invoices Router (`/api/invoices`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/invoices` | List invoices with pagination |
| POST | `/api/invoices` | Create invoice with items |
| GET | `/api/invoices/{id}` | Retrieve invoice with client + items |
| PUT | `/api/invoices/{id}` | Update invoice (full item replacement) |
| DELETE | `/api/invoices/{id}` | Soft delete invoice |
| POST | `/api/invoices/{id}/charge` | Charge invoice via Stripe (stub) |
| POST | `/api/invoices/{id}/mark_paid` | Mark invoice as manually paid |

### Key Features

#### Proposals

1. **Status System**
   - 0 = Draft
   - 1 = Sent
   - 2 = Signed
   - 3 = Rejected

2. **Proposal Items**
   - Link to services via `service_id`
   - Store quantity and price per item
   - Auto-calculate total from items

3. **Send Workflow**
   - Validates proposal is in Draft status
   - Updates status to Sent, sets `sent_at`

4. **Sign Workflow**
   - Validates proposal is in Sent status
   - Find-or-create client by email
   - Creates order with proposal metadata snapshot
   - Updates status to Signed, sets `signed_at` and `converted_order_id`

#### Invoices

1. **Status System**
   - 0 = Draft
   - 1 = Unpaid
   - 3 = Paid
   - 4 = Refunded
   - 5 = Cancelled
   - 7 = Partially Paid

2. **Status Transitions**
   ```
   Draft(0) → Unpaid(1), Cancelled(5)
   Unpaid(1) → Draft(0), Cancelled(5)
   Paid(3) → Refunded(4) only
   Refunded(4) → terminal (no transitions)
   Cancelled(5) → Draft(0), Unpaid(1)
   PartiallyPaid(7) → Paid(3), Refunded(4), Cancelled(5)
   ```

3. **Invoice Items**
   - name, description, quantity, amount, discount
   - Optional service_id linking
   - Full replacement on update (delete old, insert new)

4. **Client Resolution**
   - Accept `user_id` OR `email`
   - Auto-create client if email not found
   - Snapshot billing address from client

5. **Invoice Number Generation**
   - Format: `INV-00001`
   - Auto-incrementing based on count

6. **Charge Workflow**
   - Validates not already paid
   - Simulates Stripe payment (stub)
   - Creates orders for items with service_id
   - Links items to created orders

7. **Mark Paid Workflow**
   - Idempotent (returns current state if already paid)
   - Sets paysys to "Manual"
   - Creates orders for items with service_id
   - Creates subscription if recurring is configured

8. **Recurring Invoices**
   - `r_period_l`: period length (integer)
   - `r_period_t`: period type (M=Month, W=Week, D=Day)
   - Creates subscription record on mark_paid

### Database Tables

**Proposals:**
- `proposals` - Main proposal records
- `proposal_items` - Line items linked to services

**Invoices:**
- `invoices` - Main invoice records
- `invoice_items` - Line items with pricing

**Related:**
- `users` - Client records (created on proposal sign or invoice create)
- `orders` - Created from signed proposals or paid invoices
- `subscriptions` - Created for recurring invoices

### Multi-tenant Security

- All operations filter by `org_id`
- Client creation scoped to org
- Service validation scoped to org

## Tests

40 tests passing:
- 5 proposals tests (new)
- 7 invoices tests (new)
- 10 orders tests
- 4 order-tasks tests
- 1 order-messages test
- 6 services tests
- 6 clients tests
- 2 health tests

## Response Examples

**Proposal Response:**
```json
{
  "id": "uuid",
  "client_email": "john@example.com",
  "client_name": "John Doe",
  "client_name_f": "John",
  "client_name_l": "Doe",
  "client_company": "Acme Inc",
  "status": "Sent",
  "status_id": 1,
  "total": "1500.00",
  "notes": "Web development proposal",
  "created_at": "2026-02-07T...",
  "sent_at": "2026-02-07T...",
  "signed_at": null,
  "converted_order_id": null,
  "items": [
    {
      "id": "uuid",
      "service_id": "uuid",
      "service_name": "Web Development",
      "quantity": 1,
      "price": "1500.00"
    }
  ]
}
```

**Invoice Response:**
```json
{
  "id": "uuid",
  "number": "INV-00001",
  "number_prefix": "INV-",
  "client": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "address": {...}
  },
  "items": [
    {
      "id": "uuid",
      "name": "Web Development",
      "quantity": 1,
      "amount": "1500.00",
      "discount": "0.00",
      "total": "1500.00",
      "order_id": "uuid"
    }
  ],
  "billing_address": {...},
  "status": "Paid",
  "status_id": 3,
  "subtotal": "1500.00",
  "tax": "0.00",
  "total": "1500.00",
  "date_due": "2026-02-21T...",
  "date_paid": "2026-02-07T...",
  "transaction_id": "txn_123...",
  "paysys": "Manual",
  "recurring": null
}
```

## Next: Phase 6 - Tickets & Polish

Phase 6 will implement:
- Tickets API (CRUD + messages)
- Final polish and cleanup
- OpenAPI documentation updates
