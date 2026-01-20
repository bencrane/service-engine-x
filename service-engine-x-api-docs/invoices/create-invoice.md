# Create Invoice

```
POST /api/invoices
```

---

## 1. Purpose

Create a new invoice for a client with one or more line items.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with invoice management permissions.

---

## 3. Request

### Request Headers

| Header | Type | Required |
|--------|------|----------|
| `Authorization` | string | Yes |
| `Content-Type` | string | Yes (`application/json`) |
| `Accept` | string | Yes (`application/json`) |

### Request Body

```json
{
  "user_id": "uuid",
  "items": [
    {
      "name": "Web Design",
      "description": "Homepage redesign",
      "quantity": 1,
      "amount": 500.00,
      "discount": 0.00,
      "service_id": "uuid",
      "options": {}
    }
  ],
  "status": 1,
  "tax": 10.00,
  "tax_type": 1,
  "recurring": false,
  "r_period_l": null,
  "r_period_t": null,
  "coupon_id": null,
  "note": "Thank you for your business"
}
```

### Body Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `user_id` | UUID | No* | — | Client ID. Required if `email` not provided. |
| `email` | string | No* | — | Client email. Creates client if not found. |
| `items` | array | **Yes** | — | Invoice line items (at least one required). |
| `status` | integer | No | `1` | Status ID (0=Draft, 1=Unpaid, etc.). |
| `tax` | number | No | `0` | Tax amount or percentage. |
| `tax_type` | integer | No | `0` | Tax calculation type. |
| `recurring` | object/null | No | `null` | Recurring configuration (see below). |
| `coupon_id` | UUID | No | `null` | Coupon to apply. |
| `note` | string | No | `null` | Invoice note. |
| `user_data` | object | No | `null` | Additional client data for creation. |

*Either `user_id` or `email` must be provided.

### Item Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | **Yes** | Item name. |
| `description` | string | No | Item description. |
| `quantity` | integer | **Yes** | Quantity (must be ≥ 1). |
| `amount` | number | **Yes** | Unit price. |
| `discount` | number | No | Discount amount. |
| `service_id` | UUID | No | Associated service. |
| `options` | object | No | Service options selected. |

### Status Values

| Value | Meaning |
|-------|---------|
| 0 | Draft |
| 1 | Unpaid |
| 3 | Paid |
| 4 | Refunded |
| 5 | Cancelled |
| 7 | Partially Paid |

### Tax Type Values

| Value | Meaning |
|-------|---------|
| 0 | No tax |
| 1 | Fixed amount |
| 2 | Percentage |
| 3–8 | Reserved |

---

## 4. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `user_id` | Write-only | Client reference |
| `email` | Write-only | Alternative to user_id |
| `items` | Write (required) | Full replacement |
| `status` | Write | Default 1 (Unpaid) |
| `tax` | Write | Amount or percentage |
| `tax_type` | Write | Calculation method |
| `recurring` | Write | Recurring config object or null |
| `coupon_id` | Write | Optional coupon |
| `note` | Write | Optional note |
| `user_data` | Write-only | Client creation data |

### Write-Time Ignored Fields

| Field | Behavior |
|-------|----------|
| `id` | Ignored, always generated |
| `number` | Ignored, auto-generated |
| `date_paid` | Ignored, set on payment |
| `transaction_id` | Ignored, set on payment |
| `paysys` | Ignored, set on payment |
| `subtotal` | Ignored, computed |
| `total` | Ignored, computed |
| `view_link` | Ignored, computed |

---

## 5. Side Effects

| Effect | Description |
|--------|-------------|
| **Invoice created** | New row in `invoices` table |
| **Items created** | Rows inserted into `invoice_items` |
| **Billing address snapshotted** | Client address copied to invoice |
| **Client created** | If `email` provided and client doesn't exist |

---

## 6. Response Shape

### 201 Created

Returns the full invoice object with nested client, items, and billing_address.

```json
{
  "id": "uuid",
  "number": "INV-00042",
  "number_prefix": "INV-",
  "client": { ... },
  "items": [ ... ],
  "billing_address": { ... },
  "status": "Unpaid",
  "status_id": 1,
  "created_at": "2024-01-15T10:00:00Z",
  "date_due": "2024-02-14T10:00:00Z",
  "date_paid": null,
  "credit": "0.00",
  "tax": "50.00",
  "tax_name": "Sales Tax",
  "tax_percent": "10.00",
  "currency": "USD",
  "subtotal": "500.00",
  "total": "550.00",
  "recurring": null,
  "coupon_id": null,
  "transaction_id": null,
  "paysys": null,
  "note": "Thank you for your business",
  "view_link": "https://...",
  "download_link": "https://...",
  "thanks_link": "https://..."
}
```

---

## 7. Error Behavior

### 400 Bad Request

Validation failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "items": ["The items field is required."],
    "items.0.name": ["The name field is required."]
  }
}
```

**Common validation errors:**
- Missing `items` array
- Missing `user_id` and `email`
- Invalid item fields (missing name, quantity, or amount)
- Invalid status value
- Invalid recurring configuration

### 401 Unauthorized

Missing or invalid Bearer token.

```json
{
  "error": "Unauthorized"
}
```

### 422 Unprocessable Entity

Referential integrity failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "user_id": ["The specified client does not exist."],
    "coupon_id": ["The specified coupon does not exist."]
  }
}
```

**Note:** Create never returns 404.

---

## 8. Notes / Edge Cases

### Client Resolution

1. If `user_id` provided: Must reference existing client
2. If `email` provided without `user_id`:
   - Existing client with email → use that client
   - No existing client → create new client using `user_data` if provided

### Billing Address Snapshot

At creation, the client's current address is copied to `billing_address`. This snapshot is immutable — changes to the client's address do not affect existing invoices.

### Items are Required

At least one item must be provided.

| Scenario | Result |
|----------|--------|
| `items` omitted | 400 — field required |
| `items: []` | 400 — at least one item required |
| `items: [valid]` | ✅ Invoice created |

### Computed Fields

The following are computed server-side and cannot be set:
- `number`: Auto-incremented invoice number
- `subtotal`: Sum of (item.amount × item.quantity - item.discount)
- `total`: subtotal + tax - credit
- `view_link`, `download_link`, `thanks_link`: Generated URLs

### Recurring Configuration

`recurring` is an **object** containing period configuration, or `null` to disable:

```json
// Enable recurring (monthly)
{
  "recurring": {
    "r_period_l": 1,
    "r_period_t": "M"
  }
}

// No recurring
{
  "recurring": null
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `r_period_l` | integer | Yes | Period length (1, 3, 12, etc.) |
| `r_period_t` | string | Yes | Period type: `M` (months), `W` (weeks), `D` (days) |

### Default Due Date

If not specified, `date_due` defaults to 14 days from creation.
