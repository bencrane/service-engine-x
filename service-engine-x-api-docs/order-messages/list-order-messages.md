# List Order Messages

```
GET /api/orders/{id}/messages
```

---

## 1. Purpose

Retrieve all messages for a specific order. Messages are sorted by creation date in descending order (newest first).

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with order access.

**Visibility rules:**
- Staff users see all messages (including `staff_only: true`)
- Client users see only messages where `staff_only: false`

---

## 3. Request Parameters

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | **Yes** | Order identifier. |

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | `20` | Items per page. Range: 1–100. |
| `page` | integer | No | `1` | Page number. Must be ≥ 1. |

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
      "order_id": "uuid",
      "user_id": "uuid-or-null",
      "message": "Work has been completed.",
      "staff_only": false,
      "files": ["https://storage.example.com/file1.pdf"],
      "created_at": "2024-01-16T14:22:00+00:00"
    },
    {
      "id": "uuid",
      "order_id": "uuid",
      "user_id": "uuid",
      "message": "Internal note: verified deliverables",
      "staff_only": true,
      "files": [],
      "created_at": "2024-01-15T10:30:00+00:00"
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
    "last_page": 2,
    "per_page": 20,
    "total": 25,
    "path": "..."
  }
}
```

### Response Fields

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | UUID | No | Message identifier |
| `order_id` | UUID | No | Parent order reference |
| `user_id` | UUID | Yes | Author (null if user deleted) |
| `message` | string | No | Message content |
| `staff_only` | boolean | No | Staff-only visibility flag |
| `files` | array[string] | No | File URLs/IDs (empty array if none) |
| `created_at` | datetime | No | Creation timestamp |

---

## 6. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Generated UUID |
| `order_id` | Read-only | Set from path parameter |
| `user_id` | Read-only | Author; null if user was deleted (ON DELETE SET NULL) |
| `message` | Read-only | Immutable after creation |
| `staff_only` | Read-only | Immutable after creation |
| `files` | Read-only | File URLs/IDs; immutable after creation |
| `created_at` | Read-only | Auto-set at creation |

**Note:** All fields are read-only in list context. Messages are immutable — there is no update endpoint.

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

Order does not exist or is soft-deleted.

```json
{
  "error": "Not Found"
}
```

**Causes:**
- Invalid UUID format for `order_id`
- Order does not exist
- Order has been soft-deleted (`deleted_at IS NOT NULL`)

**Note:** 400 and 409 are not applicable to list endpoints.

---

## 8. Notes / Edge Cases

### Soft-Deleted Orders

If the parent order is soft-deleted, this endpoint returns 404. Messages for soft-deleted orders cannot be retrieved via API.

### Staff-Only Filtering

Messages with `staff_only: true` are internal communications:
- Visible to operators/staff
- Hidden from clients

Filtering is handled at the query level based on the authenticated user's role.

### Null User ID

`user_id` can be `null` if:
- The user who created the message has been deleted
- FK uses `ON DELETE SET NULL` to preserve message history

The message content remains intact even when the author is deleted.

### File Attachments

File attachments are supported via the `files` field:
- Stored as JSONB array in `order_messages.files`
- Contains URLs or file IDs (strings)
- No upload mechanism — files must be stored externally first
- Empty array `[]` if no attachments

### Message Immutability

Order messages are immutable:
- No `PUT` or `PATCH` endpoint exists
- Content cannot be modified after creation
- Only deletion is supported (hard delete)

### Empty Results

If no messages exist for the order:
- `data` is empty array `[]`
- `meta.total` is `0`
- Response is 200 OK (not 404)
