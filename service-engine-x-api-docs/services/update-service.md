# Update Service

```
PUT /api/services/{id}
```

---

## 1. Purpose

Update an existing service. Any parameters not provided are left unchanged (partial update semantics).

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with service management permissions.

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
| `Content-Type` | string | Yes (`application/json`) |
| `Accept` | string | Yes (`application/json`) |
| `X-Api-Version` | string | No |

### Request Body

All fields are optional. Only provided fields are updated.

```json
{
  "name": "Updated Service Name",
  "description": "Updated description...",
  "recurring": 1,
  "currency": "USD",
  "price": 349.00,
  "f_price": 349.00,
  "f_period_l": 1,
  "f_period_t": "M",
  "r_price": 249.00,
  "r_period_l": 1,
  "r_period_t": "M",
  "recurring_action": 1,
  "deadline": 30,
  "public": true,
  "employees": ["uuid-1", "uuid-2"],
  "group_quantities": false,
  "multi_order": true,
  "request_orders": false,
  "max_active_requests": 10,
  "metadata": [
    { "title": "category", "value": "seo" }
  ],
  "folder_id": "uuid-or-null",
  "sort_order": 5
}
```

### Body Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Service name. Max 255 characters. |
| `description` | string | Service description. |
| `recurring` | integer | 0 = one-time, 1 = recurring, 2 = trial/setup |
| `currency` | string | ISO 4217 currency code. |
| `price` | number | Base price. |
| `f_price` | number | First period price. |
| `f_period_l` | integer | First period length. |
| `f_period_t` | string | First period type: `D`, `W`, `M`, `Y`. |
| `r_price` | number | Recurring period price. |
| `r_period_l` | integer | Recurring period length. |
| `r_period_t` | string | Recurring period type: `D`, `W`, `M`, `Y`. |
| `recurring_action` | integer | Action on subscription cycle end. |
| `deadline` | integer | Default deadline in days. |
| `public` | boolean | Visible to clients. |
| `employees` | array[UUID] | Employee UUIDs. **Replaces** existing assignments. |
| `group_quantities` | boolean | Group quantities in cart. |
| `multi_order` | boolean | Allow multiple simultaneous orders. |
| `request_orders` | boolean | Enable request-based ordering. |
| `max_active_requests` | integer | Max concurrent active requests. |
| `metadata` | array | Array of `{title, value}` objects. **Replaces** existing metadata. |
| `folder_id` | UUID | Service folder UUID. Set to `null` to remove from folder. |
| `sort_order` | integer | Display order. |
| `braintree_plan_id` | string | Braintree subscription plan ID. |
| `hoth_product_key` | string | HOTH integration key. |
| `hoth_package_name` | string | HOTH package name. |
| `provider_id` | integer | External provider ID. |
| `provider_service_id` | integer | External service ID. |

### Validation Rules

| Field | Rule |
|-------|------|
| `name` | If provided, must be non-empty string, max 255 chars |
| `recurring` | If provided, must be 0, 1, or 2 |
| `currency` | If provided, must be valid ISO 4217 code |
| `f_period_t`, `r_period_t` | If provided, must be `D`, `W`, `M`, or `Y` |
| `employees` | Each UUID must reference an existing team member |
| `folder_id` | If provided (and not null), must reference existing folder |
| `metadata` | Each item must have `title` (string) and `value` (string) |

---

## 4. Side Effects

| Effect | Description |
|--------|-------------|
| **Service updated** | Row updated in `services` table |
| **Employees replaced** | If `employees` provided, all existing assignments deleted and replaced |
| **Metadata replaced** | If `metadata` provided, entire metadata object replaced |
| **updated_at set** | Timestamp updated automatically |

---

## 5. Response Shape

### 200 OK

Returns the full updated service object.

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Service Name",
  "description": "Updated description...",
  "image": "https://example.com/image.png",
  "recurring": 1,
  "price": "349.00",
  "pretty_price": "$349.00",
  "currency": "USD",
  "f_price": "349.00",
  "f_period_l": 1,
  "f_period_t": "M",
  "r_price": "249.00",
  "r_period_l": 1,
  "r_period_t": "M",
  "recurring_action": 1,
  "multi_order": true,
  "request_orders": false,
  "max_active_requests": 10,
  "deadline": 30,
  "public": true,
  "sort_order": 5,
  "group_quantities": false,
  "folder_id": "uuid-or-null",
  "metadata": { "category": "seo" },
  "braintree_plan_id": null,
  "hoth_product_key": null,
  "hoth_package_name": null,
  "provider_id": null,
  "provider_service_id": null,
  "created_at": "2024-01-15T10:30:00+00:00",
  "updated_at": "2024-01-20T14:45:00+00:00"
}
```

---

## 6. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Cannot be changed |
| `name` | Read + Write | |
| `description` | Read + Write | |
| `image` | Read-only | Managed via separate upload |
| `recurring` | Read + Write | |
| `price` | Read + Write | |
| `pretty_price` | Computed | |
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
| `employees` | Write-only | Replaces all assignments |
| `folder_id` | Read + Write | Set to `null` to unassign |
| `metadata` | Read + Write (replace) | Replaces entire object |
| `braintree_plan_id` | Read + Write | |
| `hoth_product_key` | Read + Write | |
| `hoth_package_name` | Read + Write | |
| `provider_id` | Read + Write | |
| `provider_service_id` | Read + Write | |
| `created_at` | Read-only | Cannot be changed |
| `updated_at` | Read-only | Auto-updated |

### Write-Time Ignored Fields

The following fields are **ignored** if provided:

| Field | Behavior |
|-------|----------|
| `id` | Ignored, cannot change primary key |
| `pretty_price` | Ignored, always computed |
| `image` | Ignored, managed via separate upload |
| `created_at` | Ignored, immutable |
| `updated_at` | Ignored, auto-set |

---

## 7. Error Behavior

### 400 Bad Request

Validation failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "recurring": ["The recurring field must be 0, 1, or 2."],
    "f_period_t": ["The period type must be D, W, M, or Y."]
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

### Partial Update Semantics

Only fields included in the request body are updated. Omitted fields retain their current values.

```json
// Only updates price
{ "price": 399.00 }
```

### Employee Replacement

When `employees` is provided, the operation is a **full replacement**:

1. All existing `service_employees` rows for this service are deleted
2. New rows are inserted for each UUID in the array

To clear all employees:
```json
{ "employees": [] }
```

To leave employees unchanged, omit the field entirely.

### Metadata Replacement

When `metadata` is provided, the entire metadata object is **replaced**:

```json
// Replaces all metadata
{ "metadata": [{ "title": "new_key", "value": "new_value" }] }
```

To clear metadata:
```json
{ "metadata": [] }
```

To leave metadata unchanged, omit the field.

### Folder Assignment

- Set `folder_id` to a valid UUID to move service to that folder
- Set `folder_id` to `null` to remove from any folder (unorganized)
- Omit `folder_id` to leave folder assignment unchanged

### Soft-Deleted Services

Attempting to update a soft-deleted service returns 404. To restore a soft-deleted service, use the dedicated restore endpoint (if implemented).

### Impact on Existing Orders

Updating a service does **not** affect existing orders. Orders store a snapshot of service data at order creation time.

### Deferred Features

The following SPP fields are **not supported**:
- `parent_services`
- `clear_variants`
