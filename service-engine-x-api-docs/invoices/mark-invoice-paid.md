# Mark Invoice Paid

```
POST /api/invoices/{id}/mark_paid
```

---

## 1. Purpose

Manually mark an invoice as paid without processing a payment through a payment processor. Used for offline payments, bank transfers, or manual reconciliation.

**This endpoint is idempotent.** Calling it on an already-paid invoice returns 200 OK with the unchanged invoice.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated **staff** with invoice management permissions.

| User Type | Can Mark Paid |
|-----------|---------------|
| Staff (invoice_management) | ✅ Yes |
| Staff (invoice_access only) | ❌ No |
| Client | ❌ No |

Clients cannot mark invoices paid — this is a staff-only operation for offline reconciliation.

---

## 3. Request

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | **Yes** | Invoice identifier. |

### Request Headers

| Header | Type | Required |
|--------|------|----------|
| `Authorization` | string | Yes |
| `Content-Type` | string | Yes (`application/json`) |
| `Accept` | string | Yes (`application/json`) |

### Request Body

None required. Empty body or `{}` accepted.

---

## 4. Field Semantics

### Fields Modified on Success

| Field | Before | After |
|-------|--------|-------|
| `status_id` | 1 (Unpaid) | 3 (Paid) |
| `status` | "Unpaid" | "Paid" |
| `date_paid` | null | Current timestamp |
| `paysys` | null | "Manual" |

---

## 5. Side Effects

| Effect | Description |
|--------|-------------|
| **Invoice status updated** | Marked as Paid |
| **paysys set to Manual** | Indicates non-processor payment |
| **Client balance updated** | Spent amount recalculated |
| **Orders created** | If invoice items have service_id |
| **Subscription created** | If recurring invoice |

---

## 6. Response Shape

### 200 OK

Returns the full updated invoice object.

```json
{
  "id": "uuid",
  "number": "INV-00042",
  "client": { ... },
  "items": [ ... ],
  "billing_address": { ... },
  "status": "Paid",
  "status_id": 3,
  "created_at": "2024-01-15T10:00:00Z",
  "date_due": "2024-02-14T10:00:00Z",
  "date_paid": "2024-01-20T14:30:00Z",
  "credit": "0.00",
  "tax": "50.00",
  "tax_name": "Sales Tax",
  "tax_percent": "10.00",
  "currency": "USD",
  "subtotal": "500.00",
  "total": "550.00",
  "transaction_id": null,
  "paysys": "Manual",
  "recurring": null,
  "coupon_id": null,
  "view_link": "https://...",
  "download_link": "https://...",
  "thanks_link": "https://..."
}
```

---

## 7. Error Behavior

### 400 Bad Request

Invoice cannot be marked paid.

```json
{
  "message": "Invoice has no client assigned."
}
```

**Common causes:**
- Invoice has no client assigned
- Invoice is in Cancelled or Refunded status

### 401 Unauthorized

Missing or invalid Bearer token.

```json
{
  "error": "Unauthorized"
}
```

### 404 Not Found

Invoice does not exist or is soft-deleted.

```json
{
  "error": "Not Found"
}
```

---

## 8. Notes / Edge Cases

### Idempotent Behavior

Marking an already-paid invoice is a **no-op**:
- Returns 200 OK
- Invoice unchanged
- No side effects triggered
- Safe to retry

This enables safe retries and webhook reconciliation without error handling for "already paid" cases.

### Invoice Must Have Client

Invoices without an assigned client cannot be marked paid:

```json
{
  "message": "Invoice has no client assigned."
}
```

This is required because:
- Orders must be created for a client
- Subscriptions are per-client
- Client spend tracking requires client reference

### No Transaction ID

Unlike `charge`, manual payment does NOT set `transaction_id`:
- No processor reference exists
- Use invoice number for external tracking

### Order Creation

Same as `charge` endpoint:
1. For each item with `service_id`: an Order is created
2. Orders linked to invoice
3. Order status per service configuration

### Subscription Creation

For recurring invoices:
1. Subscription created for client
2. Next invoice scheduled
3. Future invoices will be unpaid (require separate payment)

### Contrast with Charge

| Aspect | charge | mark_paid |
|--------|--------|-----------|
| Payment processor | Yes | No |
| transaction_id | Set | null |
| paysys | "Stripe" | "Manual" |
| payment_method_id | Required | Not used |
| Permission | Staff or client | Staff only |

### Use Cases

- Bank transfer received
- Cash payment
- Check payment
- Offline transaction
- Testing/development
- Payment reconciliation

### Idempotency

Fully idempotent:
- First call: 200 OK, invoice marked paid, side effects triggered
- Subsequent calls: 200 OK, no changes, no side effects

### Audit Trail

Manual payments should be documented externally. The API does not record:
- Who marked it paid
- External reference numbers
- Payment method details

Consider adding a note before marking paid if documentation is needed.
