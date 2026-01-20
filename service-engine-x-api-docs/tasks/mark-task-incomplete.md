# Mark Task Incomplete

```
DELETE /api/order-tasks/{id}/complete
```

---

## 1. Purpose

Mark a previously completed order task as incomplete, clearing completion metadata.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated staff user with access to the task's order. Clients cannot mark tasks incomplete.

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
| `is_complete` | `true` | `false` | Completion status |
| `completed_by` | `{user_id}` | `null` | Cleared |
| `completed_at` | `{timestamp}` | `null` | Cleared |

These fields are **not directly writable** via task create/update endpoints — they are only mutated via this toggle endpoint.

---

## 5. Side Effects

| Effect | Description |
|--------|-------------|
| **Task updated** | `is_complete`, `completed_by`, `completed_at` cleared |
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

### 403 Forbidden

Client user attempting to mark task incomplete.

```json
{
  "error": "Forbidden"
}
```

Only staff users may mark tasks incomplete, regardless of `for_client` setting.

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

Marking an already-incomplete task as incomplete is a no-op:
- Returns 200 OK
- Fields are already null/false
- No data changes occur

### Client Restriction

Unlike mark-complete (which allows clients on `for_client: true` tasks), mark-incomplete is **staff-only**. This prevents clients from undoing completed work.

| User Type | Can Mark Complete | Can Mark Incomplete |
|-----------|-------------------|---------------------|
| Staff | ✅ Yes | ✅ Yes |
| Client (`for_client: true`) | ✅ Yes | ❌ No |
| Client (`for_client: false`) | ❌ No | ❌ No |

### Soft-Deleted Parent Order

If the task's parent order is soft-deleted, the task returns 404. Tasks on soft-deleted orders cannot be marked incomplete.

### Original Completer Not Preserved

When unmarking a task, the original `completed_by` and `completed_at` values are lost. There is no history of prior completion states.
