# Retrieve Invoice

```
GET /api/invoices/{id}
```

---

## 1. Purpose

Retrieve a single invoice by ID, including full client, items, and billing address details.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with invoice access.

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
| `Accept` | string | Yes (`application/json`) |

---

## 4. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Invoice UUID |
| `number` | Read-only | Human-readable invoice number |
| `number_prefix` | Read-only | Invoice number prefix |
| `client` | Read-only (joined) | Full client object |
| `items` | Read-only (joined) | Invoice line items |
| `billing_address` | Read-only | Address snapshot |
| `status` | Read-only | Status string |
| `status_id` | Read-only | Status integer |
| `created_at` | Read-only | Creation timestamp |
| `date_due` | Read-only | Due date |
| `date_paid` | Read-only | Payment date (null if unpaid) |
| `credit` | Read-only | Credit applied |
| `tax` | Read-only | Tax amount |
| `tax_name` | Read-only | Tax label |
| `tax_percent` | Read-only | Tax percentage |
| `currency` | Read-only | Currency code |
| `subtotal` | Computed | Pre-tax total |
| `total` | Computed | Final amount |
| `recurring` | Read-only | Recurring config or null |
| `coupon_id` | Read-only | Applied coupon |
| `transaction_id` | Read-only | Payment transaction ID |
| `paysys` | Read-only | Payment system |
| `note` | Read-only | Invoice note |
| `reason` | Read-only | Invoice reason |
| `ip_address` | Read-only | Client IP at creation |
| `view_link` | Computed | Public view URL |
| `download_link` | Computed | PDF download URL |
| `thanks_link` | Computed | Thank you page URL |

---

## 5. Side Effects

None. Read-only operation.

---

## 6. Response Shape

### 200 OK

```json
{
  "id": "uuid",
  "number": "INV-00042",
  "number_prefix": "INV-",
  "client": {
    "id": "uuid",
    "aff_id": 123,
    "aff_link": "https://example.com/r/ABC123",
    "created_at": "2023-01-01T00:00:00Z",
    "name": "John Doe",
    "name_f": "John",
    "name_l": "Doe",
    "email": "john@example.com",
    "company": "Acme Inc.",
    "tax_id": "123456789",
    "phone": "+1234567890",
    "address": {
      "line_1": "123 Main St",
      "line_2": null,
      "city": "New York",
      "state": "NY",
      "postcode": "10001",
      "country": "US"
    },
    "note": null,
    "balance": "0.00",
    "stripe_id": "cus_xxx",
    "custom_fields": {},
    "status": 1,
    "role_id": "uuid",
    "role": { ... },
    "managers": [ ... ],
    "spent": "1500.00"
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
      "discount2": "0.00",
      "total": "500.00",
      "service_id": "uuid",
      "order_id": "uuid",
      "options": {},
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
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
    "tax_id": "123456789",
    "company_name": "Acme Inc.",
    "company_vat": null
  },
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
  "reason": null,
  "note": "Thank you for your business",
  "ip_address": "192.168.1.1",
  "loc_confirm": false,
  "recurring": null,
  "coupon_id": null,
  "transaction_id": "pi_xxx",
  "paysys": "Stripe",
  "subtotal": "500.00",
  "total": "550.00",
  "employee_id": "uuid",
  "view_link": "https://example.com/invoices/INV-00042?key=xxx",
  "download_link": "https://example.com/invoices/INV-00042/download?key=xxx",
  "thanks_link": "https://example.com/thanks/INV-00042?key=xxx"
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

### 404 Not Found

Invoice does not exist or is soft-deleted.

```json
{
  "error": "Not Found"
}
```

**Causes:**
- Invalid UUID format
- Invoice ID does not exist
- Invoice is soft-deleted (`deleted_at IS NOT NULL`)

---

## 8. Notes / Edge Cases

### Soft-Deleted Invoices

Soft-deleted invoices return 404. There is no way to retrieve a soft-deleted invoice via API.

### Nested Objects

The response includes fully joined objects:
- `client`: Complete client with address, role, managers
- `items`: All line items with computed totals
- `billing_address`: Immutable snapshot from invoice creation

### Item Order ID

`items[].order_id` references the order created when the invoice was paid (if applicable). May be null for unpaid invoices or manual items.

### Payment Fields

When invoice is paid:
- `status_id`: 3 (Paid)
- `date_paid`: Payment timestamp
- `transaction_id`: Payment processor reference
- `paysys`: "Stripe", "Manual", etc.
