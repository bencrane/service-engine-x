# Update Order Task

```
PUT /api/order-tasks/{id}
```

---

## 1. Purpose

Update an existing task's properties. Partial updates supported — only provided fields are changed.

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
| `Content-Type` | string | Yes (`application/json`) |
| `Accept` | string | Yes (`application/json`) |
| `X-Api-Version` | string | No |

### Request Body

All fields are optional. Only provided fields are updated.

```json
{
  "name": "Updated Task Name",
  "description": "Updated description",
  "employee_ids": ["uuid-1"],
  "sort_order": 2,
  "is_public": false,
  "for_client": false,
  "deadline": 48,
  "due_at": null
}
```

### Body Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | No | Task name. Non-empty if provided. |
| `description` | string | No | Task description. |
| `employee_ids` | array[UUID] | No | Employees to assign. **Full replacement.** |
| `sort_order` | integer | No | Display order. |
| `is_public` | boolean | No | Portal visibility. |
| `for_client` | boolean | No | Client-completable flag. |
| `deadline` | integer | No | Hours until deadline. Mutually exclusive with `due_at`. |
| `due_at` | datetime | No | Specific due datetime. Mutually exclusive with `deadline`. |

### Validation Rules

| Rule | Description |
|------|-------------|
| `name` non-empty | If provided, must be non-empty string. |
| `employee_ids` valid | Each UUID must reference existing team member. |
| `for_client` + `employee_ids` exclusive | If `for_client: true`, `employee_ids` must be empty or omitted. |
| `deadline` + `due_at` exclusive | Only one can be set, not both. |

---

## 4. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Cannot be changed |
| `order_id` | Read-only | Cannot be changed |
| `name` | Read + Write | |
| `description` | Read + Write | |
| `employee_ids` | Write-only | **Full replacement**; not returned in response |
| `sort_order` | Read + Write | |
| `is_public` | Read + Write | |
| `for_client` | Read + Write | |
| `deadline` | Read + Write | Mutually exclusive with `due_at` |
| `due_at` | Read + Write | Mutually exclusive with `deadline` |
| `is_complete` | Read-only | Managed via mark-complete endpoint |
| `completed_by` | Read-only | Managed via mark-complete endpoint |
| `completed_at` | Read-only | Managed via mark-complete endpoint |
| `employees` | Read-only (joined) | Returned in response |

### Replacement Semantics (No Merge)

`employee_ids` is **full replacement**:
- All existing assignments are removed
- All provided UUIDs are assigned
- No merge behavior
- Pass `[]` to remove all employee assignments

### Write-Time Ignored Fields

| Field | Behavior |
|-------|----------|
| `id` | Ignored, immutable |
| `order_id` | Ignored, immutable |
| `is_complete` | Ignored, managed via separate endpoint |
| `completed_by` | Ignored, managed via separate endpoint |
| `completed_at` | Ignored, managed via separate endpoint |

---

## 5. Side Effects

| Effect | Description |
|--------|-------------|
| **Task updated** | Row updated in `order_tasks` table |
| **Employees replaced** | If `employee_ids` provided, junction rows deleted and re-inserted |
| **Order updated_at touched** | `orders.updated_at` refreshed |

---

## 6. Response Shape

### 200 OK

```json
{
  "id": "uuid",
  "order_id": "uuid",
  "name": "Updated Task Name",
  "description": "Updated description",
  "sort_order": 2,
  "is_public": false,
  "for_client": false,
  "is_complete": false,
  "completed_by": null,
  "completed_at": null,
  "deadline": 48,
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
    "name": ["The name field cannot be empty."],
    "for_client": ["Cannot assign employees when for_client is true."]
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

**Note:** 409 is not applicable to task updates.

---

## 8. Notes / Edge Cases

### Partial Update Semantics

Only fields included in the request body are updated. Omitted fields retain their current values.

```json
// Only updates sort_order
{ "sort_order": 5 }
```

### for_client vs employee_ids (Mutually Exclusive)

When updating, the validation applies to the **resulting state**:
- If setting `for_client: true`, any existing employee assignments must be cleared
- If providing `employee_ids`, `for_client` must be `false` (or omitted/false)

```json
// Valid: clear employees and set for_client
{
  "for_client": true,
  "employee_ids": []
}
```

### deadline vs due_at (Mutually Exclusive)

When updating:
- If setting `deadline`, `due_at` should be set to `null` (or omitted if currently `null`)
- If setting `due_at`, `deadline` should be set to `null` (or omitted if currently `null`)

To switch from one to the other:

```json
// Switch from deadline to due_at
{
  "deadline": null,
  "due_at": "2024-12-31T23:59:59+00:00"
}
```

### Employee Replacement

When `employee_ids` is provided:
1. All existing `order_task_employees` rows for this task are deleted
2. New rows are inserted for each provided UUID

To remove all employees:

```json
{ "employee_ids": [] }
```

### Completion Fields Not Editable

`is_complete`, `completed_by`, and `completed_at` are managed via separate mark-complete/incomplete endpoints (Section 1. Tasks) and cannot be modified via this endpoint.

### Soft-Deleted Parent Order

If the task's parent order is soft-deleted, the task returns 404. Tasks on soft-deleted orders cannot be updated.
