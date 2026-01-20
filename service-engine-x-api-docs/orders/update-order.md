# Update Order

```
PUT /api/orders/{id}
```

---

## 1. Purpose

Update an existing order. Any parameters not provided are left unchanged (partial update semantics).

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with order management permissions.

---

## 3. Request Parameters

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | **Yes** | Order identifier. |

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
  "status": 2,
  "employees": ["uuid-1", "uuid-2"],
  "tags": ["completed", "reviewed"],
  "note": "Updated note",
  "service_id": "uuid",
  "form_data": { "field1": "updated_value" },
  "metadata": [{ "title": "key", "value": "value" }],
  "created_at": "2024-01-15T10:30:00+00:00",
  "date_started": "2024-01-15T10:30:00+00:00",
  "date_completed": "2024-01-20T16:00:00+00:00",
  "date_due": "2024-01-22T10:30:00+00:00"
}
```

### Body Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | integer | Status code (0–4). |
| `employees` | array[UUID] | Employee UUIDs. **Replaces** existing. |
| `tags` | array[string] | Tag names. **Replaces** existing. |
| `note` | string | Internal note. |
| `service_id` | UUID | Service reference. |
| `form_data` | object | Form field values. **Replaces** existing. |
| `metadata` | array | Array of `{title, value}`. **Replaces** existing. |
| `created_at` | datetime | Creation timestamp. |
| `date_started` | datetime | Work start date. |
| `date_completed` | datetime | Completion date. |
| `date_due` | datetime | Due date. |

### Validation Rules

| Field | Rule |
|-------|------|
| `status` | If provided, must be 0, 1, 2, 3, or 4 |
| `employees` | Each UUID must reference existing team member |
| `service_id` | If provided, must reference existing non-deleted service |
| `metadata` | Each item must have `title` and `value` strings |

---

## 4. Side Effects

| Effect | Description |
|--------|-------------|
| **Order updated** | Row updated in `orders` table |
| **Employees replaced** | If `employees` provided, all existing deleted, new inserted |
| **Tags replaced** | If `tags` provided, all existing deleted, new inserted |
| **Metadata replaced** | If `metadata` provided, entire object replaced |
| **Form data replaced** | If `form_data` provided, entire object replaced |
| **updated_at set** | Timestamp auto-updated |

---

## 5. Response Shape

### 200 OK

Returns `IndexOrder` representation.

```json
{
  "id": "uuid",
  "number": "ORD-ABC123",
  "created_at": "2024-01-15T10:30:00+00:00",
  "updated_at": "2024-01-20T16:05:00+00:00",
  "last_message_at": "2024-01-16T14:22:00+00:00",
  "date_started": "2024-01-15T10:30:00+00:00",
  "date_completed": "2024-01-20T16:00:00+00:00",
  "date_due": "2024-01-22T10:30:00+00:00",
  "client": { ... },
  "tags": ["completed", "reviewed"],
  "status": "Completed",
  "price": "299.00",
  "quantity": 1,
  "invoice_id": "uuid",
  "service": "Monthly SEO Package",
  "service_id": "uuid",
  "user_id": "uuid",
  "employees": [ ... ],
  "note": "Updated note",
  "form_data": { "field1": "updated_value" },
  "paysys": "Stripe"
}
```

---

## 6. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Cannot be changed |
| `number` | Read-only | Cannot be changed after creation |
| `user_id` | Read-only | Cannot be changed after creation |
| `status` | Read + Write | Integer stored (default `0` = Unpaid), string returned |
| `employees` | Write-only input, Read-only output | **Full replacement**; returned as joined array |
| `tags` | Write-only input, Read-only output | **Full replacement**; returned as string array |
| `note` | Read + Write | |
| `service_id` | Read + Write | Can be updated |
| `form_data` | Read + Write | **Full replacement** |
| `metadata` | Read + Write | **Full replacement**; array in, object out |
| `created_at` | Read + Write | Backdating allowed (operator use only) |
| `date_started` | Read + Write | |
| `date_completed` | Read + Write | |
| `date_due` | Read + Write | |
| `price` | Read-only | **Snapshot** — immutable |
| `quantity` | Read-only | Immutable after creation |
| `currency` | Read-only | **Snapshot** — immutable |
| `service` | Read-only | **Snapshot** — immutable |
| `invoice_id` | Read-only | Set via invoice creation |
| `paysys` | Read-only | Set via payment flow |
| `updated_at` | Read-only | Auto-set |
| `last_message_at` | Read-only | Auto-managed |

### Replacement Semantics (No Merge)

- `employees`: Full replacement. All existing assignments deleted, new ones inserted. Pass `[]` to clear.
- `tags`: Full replacement. All existing tags removed, new ones assigned. Pass `[]` to clear.
- `metadata`: Full replacement. Entire object replaced. Pass `[]` to clear.
- `form_data`: Full replacement. Entire object replaced. Pass `{}` to clear.

### Write-Time Ignored Fields

| Field | Behavior |
|-------|----------|
| `id` | Ignored, immutable |
| `number` | Ignored, immutable |
| `user_id` | Ignored, immutable |
| `price` | Ignored, snapshot immutable |
| `quantity` | Ignored, immutable |
| `currency` | Ignored, snapshot immutable |
| `service` | Ignored, snapshot immutable |
| `invoice_id` | Ignored, managed by invoice creation |
| `paysys` | Ignored, managed by payment flow |
| `updated_at` | Ignored, auto-set |
| `last_message_at` | Ignored, auto-managed |

---

## 7. Error Behavior

### 400 Bad Request

Validation failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "status": ["The status must be between 0 and 4."]
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

Order does not exist or is soft-deleted.

```json
{
  "error": "Not Found"
}
```

**Causes:**
- Invalid UUID format
- UUID does not match any order
- Order has been soft-deleted (`deleted_at IS NOT NULL`)

### 422 Unprocessable Entity

Referential integrity failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "service_id": ["The specified service does not exist."],
    "employees": ["Employee with ID uuid-x does not exist."]
  }
}
```

**Note:** 409 is not applicable to order updates.

---

## 8. Notes / Edge Cases

### Partial Update Semantics

Only fields included in the request body are updated. Omitted fields retain their current values.

```json
// Only updates status
{ "status": 2 }
```

### Immutable Fields

The following fields **cannot be changed** after order creation:
- `id`
- `number`
- `user_id` (client assignment)
- `price` (snapshot)
- `quantity`
- `currency` (snapshot)
- `service` (snapshot — the `service_name` field)

To change the client, create a new order.

### Service ID Updates

`service_id` can be updated, but this:
- Changes which service object is joined as `order_service`
- Does **not** update the snapshot fields (`price`, `service`, `currency`)

The original pricing remains unchanged.

### Status Transitions

No transition validation is enforced. Any status can be set to any other status:

| From | To | Allowed |
|------|-----|---------|
| Any | Any | Yes |

Business logic for status transitions should be enforced at application layer if needed.

### Soft-Deleted Orders

Attempting to update a soft-deleted order returns 404. To restore, direct database update is required.

### Employee Replacement

When `employees` is provided:
1. All existing `order_employees` rows deleted
2. New rows inserted for each UUID

To remove all employees:
```json
{ "employees": [] }
```

### Tag Replacement

When `tags` is provided:
1. All existing `order_tags` rows deleted
2. New tags linked (created if needed)

To remove all tags:
```json
{ "tags": [] }
```
