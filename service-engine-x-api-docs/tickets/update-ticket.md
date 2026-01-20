# Update Ticket

```
PUT /api/tickets/{id}
```

---

## 1. Purpose

Update an existing ticket. Supports partial updates—only provided fields are changed.

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

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | uuid | **Yes** | Ticket UUID. |

### Query Parameters

None.

### Request Body

```json
{
  "subject": "Updated subject",
  "status": 2,
  "order_id": "order-uuid-or-null",
  "employees": ["employee-uuid-1"],
  "tags": ["updated-tag"],
  "note": "Updated internal note",
  "metadata": { "updated": true }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `subject` | string | No | Update ticket subject. |
| `status` | integer | No | Update ticket status. |
| `order_id` | uuid/null | No | Link/unlink order. |
| `employees` | array[uuid] | No | **Full replacement** of assigned employees. |
| `tags` | array[string] | No | **Full replacement** of tags. |
| `note` | string | No | Update internal note. |
| `metadata` | object | No | **Full replacement** of metadata. |

**Note:** `user_id` (client) cannot be changed after creation.

---

## 4. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Cannot be changed |
| `user_id` | Read-only | Cannot be changed after creation |
| `subject` | Read + Write | |
| `status` | Read + Write | Integer input, string output |
| `order_id` | Read + Write | Can be set, changed, or set to null |
| `employees` | Write-only input, Read-only output | **Full replacement** |
| `tags` | Write-only input, Read-only output | **Full replacement** |
| `note` | Read + Write | |
| `metadata` | Write-only input, Read-only output | **Full replacement** |
| `source` | Read-only | Cannot be changed |
| `form_data` | Read-only | Cannot be changed |
| `created_at` | Read-only | |
| `updated_at` | Read-only | Updated automatically |
| `last_message_at` | Read-only | Updated by message creation |
| `date_closed` | Read-only | Set automatically when status → Closed |

### Replacement Semantics (No Merge)

**`employees`**: Full replacement.
- Provide all employee UUIDs that should be assigned.
- Omitting clears all assignments.
- Employees not in the new list are unassigned.

**`tags`**: Full replacement.
- Provide all tags that should exist.
- Omitting clears all tags.
- Tags not in the new list are removed.

**`metadata`**: Full replacement.
- The entire metadata object is replaced.
- Omitting clears metadata.
- No deep merge.

---

## 5. Side Effects

| Effect | Condition |
|--------|-----------|
| `updated_at` set to NOW() | Always |
| `ticket_employees` rows replaced | If `employees` provided |
| `ticket_tags` rows replaced | If `tags` provided |
| `date_closed` set | If `status` changed to Closed (3) |
| `date_closed` cleared | If `status` changed from Closed to other |

---

## 6. Response Shape

### Success: 200 OK

```json
{
  "id": "ticket-uuid",
  "subject": "Updated subject",
  "user_id": "client-uuid",
  "order_id": "order-uuid-or-null",
  "status": "Pending",
  "status_id": 2,
  "source": "Dashboard",
  "note": "Updated internal note",
  "form_data": {},
  "metadata": { "updated": true },
  "tags": ["updated-tag"],
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
    "email": "jane@example.com"
  },
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T14:00:00Z",
  "last_message_at": "2024-01-15T11:30:00Z",
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
    "status": ["The selected status is invalid."]
  }
}
```

### 401 Unauthorized

Missing or invalid authentication token.

### 404 Not Found

Ticket does not exist or has been soft-deleted.

```json
{
  "error": "Not Found"
}
```

### 422 Unprocessable Entity

Referential integrity failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "order_id": ["The specified order does not exist."],
    "employees.0": ["The specified employee does not exist."]
  }
}
```

---

## 8. Notes / Edge Cases

### Changing order_id

| Action | How |
|--------|-----|
| Link to order | `"order_id": "order-uuid"` |
| Unlink order | `"order_id": null` |
| Keep unchanged | Omit `order_id` from request |

### Soft-deleted order

Linking to a soft-deleted order returns 422.

### Closing a ticket

Setting `status: 3` (Closed) automatically sets `date_closed` to NOW().

Re-opening a closed ticket (changing status from 3 to 1 or 2) clears `date_closed`.

### Status values

| Status | ID |
|--------|-----|
| Open | 1 |
| Pending | 2 |
| Closed | 3 |

### last_message_at

Read-only. Cannot be modified via update. Only updated when ticket messages are created.
