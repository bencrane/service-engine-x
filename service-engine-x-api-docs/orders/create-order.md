# Create Order

```
POST /api/orders
```

---

## 1. Purpose

Create a new order for a client. Orders represent purchased services or work items.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with order management permissions.

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
  "user_id": "uuid",
  "service_id": "uuid",
  "service": "Custom Order Title",
  "status": 1,
  "employees": ["uuid-1", "uuid-2"],
  "tags": ["priority", "vip"],
  "note": "Internal note",
  "number": "ORD-CUSTOM-001",
  "metadata": [
    { "title": "source", "value": "api" }
  ],
  "created_at": "2024-01-15T10:30:00+00:00",
  "date_started": "2024-01-15T10:30:00+00:00",
  "date_completed": null,
  "date_due": "2024-01-22T10:30:00+00:00"
}
```

### Body Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `user_id` | UUID | **Yes** | — | Client UUID. Must exist. |
| `service_id` | UUID | Conditional | `null` | Service UUID. Required unless `service` is provided. |
| `service` | string | Conditional | — | Order title. Required unless `service_id` is provided. |
| `status` | integer | No | `0` | Status code (0–4). |
| `employees` | array[UUID] | No | `[]` | Employee UUIDs to assign. |
| `tags` | array[string] | No | `[]` | Tag names to attach. |
| `note` | string | No | `null` | Internal note. |
| `number` | string | No | Auto-generated | Custom order number. |
| `metadata` | array | No | `{}` | Array of `{title, value}` objects. |
| `created_at` | datetime | No | `NOW()` | Custom creation timestamp. |
| `date_started` | datetime | No | `null` | Work start date. |
| `date_completed` | datetime | No | `null` | Completion date. |
| `date_due` | datetime | No | `null` | Due date. |

### Validation Rules

| Field | Rule |
|-------|------|
| `user_id` | Required. Must reference existing client. |
| `service_id` | If provided, must reference existing non-deleted service. |
| `service` | Required if `service_id` not provided. |
| `status` | Must be 0, 1, 2, 3, or 4. |
| `employees` | Each UUID must reference existing team member. |
| `tags` | Tag names are matched/created as needed. |
| `number` | If provided, must be unique. |

---

## 4. Side Effects

| Effect | Description |
|--------|-------------|
| **Order created** | New row in `orders` table |
| **Snapshot captured** | `service_name`, `price`, `currency` copied from service (if `service_id` provided) |
| **Employees assigned** | Rows inserted into `order_employees` junction |
| **Tags assigned** | Rows inserted into `order_tags` junction |
| **Metadata transformed** | Array of `{title, value}` → JSONB object |
| **Number generated** | If not provided, auto-generated unique number |

---

## 5. Response Shape

### 201 Created

Returns `IndexOrder` representation.

```json
{
  "id": "uuid",
  "number": "ORD-ABC123",
  "created_at": "2024-01-15T10:30:00+00:00",
  "updated_at": "2024-01-15T10:30:00+00:00",
  "last_message_at": null,
  "date_started": "2024-01-15T10:30:00+00:00",
  "date_completed": null,
  "date_due": "2024-01-22T10:30:00+00:00",
  "client": {
    "id": "uuid",
    "name": "John Doe",
    "name_f": "John",
    "name_l": "Doe",
    "email": "john@example.com",
    ...
  },
  "tags": ["priority", "vip"],
  "status": "In Progress",
  "price": "299.00",
  "quantity": 1,
  "invoice_id": null,
  "service": "Monthly SEO Package",
  "service_id": "uuid",
  "user_id": "uuid",
  "employees": [
    {
      "id": "uuid",
      "name_f": "Jane",
      "name_l": "Smith",
      "role_id": "uuid"
    }
  ],
  "note": "Internal note",
  "form_data": {},
  "paysys": null
}
```

---

## 6. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Generated UUID |
| `number` | Read + Write | Auto-generated if not provided; must be unique |
| `user_id` | Write (required) | Client UUID |
| `service_id` | Write | Service reference (nullable) |
| `service` | Write | Order title; **snapshotted** as `service_name` |
| `status` | Write | Integer code; defaults to `0` (Unpaid); returned as mapped string |
| `employees` | Write-only input, Read-only output | **Full replacement**; returned as joined array |
| `tags` | Write-only input, Read-only output | **Full replacement**; returned as string array |
| `note` | Read + Write | Internal note |
| `metadata` | Read + Write | Array in, object out; **full replacement** |
| `created_at` | Read + Write | Backdating allowed (operator use only) |
| `date_started` | Write | |
| `date_completed` | Write | |
| `date_due` | Write | |
| `price` | Read-only | **Snapshot** from service at creation |
| `quantity` | Read-only | Defaults to 1 |
| `currency` | Read-only | **Snapshot** from service at creation |
| `invoice_id` | Read-only | Set later when invoice created |
| `paysys` | Read-only | Set via payment flow |
| `updated_at` | Read-only | Auto-set |
| `last_message_at` | Read-only | Set when messages added |
| `client` | Read-only (joined) | Embedded client object |

### Replacement Semantics (No Merge)

- `employees`: Full replacement. All UUIDs provided replace any default.
- `tags`: Full replacement. All tag names provided are assigned.
- `metadata`: Full replacement. Array converted to object.

### Write-Time Ignored Fields

| Field | Behavior |
|-------|----------|
| `id` | Ignored, always generated |
| `price` | Ignored, snapshotted from service |
| `quantity` | Ignored on create (defaults to 1) |
| `currency` | Ignored, snapshotted from service |
| `invoice_id` | Ignored, set via invoice creation |
| `paysys` | Ignored, set via payment flow |
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
    "user_id": ["The user_id field is required."],
    "service": ["Either service_id or service must be provided."]
  }
}
```

