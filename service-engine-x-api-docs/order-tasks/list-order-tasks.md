# List Order Tasks

```
GET /api/orders/{id}/tasks
```

---

## 1. Purpose

Retrieve all tasks for a specific order, sorted by creation date descending.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with order access.

---

## 3. Request

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

## 4. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Task UUID |
| `order_id` | Read-only | Parent order reference |
| `name` | Read + Write | Task name |
| `description` | Read + Write | Task description |
| `sort_order` | Read + Write | Display order (lower = first) |
| `is_public` | Read + Write | If true, visible to client on portal |
| `for_client` | Read + Write | If true, client completes this task |
| `is_complete` | Read-only | Completion status |
| `completed_by` | Read-only | User who completed (null if incomplete) |
| `completed_at` | Read-only | Completion timestamp (null if incomplete) |
| `deadline` | Read + Write | Hours until deadline (mutually exclusive with `due_at`) |
| `due_at` | Read + Write | Specific due datetime (mutually exclusive with `deadline`) |
| `employees` | Read-only (joined) | Assigned employees array |

---

## 5. Side Effects

None. Read-only operation.

---

## 6. Response Shape

### 200 OK

```json
{
  "data": [
    {
      "id": "uuid",
      "order_id": "uuid",
      "name": "Design Logo",
      "description": "Create a new logo for the client",
      "sort_order": 1,
      "is_public": true,
      "for_client": false,
      "is_complete": false,
      "completed_by": null,
      "completed_at": null,
      "deadline": 72,
      "due_at": null,
      "employees": [
        {
          "id": "uuid",
          "name_f": "Jane",
          "name_l": "Smith"
        }
      ]
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

**Note:** 400 and 409 are not applicable to list endpoints.

---

## 8. Notes / Edge Cases

### Soft-Deleted Orders

If the parent order is soft-deleted, this endpoint returns 404. Tasks for soft-deleted orders cannot be retrieved via API.

### Visibility Rules

All tasks are returned regardless of `is_public` value — visibility filtering is a client-side concern. The API returns the full task list for authorized operators.

### Completion Fields

- `is_complete`: Boolean indicating task completion status
- `completed_by`: UUID of user who marked complete (null if incomplete)
- `completed_at`: Timestamp when marked complete (null if incomplete)

These fields are managed via separate mark-complete/incomplete endpoints (Section 1. Tasks), not via this endpoint.

### Deadline vs Due At

Tasks use one of two deadline mechanisms (mutually exclusive):
- `deadline`: Hours from order creation or previous task
- `due_at`: Specific datetime

Only one will have a value; the other will be null.

### Empty Results

If no tasks exist for the order:
- `data` is empty array `[]`
- `meta.total` is `0`
- Response is 200 OK (not 404)
