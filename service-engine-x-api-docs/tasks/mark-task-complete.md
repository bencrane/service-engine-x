# Mark Task Complete

```
POST /api/order-tasks/{id}/complete
```

---

## 1. Purpose

Mark an order task as complete, recording who completed it and when.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated user with access to the task's order. Both staff and clients (if `for_client: true`) may complete tasks.

---

## 3. Request

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | **Yes** | Task identifier. |

### Request Headers

| Header | Type | Required |
|--------|------|----------|
| `Authorization` | string | Yes |
| `Accept` | string | Yes (`application/json`) |
| `X-Api-Version` | string | No |

### Request Body

None. No request body expected.

---

## 4. Field Semantics

This endpoint modifies three fields on the task:

| Field | Before | After | Notes |
|-------|--------|-------|-------|
| `is_complete` | `false` | `true` | Completion status |
| `completed_by` | `null` | `{user_id}` | UUID of authenticated user |
| `completed_at` | `null` | `{timestamp}` | Current server timestamp |

These fields are **not directly writable** via task create/update endpoints — they are only mutated via this toggle endpoint.

---

## 5. Side Effects

| Effect | Description |
|--------|-------------|
| **Task updated** | `is_complete`, `completed_by`, `completed_at` set |
| **Order updated_at touched** | `orders.updated_at` refreshed |

---

## 6. Response Shape

### 200 OK

Returns the updated task object.

```json
{
  "id": "uuid",
  "order_id": "uuid",
  "name": "Design Logo",
  "description": "Create a new logo for the client",
  "sort_order": 1,
  "is_public": true,
  "for_client": false,
  "is_complete": true,
  "completed_by": "uuid",
  "completed_at": "2024-01-15T10:30:00Z",
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

Task does not exist.

```json
{
  "error": "Not Found"
}
```

**Causes:**
- Invalid UUID format
- Task ID does not exist
- Task's parent order is soft-deleted

**Note:** 400 and 409 are not applicable.

---

## 8. Notes / Edge Cases

### Idempotency

Marking an already-complete task as complete is a no-op:
- Returns 200 OK
- `completed_by` and `completed_at` are **not** overwritten
- Original completion metadata is preserved

### Client vs Staff Completion

| Task State | Who Can Complete |
|------------|------------------|
| `for_client: true` | Client or staff |
| `for_client: false` | Staff only |

If a client attempts to complete a staff-only task, return 403 Forbidden.

### Soft-Deleted Parent Order

If the task's parent order is soft-deleted, the task returns 404. Tasks on soft-deleted orders cannot be completed.

### Completion Timestamp

`completed_at` is set to the server's current timestamp at the moment of completion. Clients cannot specify a custom completion time.
