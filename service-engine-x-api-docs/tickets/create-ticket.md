# Create Ticket

```
POST /api/tickets
```

---

## 1. Purpose

Create a new ticket for a client. Tickets can optionally be linked to an order.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated user with `ticket_management` permission.

---

## 3. Request

### Path Parameters

None.

### Query Parameters

None.

### Request Body

```json
{
  "user_id": "client-uuid",
  "subject": "Ticket subject",
  "status": 1,
  "order_id": "order-uuid-or-null",
  "employees": ["employee-uuid-1", "employee-uuid-2"],
  "tags": ["tag1", "tag2"],
  "note": "Internal note",
  "metadata": { "key": "value" }
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `user_id` | uuid | **Yes** | — | Client UUID. Must exist. |
| `subject` | string | **Yes** | — | Ticket subject. |
| `status` | integer | No | `1` (Open) | Ticket status. |
| `order_id` | uuid | No | `null` | Optional order reference. Must exist if provided. |
| `employees` | array[uuid] | No | `[]` | Employee UUIDs to assign. |
| `tags` | array[string] | No | `[]` | Tag strings to apply. |
| `note` | string | No | `null` | Internal note (not visible to client). |
| `metadata` | object | No | `{}` | Arbitrary metadata. |

---

## 4. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Generated UUID |
| `user_id` | Write (required) | Client assignment |
| `subject` | Write (required) | Ticket subject |
| `status` | Write | Default 1 (Open) |
| `order_id` | Write | Optional order link |
| `employees` | Write-only input, Read-only output | **Full replacement** |
| `tags` | Write-only input, Read-only output | **Full replacement** |
| `note` | Write | Internal note |
| `metadata` | Write | **Full replacement** |
| `source` | Read-only | Set to "API" on creation |
| `form_data` | Read-only | Empty object on API creation |
| `created_at` | Read-only | Set on creation |
| `updated_at` | Read-only | Set on creation |
| `last_message_at` | Read-only | Null initially; updated by messages |
| `date_closed` | Read-only | Null initially |
| `client` | Read-only | Joined in response |

### Replacement Semantics (No Merge)

**`employees`**: Full replacement. Provide the complete list of employee UUIDs to assign. Employees not in the list are unassigned.

**`tags`**: Full replacement. Provide the complete list of tags. Existing tags not in the list are removed.

**`metadata`**: Full replacement. The entire metadata object is replaced.

---

## 5. Side Effects

| Effect | Condition |
|--------|-----------|
| `ticket_employees` rows created | If `employees` provided |
| `ticket_tags` rows created | If `tags` provided |

---

## 6. Response Shape

### Success: 201 Created

```json
{
  "id": "ticket-uuid",
  "subject": "Ticket subject",
  "user_id": "client-uuid",
  "order_id": "order-uuid-or-null",
  "status": "Open",
  "status_id": 1,
  "source": "API",
  "note": "Internal note",
  "form_data": {},
  "metadata": { "key": "value" },
  "tags": ["tag1", "tag2"],
  "employees": [
    {
      "id": "employee-uuid",
      "name_f": "John",
      "name_l": "Doe",
      "role_id": "role-uuid"
    }
  ],
  "client": {
    "id": "client-uuid",
    "name": "Jane Smith",
    "name_f": "Jane",
    "name_l": "Smith",
    "email": "jane@example.com"
  },
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z",
  "last_message_at": null,
  "date_closed": null
}
```

---

## 7. Error Behavior

### 400 Bad Request

Validation failed.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "user_id": ["The user_id field is required."],
    "subject": ["The subject field is required."]
  }
}
```

### 401 Unauthorized

Missing or invalid authentication token.

### 422 Unprocessable Entity

Referential integrity failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "user_id": ["The specified client does not exist."],
    "order_id": ["The specified order does not exist."],
    "employees.0": ["The specified employee does not exist."]
  }
}
```

**Note:** Create never returns 404. All referential failures return 422.

---

## 8. Notes / Edge Cases

### Optional order_id

Tickets are **first-class entities** that can exist without orders.

| Scenario | Result |
|----------|--------|
| `order_id` omitted | Ticket created without order link |
| `order_id: null` | Same as omitted |
| `order_id: "valid-uuid"` | Ticket linked to order |
| `order_id: "invalid-uuid"` | 422 error |

### Soft-deleted order

If the specified `order_id` references a soft-deleted order, the request returns 422.

### last_message_at initialization

- `last_message_at` is `null` on ticket creation.
- Updated automatically when ticket messages are created.
- Cannot be set via API.

### Employee validation

- All employee UUIDs must reference valid team members.
- Invalid UUIDs return 422.
- Empty array `[]` is valid (no employees assigned).

### Status values

| Status | ID |
|--------|-----|
| Open | 1 |
| Pending | 2 |
| Closed | 3 |

Default is `1` (Open) if not specified.