**Common validation errors:**
- Missing `user_id`
- Neither `service_id` nor `service` provided
- Invalid status value
- Duplicate `number`

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
    "user_id": ["The specified client does not exist."],
    "service_id": ["The specified service does not exist."],
    "employees": ["Employee with ID uuid-x does not exist."]
  }
}
```

**Note:** Create endpoints never return 404. Referential failures (missing client, service, employee) return 422, not 404. 409 is not applicable.

---

## 8. Notes / Edge Cases

### Service ID vs Service Name

Orders can be created in two modes:

1. **With `service_id`**: Links to existing service. Price, name, and currency are **snapshotted** from the service.
2. **With `service` only**: Creates a "custom" order with the provided title. Price defaults to 0, currency defaults to USD.

If both are provided, `service_id` takes precedence for snapshotting, but `service` is stored as `service_name`.

### Snapshot Behavior

When `service_id` is provided, the following are captured at creation:
- `service_name` ← `services.name`
- `price` ← `services.price`
- `currency` ← `services.currency`

These values **never update**, even if the service is modified or deleted later.

### Order Number Generation

If `number` is not provided:
- System generates a unique alphanumeric number
- Format: 8-character uppercase alphanumeric (e.g., "E4A269FC")
- Uniqueness is enforced at database level

### Tag Handling

Tags are provided as string names:
```json
{ "tags": ["priority", "vip"] }
```

- If a tag name exists in `tags` table, it's linked
- If a tag name doesn't exist, behavior depends on implementation (create or error)
- Tags are returned as string array in response

### Status Values

| Code | Meaning |
|------|---------|
| 0 | Unpaid |
| 1 | In Progress |
| 2 | Completed |
| 3 | Cancelled |
| 4 | On Hold |

**Default on create:** `0` (Unpaid). This is intentional — new orders start unpaid until payment is processed.

Status is stored as integer but returned as mapped string.

### Backdating (created_at)

Operators may provide a custom `created_at` timestamp to backdate orders (e.g., for data migration or historical corrections). This field is accepted on create but should be used judiciously.

### Metadata Transformation

Request format (array):
```json
{ "metadata": [{ "title": "key", "value": "val" }] }
```

Stored and returned as (object):
```json
{ "metadata": { "key": "val" } }
```
