# List Clients

```
GET /api/clients
```

---

## 1. Purpose

Returns a paginated list of client users. Results are sorted by `created_at` descending by default.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator.

---

## 3. Request Parameters

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Items per page. Default: `20`. Max: `100`. |
| `page` | integer | No | Page number. Default: `1`. |
| `sort` | string | No | Sort field and direction. Format: `field:asc` or `field:desc`. Default: `created_at:desc`. |
| `expand[]` | array[string] | No | Related objects to include. Currently unused for clients. |
| `filters[{field}][{operator}]` | varies | No | Filter results by field values. |

### Supported Filter Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `$eq` | Equals | `filters[status][$eq]=1` |
| `$lt` | Less than | `filters[balance][$lt]=100` |
| `$gt` | Greater than | `filters[balance][$gt]=0` |
| `$in[]` | In array | `filters[id][$in][]=uuid1&filters[id][$in][]=uuid2` |

### Filterable Fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | |
| `email` | string | Exact match |
| `status` | integer | |
| `balance` | numeric | |
| `created_at` | datetime | |

### Request Headers

| Header | Type | Required |
|--------|------|----------|
| `Authorization` | string | Yes |
| `Accept` | string | Yes (`application/json`) |
| `X-Api-Version` | string | No |

---

## 4. Side Effects

None. Read-only operation.

---

## 5. Response Shape

### 200 OK

```json
{
  "data": [ ClientObject, ... ],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

### Top-Level Structure

| Field | Type | Description |
|-------|------|-------------|
| `data` | array[ClientObject] | Array of client objects. Empty array `[]` if no results. Never `null`. |
| `links` | PaginationLinks | Navigation URLs. Always present. |
| `meta` | PaginationMeta | Pagination metadata. Always present. |

### ClientObject

```json
{
  "id": "uuid",
  "name": "John Doe",
  "name_f": "John",
  "name_l": "Doe",
  "email": "client@example.com",
  "company": "Acme Inc.",
  "phone": "555-1234",
  "tax_id": "123456789",
  "address": AddressObject | null,
  "note": "VIP client",
  "balance": "100.00",
  "spent": "500.00",
  "optin": "Yes",
  "stripe_id": "cus_xxx",
  "custom_fields": {},
  "status": 1,
  "aff_id": 12345,
  "aff_link": "https://example.com/r/ABC123",
  "role_id": "uuid",
  "role": RoleObject,
  "created_at": "2024-01-15T10:30:00+00:00"
}
```

### AddressObject (Joined, Optional)

Returns `null` if client has no address. Otherwise:

```json
{
  "line_1": "123 Main St",
  "line_2": "Suite 100",
  "city": "New York",
  "state": "NY",
  "country": "US",
  "postcode": "10001",
  "name_f": "John",
  "name_l": "Doe",
  "tax_id": "123456789",
  "company_name": "Acme Inc.",
  "company_vat": "VAT123"
}
```

### RoleObject (Joined, Always Present)

```json
{
  "id": "uuid",
  "name": "Client",
  "dashboard_access": 0,
  "order_access": 1,
  "order_management": 0,
  "ticket_access": 1,
  "ticket_management": 0,
  "invoice_access": 1,
  "invoice_management": 0,
  "clients": 0,
  "services": 0,
  "coupons": 0,
  "forms": 0,
  "messaging": 1,
  "affiliates": 0,
  "settings_company": false,
  "settings_payments": false,
  "settings_team": false,
  "settings_modules": false,
  "settings_integrations": false,
  "settings_orders": false,
  "settings_tickets": false,
  "settings_accounts": false,
  "settings_messages": false,
  "settings_tags": false,
  "settings_sidebar": false,
  "settings_dashboard": false,
  "settings_templates": false,
  "settings_emails": false,
  "settings_language": false,
  "settings_logs": false,
  "created_at": "2024-01-01T00:00:00+00:00",
  "updated_at": "2024-01-01T00:00:00+00:00"
}
```

### PaginationLinks

```json
{
  "first": "https://example.com/api/clients?page=1",
  "last": "https://example.com/api/clients?page=5",
  "prev": null,
  "next": "https://example.com/api/clients?page=2"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `first` | string | URL to first page. Always present. |
| `last` | string | URL to last page. Always present. |
| `prev` | string \| null | URL to previous page. `null` on first page. |
| `next` | string \| null | URL to next page. `null` on last page. |

### PaginationMeta

```json
{
  "current_page": 1,
  "from": 1,
  "to": 20,
  "last_page": 5,
  "per_page": 20,
  "total": 100,
  "path": "https://example.com/api/clients",
  "links": [
    { "url": null, "label": "Previous", "active": false },
    { "url": "...", "label": "1", "active": true },
    { "url": "...", "label": "Next", "active": false }
  ]
}
```

---

## 6. Field Semantics

| Field | Semantics | Type | Description |
|-------|-----------|------|-------------|
| `id` | Read-only | UUID | Primary identifier. |
| `name` | Computed | string | `name_f + " " + name_l`. Never stored. |
| `name_f` | Read + Write | string | First name. |
| `name_l` | Read + Write | string | Last name. |
| `email` | Read + Write | string | Unique email address. |
| `company` | Read + Write | string \| null | Company name. |
| `phone` | Read + Write | string \| null | Phone number. |
| `tax_id` | Read + Write | string \| null | Tax identifier. |
| `address` | Read + Write | object \| null | Joined address record. See Address Handling. |
| `note` | Read + Write | string \| null | Internal note. |
| `balance` | Read-only | string (numeric) | Account credit balance. Modified via invoices. |
| `spent` | Computed | string \| null | Sum of paid invoice totals. Never stored. |
| `optin` | Read + Write | string \| null | Marketing opt-in status. |
| `stripe_id` | Read + Write | string \| null | Stripe customer ID. |
| `custom_fields` | Read + Write | object | Key-value custom fields. Default: `{}`. |
| `status` | Read + Write | integer | Account status. |
| `aff_id` | Read-only | integer | Auto-generated affiliate ID. |
| `aff_link` | Read-only | string | Auto-generated affiliate URL. |
| `role_id` | Read-only | UUID | Role FK. Clients always have client role. |
| `role` | Read-only (joined) | object | Embedded role object. Always present. |
| `created_at` | Read + Write | datetime | Creation timestamp. |

---

## 7. Error Behavior

### 401 Unauthorized

Missing or invalid Bearer token.

```json
{
  "error": "Unauthorized"
}
```

**Cause:** No `Authorization` header, malformed token, or expired token.

---

## 8. Notes / Edge Cases

- **Empty results:** Returns `"data": []`, not `null` or error.
- **Deleted clients:** Permanently removed from database. Will not appear in results.
- **Address:** Joined from `addresses` table. Returns `null` if no address linked.
- **Role:** Always joined and present. Never `null`.
- **Spent:** Computed at response time. May be `null` if no invoices paid.
- **Sort fields:** Only stored fields can be sorted. `name` (computed) cannot be sorted directly; use `name_f` or `name_l`.
- **Filter operators:** Invalid operators are ignored silently.
- **Pagination bounds:** `page` beyond `last_page` returns empty `data` array.
