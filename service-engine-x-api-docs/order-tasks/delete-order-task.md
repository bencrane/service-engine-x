# Delete Order Task

```
DELETE /api/order-tasks/{id}
```

---

## Delete Semantics: Hard Delete

**Order tasks use hard delete.** The task is permanently removed from the database. This action cannot be undone.

**Rationale:**
- Tasks are work items without downstream financial dependencies
- No invoices, subscriptions, or audit records depend on tasks
- Hard delete matches SPP behavior: "Permanently deletes a task. This action cannot be undone."

---

## 1. Purpose

Permanently delete an order task. The task and all associated employee assignments are removed from the database and cannot be recovered.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with order management permissions.

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

None. Request body is ignored.

---

## 4. Field Semantics

Not applicable. Delete endpoint has no request body fields.

---

## 5. Side Effects

| Effect | Description |
|--------|-------------|
| **Task hard-deleted** | Row permanently removed from `order_tasks` |
| **Employee assignments deleted** | All rows in `order_task_employees` for this task are deleted (CASCADE) |
| **Order updated_at touched** | `orders.updated_at` refreshed |

---

## 6. Response Shape

### 204 No Content

Task successfully deleted. No response body.

```
HTTP/1.1 204 No Content
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
- Task was already deleted
- Task's parent order is soft-deleted

**Note:** 400 and 409 are not applicable to task deletion.

---

## 8. Notes / Edge Cases

### Hard Delete — No Recovery

Task deletion is permanent:
- Row is removed from database
- No `deleted_at` column
- Cannot be restored via API or admin action
- All employee assignments are cascade-deleted
- Consider implementing confirmation dialogs in UI

### Idempotency

- First delete: 204 No Content
- Subsequent deletes: 404 Not Found
- Not idempotent

### Cascade Behavior

| Related Entity | Behavior |
|----------------|----------|
| `order_task_employees` | CASCADE delete — all assignments removed |
| `orders` | Unaffected — order remains |

### Soft-Deleted Parent Order

If the task's parent order is soft-deleted:
- Task returns 404 (treated as non-existent)
- Cannot delete tasks for soft-deleted orders via API

However, if you have the task ID directly, the task row may still exist in the database but is inaccessible via API due to the parent order's soft-deleted state.

### Completed Tasks

Completed tasks (`is_complete: true`) can be deleted. There is no restriction preventing deletion of completed work.

### No Bulk Delete

Only single-task deletion is supported. To delete multiple tasks, make multiple requests.
