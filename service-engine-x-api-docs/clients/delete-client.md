# Delete Client

```
DELETE /api/clients/{id}
```

---

## 1. Purpose

Permanently deletes a client. This action cannot be undone.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator.

---

## 3. Request Parameters

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | **Yes** | Client identifier. |

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
| **Client record deleted** | Row removed from `users` table. |
| **Address orphaned** | Linked address record is NOT deleted. May become orphaned. |

---

## 5. Response Shape

### 204 No Content

Client successfully deleted. No response body.

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

Client does not exist.

```json
{
  "error": "Not Found"
}
```

**Causes:**
- Invalid UUID format
- UUID does not match any client

### 409 Conflict

Client has dependent records that prevent deletion.

```json
{
  "error": "Cannot delete client with existing orders"
}
```

```json
{
  "error": "Cannot delete client with existing invoices"
}
```

```json
{
  "error": "Cannot delete client with existing tickets"
}
```

```json
{
  "error": "Cannot delete client with existing subscriptions"
}
```

**Cause:** Foreign key constraints prevent deletion. Client has associated records in one or more of: `orders`, `invoices`, `tickets`, `subscriptions`.

---

## 8. Notes / Edge Cases

### Hard Delete Behavior

This endpoint performs a **hard delete**:
- The client row is permanently removed from the database
- The action cannot be undone
- No soft-delete flag or status change is used

### FK-Guarded Deletion

Deletion is blocked if the client has any dependent records:

| Table | Constraint | Check |
|-------|------------|-------|
| `orders` | `orders.user_id` | Any orders exist |
| `invoices` | `invoices.user_id` | Any invoices exist |
| `tickets` | `tickets.user_id` | Any tickets exist |
| `subscriptions` | `subscriptions.user_id` | Any subscriptions exist |

If any of these checks find records, the delete fails with 409 Conflict.

### Practical Implications

- Clients with transaction history cannot be deleted
- Only clients with zero associated records can be deleted
- This is intentional: business data should not disappear
- For clients that should no longer be active, use status updates instead

### Alternative: Deactivation

For clients with history who should no longer have access:

```json
PUT /api/clients/{id}
{ "status_id": 0 }
```

This preserves all historical data while marking the client as inactive.

### Address Records

The linked address record (if any) is **not** deleted when the client is deleted. Address records may become orphaned. This is acceptable—addresses are lightweight and may be referenced in historical invoice snapshots.

### Idempotency

- Deleting a non-existent client returns 404
- Deleting an already-deleted client returns 404
- The operation is not idempotent
