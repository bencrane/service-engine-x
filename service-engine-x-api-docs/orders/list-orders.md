# List Orders

```
GET /api/orders
```

---

## 1. Purpose

Retrieve a paginated list of orders. Returns a simplified `IndexOrder` representation (not the full order object). For complete order details including messages, invoice, and subscription, use the Retrieve endpoint.

Orders are sorted by creation date descending by default.

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

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | `20` | Items per page. Range: 1–100. |
| `page` | integer | No | `1` | Page number. Must be ≥ 1. |
| `sort` | string | No | `created_at:desc` | Sort field and direction. Format: `field:asc` or `field:desc`. |
| `filters[field][$op]` | varies | No | — | Filter by field using operator. See Filtering below. |

### Sortable Fields

| Field | Description |
|-------|-------------|
| `id` | Order UUID |
| `number` | Order number |
| `status` | Status code |
| `price` | Order price |
| `quantity` | Quantity |
| `user_id` | Client UUID |
| `service_id` | Service UUID |
| `created_at` | Creation timestamp |
| `date_due` | Due date |

### Filtering

Filters use the pattern `filters[field][$operator]` or `filters[field][$operator][]` for array values.

| Operator | Meaning | Example |
|----------|---------|---------|
| `$eq` | Equals | `filters[status][$eq]=1` |
| `$lt` | Less than | `filters[price][$lt]=500` |
| `$gt` | Greater than | `filters[created_at][$gt]=2024-01-01` |
| `$in` | In array | `filters[user_id][$in][]=uuid1&filters[user_id][$in][]=uuid2` |

**Filterable fields:** `id`, `number`, `status`, `user_id`, `service_id`, `price`, `invoice_id`, `created_at`, `date_due`

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
  "data": [
    {
      "id": "uuid",
      "number": "ORD-ABC123",
      "created_at": "2024-01-15T10:30:00+00:00",
      "updated_at": "2024-01-15T10:30:00+00:00",
      "last_message_at": null,
      "date_started": null,
      "date_completed": null,
      "date_due": "2024-01-22T10:30:00+00:00",
      "client": {
        "id": "uuid",
        "name": "John Doe",
        "name_f": "John",
        "name_l": "Doe",
        "email": "john@example.com",
        "company": "Acme Inc.",
        "phone": "123456789",
        "address": { ... },
        "role": { ... }
      },
      "tags": ["priority", "vip"],
      "status": "In Progress",
      "price": "299.00",
      "quantity": 1,
      "invoice_id": "uuid-or-null",
      "service": "Monthly SEO Package",
      "service_id": "uuid-or-null",
      "user_id": "uuid",
      "employees": [
        {
          "id": "uuid",
          "name_f": "Jane",
          "name_l": "Smith",
          "role_id": "uuid"
        }
      ],
      "note": "Client note",
      "form_data": {},
      "paysys": "Stripe"
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
    "last_page": 3,
    "per_page": 20,
    "total": 43,
    "path": "...",
    "links": [...]
  }
}
```

### Embedded Objects

| Object | Included | Notes |
|--------|----------|-------|
| `client` | Always | Full client object with address, role |
| `employees` | Always | Array of assigned employees |
| `tags` | Always | Array of tag names (strings) |

---

## 6. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Order UUID |
| `number` | Read + Write | Unique order number |
| `created_at` | Read + Write | Can be set on create |
| `updated_at` | Read-only | Auto-updated |
| `last_message_at` | Read-only | Set when messages added |
| `date_started` | Read + Write | Work start date |
| `date_completed` | Read + Write | Completion date |
| `date_due` | Read + Write | Due date |
| `client` | Read-only (joined) | Embedded client object |
| `tags` | Write-only input, Read-only output | **Full replacement** on write; returned as string array |
| `status` | Read + Write | Integer stored (default `0` = Unpaid), string returned |
| `price` | Read-only | **Snapshot** — captured at order creation |
| `quantity` | Read + Write | Order quantity |
| `invoice_id` | Read-only | Set when invoice created |
| `service` | Read-only | **Snapshot** — `service_name` at creation |
| `service_id` | Read + Write | Reference to service (nullable) |
| `user_id` | Read + Write | Required; client UUID |
| `employees` | Write-only input, Read-only output | **Full replacement** on write; returned as joined array |
| `note` | Read + Write | Internal note |
| `form_data` | Read + Write | Form field values (JSONB) |
| `paysys` | Read-only | Payment system used |

### Status Mapping

| Code | Display Value |
|------|---------------|
| 0 | Unpaid |
| 1 | In Progress |
| 2 | Completed |
| 3 | Cancelled |
| 4 | On Hold |

---

## 7. Error Behavior

### 400 Bad Request

Invalid query parameters.

```json
{
  "message": "Invalid request parameters.",
  "errors": {
    "limit": ["The limit must be between 1 and 100."]
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

**Note:** 404 and 409 are not applicable to list endpoints.

---

## 8. Notes / Edge Cases

### Soft-Delete Visibility

- Soft-deleted orders (`deleted_at IS NOT NULL`) are **excluded by default**
- There is **no `include_deleted` parameter** — soft-deleted orders cannot be retrieved via this endpoint
- To access deleted orders, direct database query is required

### IndexOrder vs Full Order

This endpoint returns `IndexOrder`, a simplified representation:
- Does **not** include: `subscription`, `invoice`, `order_service`, `messages`, `ratings`, `addons`, `metadata`, `currency`, `options`
- Use `GET /api/orders/{id}` for full order details

### Snapshot Fields

The following fields are **captured at order creation** and do not update:
- `price` — Price at time of order
- `service` — Service name at time of order (stored as `service_name`)
- `currency` — Currency at time of order

Even if the service is updated or deleted, these values remain unchanged.

### Client Embedding

The `client` object is fully embedded with:
- Personal details (name, email, phone, company)
- Address object
- Role object

This is a live reference, not a snapshot. Client changes reflect immediately.

### Empty Results

If no orders exist or all are filtered out:
- `data` is empty array `[]`
- `meta.total` is `0`
