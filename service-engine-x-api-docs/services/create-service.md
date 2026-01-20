# Create Service

```
POST /api/services
```

---

## 1. Purpose

Create a new service. Services represent purchasable products or offerings.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with service management permissions.

---

## 3. Request Parameters

### Request Headers

| Header | Type | Required |
|--------|------|----------|
| `Authorization` | string | Yes |
| `Content-Type` | string | Yes (`application/json`) |
| `Accept` | string | Yes (`application/json`) |
| `X-Api-Version` | string | No |

### Request Body

```json
{
  "name": "Monthly SEO Package",
  "description": "Comprehensive SEO service including...",
  "recurring": 1,
  "currency": "USD",
  "price": 299.00,
  "f_price": 299.00,
  "f_period_l": 1,
  "f_period_t": "M",
  "r_price": 199.00,
  "r_period_l": 1,
  "r_period_t": "M",
  "recurring_action": 1,
  "deadline": 30,
  "public": true,
  "employees": ["uuid-1", "uuid-2"],
  "group_quantities": false,
  "multi_order": true,
  "request_orders": false,
  "max_active_requests": 5,
  "metadata": [
    { "title": "category", "value": "seo" }
  ],
  "folder_id": "uuid-or-null"
}
```

### Body Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | **Yes** | — | Service name. Max 255 characters. |
| `description` | string | No | `null` | Service description. |
| `recurring` | integer | **Yes** | — | 0 = one-time, 1 = recurring, 2 = trial/setup |
| `currency` | string | **Yes** | — | ISO 4217 currency code (e.g., "USD"). |
| `price` | number | No | `null` | Base price. |
| `f_price` | number | No | `null` | First period price. |
| `f_period_l` | integer | No | `null` | First period length. |
| `f_period_t` | string | No | `null` | First period type: `D`, `W`, `M`, `Y`. |
| `r_price` | number | No | `null` | Recurring period price. |
| `r_period_l` | integer | No | `null` | Recurring period length. |
| `r_period_t` | string | No | `null` | Recurring period type: `D`, `W`, `M`, `Y`. |
| `recurring_action` | integer | No | `null` | Action on subscription cycle end. |
| `deadline` | integer | No | `null` | Default deadline in days. |
| `public` | boolean | No | `true` | Visible to clients. |
| `employees` | array[UUID] | No | `[]` | Employee UUIDs to assign to this service. |
| `group_quantities` | boolean | No | `false` | Group quantities in cart. |
| `multi_order` | boolean | No | `true` | Allow multiple simultaneous orders. |
| `request_orders` | boolean | No | `false` | Enable request-based ordering. |
| `max_active_requests` | integer | No | `null` | Max concurrent active requests. |
| `metadata` | array | No | `{}` | Array of `{title, value}` objects. |
| `folder_id` | UUID | No | `null` | Service folder UUID. |

### Validation Rules

| Field | Rule |
|-------|------|
| `name` | Required, non-empty string, max 255 chars |
| `recurring` | Required, must be 0, 1, or 2 |
| `currency` | Required, valid ISO 4217 code |
| `f_period_t`, `r_period_t` | If provided, must be `D`, `W`, `M`, or `Y` |
| `employees` | Each UUID must reference an existing team member |
| `folder_id` | If provided, must reference an existing service folder |
| `metadata` | Each item must have `title` (string) and `value` (string) |

---

## 4. Side Effects

| Effect | Description |
|--------|-------------|
| **Service created** | New row inserted into `services` table |
| **Employees assigned** | Rows inserted into `service_employees` junction table |
| **Metadata transformed** | Array of `{title, value}` converted to JSONB object |

---

## 5. Response Shape

### 201 Created

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Monthly SEO Package",
  "description": "Comprehensive SEO service including...",
  "image": null,
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

---

## 6. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Generated UUID |
| `name` | Read + Write | Required on create |
| `description` | Read + Write | |
| `image` | Read-only | Managed via separate upload |
| `recurring` | Read + Write | Required on create |
| `price` | Read + Write | |
| `pretty_price` | Computed | Derived from `price` + `currency` |
| `currency` | Read + Write | Required on create |
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
| `sort_order` | Read-only | Defaults to 0 on create |
| `group_quantities` | Read + Write | |
| `employees` | Write-only | **Full replacement**, not returned |
| `folder_id` | Read + Write | |
| `metadata` | Read + Write | **Full replacement**; array in, object out |
| `braintree_plan_id` | Read + Write | |
| `hoth_product_key` | Read + Write | |
| `hoth_package_name` | Read + Write | |
| `provider_id` | Read + Write | |
| `provider_service_id` | Read + Write | |
| `created_at` | Read-only | Auto-generated |
| `updated_at` | Read-only | Auto-generated |

### Replacement Semantics (No Merge)

- `employees`: Full replacement. Existing assignments deleted, new ones inserted.
- `metadata`: Full replacement. Entire object replaced, not merged.

### Write-Time Ignored Fields

The following fields are **ignored** if provided in create request:

| Field | Behavior |
|-------|----------|
| `id` | Ignored, always generated |
| `pretty_price` | Ignored, always computed |
| `image` | Ignored, managed via separate upload |
| `sort_order` | Ignored on create, defaults to 0 |
| `created_at` | Ignored, auto-set |
| `updated_at` | Ignored, auto-set |

---

## 7. Error Behavior

### 400 Bad Request

Validation failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "name": ["The name field is required."],
    "recurring": ["The recurring field must be 0, 1, or 2."],
    "currency": ["The currency field is required."]
  }
}
```

**Common validation errors:**
- Missing required fields (`name`, `recurring`, `currency`)
- Invalid `recurring` value (must be 0, 1, or 2)
- Invalid period type (must be D, W, M, or Y)
- Invalid metadata format

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
    "folder_id": ["The specified folder does not exist."],
    "employees": ["Employee with ID uuid-x does not exist."]
  }
}
```

---

## 8. Notes / Edge Cases

### Metadata Transformation

Request format (array):
```json
{
  "metadata": [
    { "title": "category", "value": "seo" },
    { "title": "tier", "value": "premium" }
  ]
}
```

Stored and returned as (object):
```json
{
  "metadata": {
    "category": "seo",
    "tier": "premium"
  }
}
```

Duplicate titles: Later values overwrite earlier ones.

### Employee Assignment

The `employees` field accepts an array of user UUIDs (team members with dashboard access). These are stored in the `service_employees` junction table.

- Employees are **not returned** in the service response
- To retrieve assigned employees, query the service with includes (future feature) or query separately

### Pricing Fields

For **one-time services** (`recurring = 0`):
- Only `price` is meaningful
- `f_*` and `r_*` fields are ignored

For **recurring services** (`recurring = 1`):
- `f_*` defines the first billing period
- `r_*` defines subsequent billing periods
- `price` may be used as display price

For **trial/setup services** (`recurring = 2`):
- Represents a one-time fee before recurring subscription begins

### Period Type Codes

| Code | Meaning |
|------|---------|
| `D` | Day |
| `W` | Week |
| `M` | Month |
| `Y` | Year |

### Folder Assignment

If `folder_id` is provided:
- Must reference an existing `service_folders` record
- If folder does not exist, returns 422

If `folder_id` is null or omitted:
- Service is "unorganized" (no folder)

### Deferred Features

The following SPP fields are **not supported** in this version:
- `parent_services` — Addon system deferred
- `clear_variants` — Options system deferred
- `option_categories` — Options system deferred
- `option_variants` — Options system deferred
