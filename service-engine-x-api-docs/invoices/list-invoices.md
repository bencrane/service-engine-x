# List Invoices

```
GET /api/invoices
```

---

## 1. Purpose

Retrieve a paginated list of invoices, sorted by creation date descending. Supports filtering by client, status, and other fields.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with invoice access.

---

## 3. Request

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | `20` | Items per page. Range: 1–100. |
| `page` | integer | No | `1` | Page number. Must be ≥ 1. |
| `sort` | string | No | `id:desc` | Sort field and direction (e.g., `created_at:asc`). |
| `filters[user_id][$eq]` | UUID | No | — | Filter by client ID. |
| `filters[status][$eq]` | integer | No | — | Filter by status ID. |
| `filters[status][$in][]` | integer[] | No | — | Filter by multiple statuses. |

### Supported Filter Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `$eq` | Equals | `filters[status][$eq]=1` |
| `$lt` | Less than | `filters[total][$lt]=100` |
| `$gt` | Greater than | `filters[total][$gt]=50` |
| `$in` | In array | `filters[status][$in][]=1&filters[status][$in][]=3` |

### Request Headers

| Header | Type | Required |
|--------|------|----------|
| `Authorization` | string | Yes |
| `Accept` | string | Yes (`application/json`) |

---

## 4. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Invoice UUID |
| `number` | Read-only | Human-readable invoice number |
| `number_prefix` | Read-only | Invoice number prefix (e.g., "INV-") |
| `client` | Read-only (joined) | Full client object with address, role, managers |
| `items` | Read-only (joined) | Array of invoice line items |
| `billing_address` | Read-only | Snapshot of billing address at invoice creation |
| `status` | Read-only | Status string (mapped from status_id) |
| `status_id` | Read + Write | Status integer |
| `created_at` | Read-only | Invoice creation timestamp |
| `date_due` | Read-only | Payment due date |
| `date_paid` | Read-only | Payment date (null if unpaid) |
| `credit` | Read-only | Credit applied |
| `tax` | Read + Write | Tax amount |
| `tax_name` | Read-only | Tax label |
| `tax_percent` | Read-only | Tax percentage |
| `currency` | Read-only | Currency code (e.g., "USD") |
| `subtotal` | Computed | Sum of item amounts before tax |
| `total` | Computed | Final amount after tax and discounts |
| `recurring` | Read + Write | Recurring config object or null |
| `coupon_id` | Read + Write | Applied coupon (nullable) |
| `transaction_id` | Read-only | Payment processor transaction ID |
| `paysys` | Read-only | Payment system used (e.g., "Stripe", "Manual") |
| `view_link` | Computed | Public invoice view URL |
| `download_link` | Computed | PDF download URL |
| `thanks_link` | Computed | Post-payment thank you URL |

### Status Mapping

| status_id | status |
|-----------|--------|
| 0 | Draft |
| 1 | Unpaid |
| 3 | Paid |
| 4 | Refunded |
| 5 | Cancelled |
| 7 | Partially Paid |

---

## 5. Side Effects

None. Read-only operation.

---

## 6. Response Shape

### 200 OK

```json
{
  "data": [
    {
      "id": "uuid",
      "number": "INV-00001",
      "number_prefix": "INV-",
      "client": {
        "id": "uuid",
        "name": "John Doe",
        "name_f": "John",
        "name_l": "Doe",
        "email": "john@example.com",
        "company": "Acme Inc.",
        "address": { ... },
        "role": { ... },
        "managers": [ ... ]
      },
      "items": [
        {
          "id": "uuid",
          "invoice_id": "uuid",
          "name": "Web Design",
          "description": "Homepage redesign",
          "quantity": 1,
          "amount": "500.00",
          "discount": "0.00",
          "total": "500.00",
          "service_id": "uuid",
          "order_id": "uuid",
          "options": {}
        }
      ],
      "billing_address": {
        "line_1": "123 Main St",
        "line_2": null,
        "city": "New York",
        "state": "NY",
        "postcode": "10001",
        "country": "US",
        "name_f": "John",
        "name_l": "Doe",
        "company_name": "Acme Inc.",
        "company_vat": null,
        "tax_id": null
      },
      "status": "Unpaid",
      "status_id": 1,
      "created_at": "2024-01-15T10:00:00Z",
      "date_due": "2024-02-15T10:00:00Z",
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
      "employee_id": "uuid",
      "note": null,
      "view_link": "https://...",
      "download_link": "https://...",
      "thanks_link": "https://..."
    }
  ],
  "links": {
    "first": "...",
    "last": "...",
    "prev": null,
    "next": "..."
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "to": 20,
    "last_page": 5,
    "per_page": 20,
    "total": 100,
    "path": "..."
  }
}
```

---

## 7. Error Behavior

### 401 Unauthorized

Missing or invalid Bearer token.

```json
{
  "error": "Unauthorized"
}
```

**Note:** 400 and 404 are not applicable to list endpoints.

---

## 8. Notes / Edge Cases

### Soft-Deleted Invoices

Soft-deleted invoices (`deleted_at IS NOT NULL`) are excluded from results by default. There is no `include_deleted` parameter — soft-deleted invoices are not retrievable via API.

### Nested Objects

- `client`: Full client object including address, role, and managers
- `items`: All invoice line items with computed totals
- `billing_address`: Snapshot captured at invoice creation (not live from client)

### Empty Results

If no invoices match filters:
- `data` is empty array `[]`
- `meta.total` is `0`
- Response is 200 OK

### Recurring Invoices

`recurring` field contains period configuration when set:

```json
{
  "r_period_l": 1,
  "r_period_t": "M"
}
```

Where `r_period_t` is: `M` (monthly), `W` (weekly), `D` (daily).
