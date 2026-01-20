# List Services

```
GET /api/services
```

---

## 1. Purpose

Retrieve a paginated list of all services. Services represent purchasable products or offerings. Results are sorted by creation date descending by default.

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
| `id` | Service UUID |
| `name` | Service name |
| `price` | Base price |
| `recurring` | Recurring type |
| `public` | Public visibility |
| `sort_order` | Sort order |
| `created_at` | Creation timestamp |

### Filtering

Filters use the pattern `filters[field][$operator]` or `filters[field][$operator][]` for array values.

| Operator | Meaning | Example |
|----------|---------|---------|
| `$eq` | Equals | `filters[public][$eq]=true` |
| `$lt` | Less than | `filters[price][$lt]=100` |
| `$gt` | Greater than | `filters[price][$gt]=0` |
| `$in` | In array | `filters[id][$in][]=uuid1&filters[id][$in][]=uuid2` |

**Filterable fields:** `id`, `name`, `recurring`, `public`, `price`, `currency`, `folder_id`, `created_at`

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
      "name": "Service name",
      "description": "Service description",
      "image": "https://example.com/image.png",
      "recurring": 1,
      "price": "99.00",
      "pretty_price": "$99.00",
      "currency": "USD",
      "f_price": "99.00",
      "f_period_l": 1,
      "f_period_t": "M",
      "r_price": "49.00",
      "r_period_l": 1,
      "r_period_t": "M",
      "recurring_action": 1,
      "multi_order": true,
      "request_orders": false,
      "max_active_requests": null,
      "deadline": 7,
      "public": true,
      "sort_order": 0,
      "group_quantities": false,
      "folder_id": "uuid-or-null",
      "metadata": {},
      "braintree_plan_id": null,
      "hoth_product_key": null,
      "hoth_package_name": null,
      "provider_id": null,
      "provider_service_id": null,
      "created_at": "2024-01-15T10:30:00+00:00",
      "updated_at": "2024-01-15T10:30:00+00:00"
    }
  ],
  "links": {
    "first": "https://example.com/api/services?page=1",
    "last": "https://example.com/api/services?page=3",
    "prev": null,
    "next": "https://example.com/api/services?page=2"
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "to": 20,
    "last_page": 3,
    "per_page": 20,
    "total": 43,
    "path": "https://example.com/api/services",
    "links": [
      { "url": null, "label": "Previous", "active": false },
      { "url": "https://example.com/api/services?page=1", "label": "1", "active": true },
      { "url": "https://example.com/api/services?page=2", "label": "Next", "active": false }
    ]
  }
}
```

### Response Structure

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `data` | array | No | Array of service objects |
| `links` | object | No | Pagination links |
| `links.first` | string | No | URL to first page |
| `links.last` | string | No | URL to last page |
| `links.prev` | string | Yes | URL to previous page, null if on first page |
| `links.next` | string | Yes | URL to next page, null if on last page |
| `meta` | object | No | Pagination metadata |
| `meta.current_page` | integer | No | Current page number |
| `meta.from` | integer | No | First item index on current page (1-based) |
| `meta.to` | integer | No | Last item index on current page |
| `meta.last_page` | integer | No | Total number of pages |
| `meta.per_page` | integer | No | Items per page |
| `meta.total` | integer | No | Total number of items |

---

## 6. Field Semantics

| Field | Semantics | Description |
|-------|-----------|-------------|
| `id` | Read-only | Service UUID, generated on create |
| `name` | Read + Write | Service name (required on create) |
| `description` | Read + Write | Service description |
| `image` | Read + Write | Image URL |
| `recurring` | Read + Write | 0 = one-time, 1 = recurring, 2 = trial/setup fee |
| `price` | Read + Write | Base price as decimal string |
| `pretty_price` | Computed | Formatted price with currency symbol |
| `currency` | Read + Write | ISO 4217 currency code |
| `f_price` | Read + Write | First period price (subscriptions) |
| `f_period_l` | Read + Write | First period length |
| `f_period_t` | Read + Write | First period type: D (day), W (week), M (month), Y (year) |
| `r_price` | Read + Write | Recurring period price |
| `r_period_l` | Read + Write | Recurring period length |
| `r_period_t` | Read + Write | Recurring period type |
| `recurring_action` | Read + Write | Action on subscription end (integer code) |
| `multi_order` | Read + Write | Allow multiple simultaneous orders |
| `request_orders` | Read + Write | Enable request-based ordering |
| `max_active_requests` | Read + Write | Max concurrent active requests |
| `deadline` | Read + Write | Default deadline in days |
| `public` | Read + Write | Visible to clients |
| `sort_order` | Read + Write | Display order (lower = first) |
| `group_quantities` | Read + Write | Group quantities in cart |
| `folder_id` | Read + Write | Service folder UUID |
| `metadata` | Read + Write | Custom key-value metadata (JSONB) |
| `braintree_plan_id` | Read + Write | Braintree subscription plan ID |
| `hoth_product_key` | Read + Write | HOTH integration key |
| `hoth_package_name` | Read + Write | HOTH package name |
| `provider_id` | Read + Write | External provider ID |
| `provider_service_id` | Read + Write | External service ID |
| `created_at` | Read-only | Creation timestamp |
| `updated_at` | Read-only | Last update timestamp |

---

## 7. Error Behavior

### 400 Bad Request

Invalid query parameters.

```json
{
  "message": "Invalid request parameters.",
  "errors": {
    "limit": ["The limit must be between 1 and 100."],
    "sort": ["Invalid sort field."]
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

- Soft-deleted services (`deleted_at IS NOT NULL`) are **excluded by default**
- There is **no `include_deleted` parameter** — soft-deleted services cannot be retrieved via this endpoint
- To access deleted services, direct database query is required

### Deferred Fields

The following fields from SPP are **not implemented** in this version:
- `option_categories` — Options system deferred
- `option_variants` — Options system deferred
- `addon_to` — Addon relationships deferred
- `media` — Media attachments deferred

### Empty Results

If no services exist or all are filtered out:
- `data` is an empty array `[]`
- `meta.total` is `0`
- `meta.from` and `meta.to` are `0`

### Pricing Fields

The `f_*` (first) and `r_*` (recurring) fields define subscription pricing:
- **First period**: Initial charge and duration
- **Recurring period**: Ongoing charge and cycle after first period

These fields are only meaningful when `recurring = 1`.

### Folder Filtering

Use `filters[folder_id][$eq]=uuid` to filter services by folder. Use `filters[folder_id][$eq]=null` to find unorganized services.
