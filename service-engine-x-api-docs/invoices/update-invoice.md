# Update Invoice

```
PUT /api/invoices/{id}
```

---

## 1. Purpose

Update an existing invoice. All item changes use full replacement semantics.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with invoice management permissions.

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

All fields are optional. Only provided fields are updated.

```json
{
  "user_id": "uuid",
  "items": [
    {
      "id": "uuid",
      "name": "Web Design - Updated",
      "description": "Homepage redesign with revisions",
      "quantity": 1,
      "amount": 600.00,
      "discount": 0.00,
      "service_id": "uuid"
    }
  ],
  "status": 1,
  "tax": 12.00,
  "tax_type": 2,
  "recurring": true,
  "r_period_l": 1,
  "r_period_t": "M",
  "coupon_id": "uuid",
  "note": "Updated note"
}
```

### Body Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | UUID | No | Change invoice client. |
| `email` | string | No | Alternative to user_id. |
| `items` | array | **Yes** | **Full replacement** of all items. |
| `status` | integer | No | Status ID. |
| `tax` | number | No | Tax amount or percentage. |
| `tax_type` | integer | No | Tax calculation type. |
| `recurring` | boolean | No | Recurring flag. |
| `r_period_l` | integer | No | Recurring period length. |
| `r_period_t` | string | No | Recurring period type. |
| `coupon_id` | UUID | No | Coupon to apply. |
| `note` | string | No | Invoice note. |

### Item Fields (Full Replacement)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | No | Existing item ID to update. Omit for new items. |
| `name` | string | **Yes** | Item name. |
| `description` | string | No | Item description. |
| `quantity` | integer | **Yes** | Quantity. |
| `amount` | number | **Yes** | Unit price. |
| `discount` | number | No | Discount amount. |
| `service_id` | UUID | No | Associated service. |
| `options` | object | No | Service options. |

---

## 4. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `user_id` | Write | Change client |
| `email` | Write-only | Alternative client lookup |
| `items` | Write (required) | **Full replacement** (see below) |
| `status` | Write | Status change (restricted transitions) |
| `tax` | Write | Tax configuration |
| `tax_type` | Write | Tax calculation method |
| `recurring` | Write | Recurring config object or null |
| `coupon_id` | Write | Coupon assignment |
| `note` | Write | Note text |

### Items: Full Replacement (No Merge)

`items` uses **full replacement** semantics:

| Behavior | Description |
|----------|-------------|
| All existing items deleted | Every `invoice_items` row for this invoice is removed |
| All request items created | Each item in the request array becomes a new row |
| Preserve with `id` | Include existing item's `id` to logically "keep" it (still re-created) |
| New items | Omit `id` to create fresh items |
| **Empty array rejected** | `items: []` returns 400 — at least one item required |
| Omitting `items` rejected | Field is required for update |

**Example — Keeping one item, adding another:**
```json
{
  "items": [
    { "id": "existing-uuid", "name": "Keep This", "quantity": 1, "amount": 100 },
    { "name": "New Item", "quantity": 2, "amount": 50 }
  ]
}
```

### Status Transitions

Not all status changes are valid:

| From | Allowed To |
|------|------------|
| Draft (0) | Unpaid (1), Cancelled (5) |
| Unpaid (1) | Draft (0), Cancelled (5) |
| Paid (3) | Refunded (4) |
| Refunded (4) | — (terminal) |
| Cancelled (5) | Unpaid (1), Draft (0) |
| Partially Paid (7) | Paid (3), Cancelled (5), Refunded (4) |

**Invalid transitions return 400:**
```json
{
  "message": "The given data was invalid.",
  "errors": {
    "status": ["Cannot transition from Paid to Draft."]
  }
}
```

### Recurring Configuration

`recurring` is an **object or null**, not a boolean:

```json
// Enable recurring
{
  "recurring": {
    "r_period_l": 1,
    "r_period_t": "M"
  }
}

// Disable recurring
{
  "recurring": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| `r_period_l` | integer | Period length (e.g., 1, 3, 12) |
| `r_period_t` | string | Period type: `M` (months), `W` (weeks), `D` (days) |

### Write-Time Ignored Fields

| Field | Behavior |
|-------|----------|
| `id` | Immutable |
| `number` | Immutable |
| `billing_address` | Immutable (snapshot) |
| `date_paid` | Managed by payment endpoints |
| `transaction_id` | Managed by payment endpoints |
| `paysys` | Managed by payment endpoints |
| `subtotal` | Computed |
| `total` | Computed |

---

## 5. Side Effects

| Effect | Description |
|--------|-------------|
| **Invoice updated** | Row updated in `invoices` table |
| **Items replaced** | All `invoice_items` deleted and re-created |
| **Billing address unchanged** | Snapshot is immutable |
| **Totals recomputed** | `subtotal`, `total` recalculated |

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
  "status": "Unpaid",
  "status_id": 1,
  "created_at": "2024-01-15T10:00:00Z",
  "date_due": "2024-02-14T10:00:00Z",
  "date_paid": null,
  "tax": "72.00",
  "subtotal": "600.00",
  "total": "672.00",
  "recurring": {
    "r_period_l": 1,
    "r_period_t": "M"
  },
  "note": "Updated note",
  ...
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
    "status": ["The selected status is invalid."]
  }
}
```

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

---

## 8. Notes / Edge Cases

### Items Are Required

Unlike other update endpoints, `items` is required for invoice updates. The items array completely replaces existing items.

### Preserving Existing Items

To keep an existing item, include it with its `id`:

```json
{
  "items": [
    { "id": "existing-uuid", "name": "Keep This", "quantity": 1, "amount": 100 },
    { "name": "New Item", "quantity": 2, "amount": 50 }
  ]
}
```

### Billing Address is Immutable

The `billing_address` snapshot cannot be changed after invoice creation. To bill to a different address, create a new invoice.

### Changing Client

If `user_id` is changed:
- Invoice is reassigned to new client
- Billing address snapshot remains unchanged
- New client's current address is NOT copied

### Paid Invoice Updates

Updating a paid invoice (`status_id: 3`) is allowed but:
- Cannot change `status` to unpaid values
- `date_paid`, `transaction_id`, `paysys` remain unchanged

### Soft-Deleted Invoice

Attempting to update a soft-deleted invoice returns 404.
