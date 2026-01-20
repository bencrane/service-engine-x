# Delete Service

```
DELETE /api/services/{id}
```

---

## 1. Purpose

Delete a service. This is a **soft delete** — the service is marked as deleted but remains in the database. This action can be undone.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with service management permissions.

---

## 3. Request Parameters

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | **Yes** | Service identifier. |

### Request Headers

| Header | Type | Required |
|--------|------|----------|
| `Authorization` | string | Yes |
| `Accept` | string | Yes (`application/json`) |
| `X-Api-Version` | string | No |

### Request Body

None. Request body is ignored.

---

## 4. Side Effects

| Effect | Description |
|--------|-------------|
| **Service soft-deleted** | `deleted_at` timestamp set on the service record |
| **Service hidden from lists** | No longer returned in list queries |
| **Employee assignments preserved** | `service_employees` rows are NOT deleted |

---

## 5. Response Shape

### 204 No Content

Service successfully deleted. No response body.

```
HTTP/1.1 204 No Content
```

---

## 6. Field Semantics

Not applicable. Delete endpoint has no request body fields.

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

Service does not exist.

```json
{
  "error": "Not Found"
}
```

**Causes:**
- Invalid UUID format
- UUID does not match any service
- Service is already soft-deleted

---

## 8. Notes / Edge Cases

### Soft Delete Behavior

This endpoint performs a **soft delete**:
- Sets `deleted_at = NOW()` on the service record
- The service row remains in the database
- The service no longer appears in list results
- The service cannot be retrieved via GET
- The action can be undone (restore functionality)

### No FK Guard

Unlike clients, services can be deleted even if they have:
- Orders referencing them
- Subscriptions referencing them
- Assigned employees

This is because:
- Orders store service data as a snapshot at creation time
- Deleting a service does not affect historical orders
- The service data remains queryable for internal/audit purposes

### Employee Assignments

The `service_employees` junction table rows are **preserved** on soft delete. If the service is restored, employee assignments are still intact.

### Idempotency

- Deleting an already-deleted service returns 404
- The operation is not truly idempotent
- First delete succeeds with 204, subsequent deletes return 404

### Impact on Existing Orders

Soft-deleting a service has **no impact** on existing orders:
- Orders that reference this service remain valid
- Order data is not modified
- Historical reporting remains accurate

New orders cannot be created for a deleted service. The service will not appear in service selection interfaces.

### Restoring Deleted Services

To restore a soft-deleted service (if implemented):
- Clear the `deleted_at` field
- Service reappears in list results
- Service becomes orderable again

Restoration is **not currently exposed** via API. Manual database intervention is required.

### Different from Client Delete

| Aspect | Client Delete | Service Delete |
|--------|---------------|----------------|
| Type | Hard delete | Soft delete |
| FK Guard | Yes (409 if dependencies) | No |
| Reversible | No | Yes (via restore) |
| Data preserved | No | Yes |

This difference exists because:
- Clients are identity records; orphaned client IDs break referential integrity
- Services are catalog items; deleted services should be preserved for historical accuracy
