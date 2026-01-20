# Retrieve Service

```
GET /api/services/{id}
```

---

## 1. Purpose

Retrieve a single service by ID. Returns the full service object.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator.

---

## 3. Request Parameters

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | **Yes** | Service identifier. |

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
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Monthly SEO Package",
  "description": "Comprehensive SEO service including...",
  "image": "https://example.com/image.png",
  "recurring": 1,
  "price": "299.00",
  "pretty_price": "$299.00",
  "currency": "USD",
  "f_price": "299.00",
  "f_period_l": 1,
  "f_period_t": "M",
  "r_price": "199.00",
  "r_period_l": 1,
  "r_period_t": "M",
  "recurring_action": 1,
  "multi_order": true,
  "request_orders": false,
  "max_active_requests": 5,
  "deadline": 30,
  "public": true,
  "sort_order": 0,
  "group_quantities": false,
  "folder_id": "uuid-or-null",
  "metadata": { "category": "seo" },
  "braintree_plan_id": null,
  "hoth_product_key": null,
  "hoth_package_name": null,
  "provider_id": null,
  "provider_service_id": null,
  "created_at": "2024-01-15T10:30:00+00:00",
  "updated_at": "2024-01-15T10:30:00+00:00"
}
```

### Response Fields

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | UUID | No | Service identifier |
| `name` | string | No | Service name |
| `description` | string | Yes | Service description |
| `image` | string | Yes | Image URL |
| `recurring` | integer | No | 0 = one-time, 1 = recurring, 2 = trial/setup |
| `price` | string | Yes | Base price as decimal string |
| `pretty_price` | string | No | Formatted price with currency symbol |
| `currency` | string | No | ISO 4217 currency code |
| `f_price` | string | Yes | First period price |
| `f_period_l` | integer | Yes | First period length |
| `f_period_t` | string | Yes | First period type (D/W/M/Y) |
| `r_price` | string | Yes | Recurring period price |
| `r_period_l` | integer | Yes | Recurring period length |
| `r_period_t` | string | Yes | Recurring period type (D/W/M/Y) |
| `recurring_action` | integer | Yes | Action on subscription cycle end |
| `multi_order` | boolean | No | Allow multiple simultaneous orders |
| `request_orders` | boolean | No | Enable request-based ordering |
| `max_active_requests` | integer | Yes | Max concurrent active requests |
| `deadline` | integer | Yes | Default deadline in days |
| `public` | boolean | No | Visible to clients |
| `sort_order` | integer | No | Display order |
| `group_quantities` | boolean | No | Group quantities in cart |
| `folder_id` | UUID | Yes | Service folder UUID |
| `metadata` | object | No | Custom key-value metadata |
| `braintree_plan_id` | string | Yes | Braintree subscription plan ID |
| `hoth_product_key` | string | Yes | HOTH integration key |
| `hoth_package_name` | string | Yes | HOTH package name |
| `provider_id` | integer | Yes | External provider ID |
| `provider_service_id` | integer | Yes | External service ID |
| `created_at` | datetime | No | Creation timestamp |
| `updated_at` | datetime | No | Last update timestamp |

---

## 6. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | |
| `name` | Read + Write | |
| `description` | Read + Write | |
| `image` | Read-only | Managed via separate upload |
| `recurring` | Read + Write | |
| `price` | Read + Write | |
| `pretty_price` | Computed | Derived from `price` + `currency` |
| `currency` | Read + Write | |
| `f_price` | Read + Write | |
| `f_period_l` | Read + Write | |
| `f_period_t` | Read + Write | |
| `r_price` | Read + Write | |
| `r_period_l` | Read + Write | |
| `r_period_t` | Read + Write | |
| `recurring_action` | Read + Write | |
| `multi_order` | Read + Write | |
| `request_orders` | Read + Write | |
| `max_active_requests` | Read + Write | |
| `deadline` | Read + Write | |
| `public` | Read + Write | |
| `sort_order` | Read + Write | |
| `group_quantities` | Read + Write | |
| `folder_id` | Read + Write | |
| `metadata` | Read + Write | |
| `braintree_plan_id` | Read + Write | |
| `hoth_product_key` | Read + Write | |
| `hoth_package_name` | Read + Write | |
| `provider_id` | Read + Write | |
| `provider_service_id` | Read + Write | |
| `created_at` | Read-only | |
| `updated_at` | Read-only | |

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

Service does not exist.

```json
{
  "error": "Not Found"
}
```

**Causes:**
- Invalid UUID format
- UUID does not match any service
- Service has been soft-deleted

---

## 8. Notes / Edge Cases

### Soft-Deleted Services

Services with `deleted_at` set are treated as deleted. Retrieve returns 404 for soft-deleted services.

### Pricing Display

The `pretty_price` field is computed at response time:
- Formats `price` with the appropriate currency symbol
- Uses standard locale formatting for the currency
- Example: `price: "299.00"`, `currency: "USD"` → `pretty_price: "$299.00"`

If `price` is null, `pretty_price` returns `"$0.00"` or equivalent.

### Metadata Format

Metadata is stored as JSONB and returned as an object:

```json
{
  "metadata": {
    "category": "seo",
    "tier": "premium"
  }
}
```

If no metadata exists, returns empty object `{}`.

### Deferred Fields

The following SPP response fields are **not implemented**:
- `option_categories`
- `option_variants`
- `addon_to`
- `media`
- `deleted_at` (internal, not exposed)

### Folder Reference

`folder_id` returns the UUID of the assigned service folder, or `null` if unorganized. The folder object itself is not embedded in the response.

### Employee Assignment

Assigned employees are **not included** in the retrieve response. To get employees for a service, query the `service_employees` junction table separately (or use includes when implemented).
