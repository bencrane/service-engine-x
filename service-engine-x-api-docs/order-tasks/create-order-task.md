# Create Order Task

```
POST /api/orders/{id}/tasks
```

---

## 1. Purpose

Create a new task on an order for tracking work items or client deliverables.

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
| `id` | UUID | **Yes** | Order identifier. |

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
  "name": "Design Logo",
  "description": "Create a new logo for the client",
  "employee_ids": ["uuid-1", "uuid-2"],
  "sort_order": 1,
  "is_public": true,
  "for_client": false,
  "deadline": 72,
  "due_at": null
}
```

### Body Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | **Yes** | — | Task name. Non-empty. |
| `description` | string | No | `null` | Task description. |
| `employee_ids` | array[UUID] | No | `[]` | Employees to assign. **Full replacement.** |
| `sort_order` | integer | No | `0` | Display order (lower = first). |
| `is_public` | boolean | No | `false` | If true, visible to client on portal. |
| `for_client` | boolean | No | `false` | If true, client completes this task. |
| `deadline` | integer | No | `null` | Hours until deadline. Mutually exclusive with `due_at`. |
| `due_at` | datetime | No | `null` | Specific due datetime. Mutually exclusive with `deadline`. |

### Validation Rules

| Rule | Description |
|------|-------------|
| `name` required | Non-empty string. |
| `employee_ids` valid | Each UUID must reference existing team member. |
| `for_client` + `employee_ids` exclusive | If `for_client: true`, `employee_ids` must be empty or omitted. |
| `deadline` + `due_at` exclusive | Only one can be set, not both. |

---

## 4. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Generated UUID |
| `order_id` | Read-only | Set from path parameter |
| `name` | Write (required) | Task name |
| `description` | Write | Task description |
| `employee_ids` | Write-only | **Full replacement**; not returned in response |
| `sort_order` | Write | Display order |
| `is_public` | Write | Portal visibility |
| `for_client` | Write | Client-completable flag |
| `deadline` | Write | Hours until due (mutually exclusive with `due_at`) |
| `due_at` | Write | Specific due datetime (mutually exclusive with `deadline`) |
| `is_complete` | Read-only | Always `false` on create |
| `completed_by` | Read-only | Always `null` on create |
| `completed_at` | Read-only | Always `null` on create |
| `employees` | Read-only (joined) | Returned in response as joined array |

### Replacement Semantics (No Merge)

`employee_ids` is **full replacement**:
- All provided UUIDs are assigned
- No merge with existing assignments (task is new)
- Pass `[]` or omit to create task without employee assignments

### Write-Time Ignored Fields

| Field | Behavior |
|-------|----------|
| `id` | Ignored, always generated |
| `order_id` | Ignored in body, taken from path |
| `is_complete` | Ignored, always `false` |
| `completed_by` | Ignored, always `null` |
| `completed_at` | Ignored, always `null` |

---

## 5. Side Effects

| Effect | Description |
|--------|-------------|
| **Task created** | New row in `order_tasks` table |
| **Employees assigned** | Rows inserted into `order_task_employees` junction |
| **Order updated_at touched** | `orders.updated_at` refreshed |

---

## 6. Response Shape

### 201 Created

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

### 400 Bad Request

Validation failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "name": ["The name field is required."],
    "for_client": ["Cannot assign employees when for_client is true."]
  }
}
```

**Common validation errors:**
- Missing `name` field
- Both `deadline` and `due_at` provided
- `for_client: true` with non-empty `employee_ids`

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

### 422 Unprocessable Entity

Referential integrity failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "employee_ids": ["Employee with ID uuid-x does not exist."]
  }
}
```

**Note:** 409 is not applicable to task creation.

---

## 8. Notes / Edge Cases

### for_client vs employee_ids (Mutually Exclusive)

Tasks are either:
1. **Staff tasks**: Assigned to employees (`for_client: false`, `employee_ids` populated)
2. **Client tasks**: Completed by the client (`for_client: true`, `employee_ids` must be empty)

If `for_client: true` is set with non-empty `employee_ids`, return 400.

### deadline vs due_at (Mutually Exclusive)

Two deadline mechanisms exist:
1. **Relative**: `deadline` = hours from order creation or previous task
2. **Absolute**: `due_at` = specific datetime

If both are provided, return 400. At most one can be set.

### Soft-Deleted Orders

Cannot create tasks on soft-deleted orders. Returns 404.

### Default Values

New tasks are created with:
- `is_complete: false`
- `completed_by: null`
- `completed_at: null`

Completion is managed via separate endpoints (Section 1. Tasks).

### Employee Assignment

Employees are assigned via `employee_ids` in the request, but returned as full `employees` array in the response with `id`, `name_f`, `name_l`.
