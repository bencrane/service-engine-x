# Charge Invoice

```
POST /api/invoices/{id}/charge
```

---

## 1. Purpose

Charge an invoice using a stored payment method (e.g., Stripe PaymentMethod). Processes payment immediately and updates invoice status.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:**

| User Type | Can Charge |
|-----------|------------|
| Staff (invoice_management) | ✅ Yes (any invoice) |
| Client (invoice owner) | ✅ Yes (own invoices only) |
| Client (other's invoice) | ❌ No |
| Staff (invoice_access only) | ❌ No |

Clients can charge their own invoices using their saved payment methods.

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

```json
{
  "payment_method_id": "pm_1J5gXt2eZvKYlo2C3X2Z2Z2Z"
}
```

### Body Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `payment_method_id` | string | **Yes** | Stripe PaymentMethod ID or equivalent processor token. |

---

## 4. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `payment_method_id` | Write-only | Payment processor token |

### Fields Modified on Success

| Field | Before | After |
|-------|--------|-------|
| `status_id` | 1 (Unpaid) | 3 (Paid) |
| `status` | "Unpaid" | "Paid" |
| `date_paid` | null | Current timestamp |
| `transaction_id` | null | Processor transaction ID |
| `paysys` | null | "Stripe" |
| `ip_address` | — | Client IP address |

---

## 5. Side Effects

| Effect | Description |
|--------|-------------|
| **Payment processed** | Charge created via payment processor |
| **Invoice status updated** | Marked as Paid |
| **Transaction ID recorded** | Processor reference stored |
| **Client balance updated** | Spent amount recalculated |
| **Orders created** | If invoice items have service_id |
| **Subscription created** | If recurring invoice |
| **Custom billing date cleared** | If invoice had scheduled billing |

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
  "transaction_id": "pi_3N2abc123def456",
  "paysys": "Stripe",
  "ip_address": "192.168.1.1",
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

Validation or payment failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "payment_method_id": ["The payment method is invalid or expired."]
  }
}
```

**Common causes:**
- Missing `payment_method_id`
- Invalid payment method
- Expired card
- Insufficient funds
- Payment declined
- Invoice already paid

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

### Invoice Must Be Unpaid

Charging an already-paid invoice returns 400:

```json
{
  "message": "Invoice is already paid."
}
```

### Invoice Must Have Client

Invoices without an assigned client (`user_id`) cannot be charged:

```json
{
  "message": "Invoice has no client assigned."
}
```

### Payment Method Ownership

The payment method must belong to the invoice's client:
- Client's `stripe_id` must match payment method's customer
- Cross-client payment methods are rejected

### Order Creation

When payment succeeds:
1. For each item with `service_id`: an Order is created
2. Orders are linked to the invoice via `invoice_id`
3. Order status set based on service configuration

### Subscription Creation

For recurring invoices:
1. Subscription created for the client
2. Next invoice scheduled based on `r_period_l` and `r_period_t`
3. Subscription linked to original invoice

### Partial Payments

This endpoint does NOT support partial payments. The full `total` is charged. For partial payments, use manual payment workflow.

### Idempotency

Charging is NOT idempotent:
- First charge: 200 OK, payment processed
- Subsequent charges: 400 (already paid)

### Payment Processor Integration

This endpoint assumes Stripe integration. The `payment_method_id` format is:
- `pm_*` for PaymentMethods
- `card_*` for legacy cards (deprecated)

### Custom Billing Date

If the invoice had a custom billing date (scheduled for future), charging immediately:
- Clears the custom billing date
- Processes payment now
- Does not wait for scheduled date
