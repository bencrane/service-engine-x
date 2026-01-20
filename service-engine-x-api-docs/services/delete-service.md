# Delete Service

```
DELETE /api/services/{id}
```

---

## Delete Semantics: Soft Delete

**Services use soft delete.** Unlike Clients (which use hard delete with FK guard), Services are marked as deleted but preserved in the database.

**Rationale:**
- Orders store service data as snapshots at creation time
- Historical orders must remain valid and auditable
- Deleted services may need to be restored
- No referential integrity risk from soft-deleted services

**Contrast with Clients:** Clients use hard delete because orphaned `user_id` references break FK integrity. Services do not have this constraint.

---

## 1. Purpose

Delete a service. Sets `deleted_at` timestamp. The service remains in the database but is excluded from queries. This action can be undone.

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

Service does not exist or is already soft-deleted.

```json
{
  "error": "Not Found"
}
```

**Causes:**
- Invalid UUID format
- UUID does not match any service
- Service is already soft-deleted (`deleted_at IS NOT NULL`)

**Note:** 400 is not applicable (no request body). 409 is not applicable (no FK guard for services).

---

## 8. Notes / Edge Cases

### Soft Delete Behavior

- Sets `deleted_at = NOW()` on the service record
- Service row remains in the database
- Service excluded from list results
- Service returns 404 on retrieve
- Employee assignments preserved in `service_employees`

### Idempotency

- First delete: 204 No Content
- Subsequent deletes: 404 Not Found
- Not idempotent

### Impact on Existing Orders

None. Orders store service snapshots. Historical data remains valid.

### Restoring Deleted Services

Not exposed via API. Requires direct database update to clear `deleted_at`.
