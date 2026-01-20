# Delete Ticket

```
DELETE /api/tickets/{id}
```

---

## Delete Semantics: Soft Delete

**Tickets use soft delete.** The `deleted_at` timestamp is set, but the ticket remains in the database. The ticket becomes inaccessible via API afterward.

**Rationale:**
- Tickets may contain important support history
- Related messages and audit trail should be preserved
- Reversibility required for accidental deletions
- SPP explicitly states "It can be undone"

**Behavior:**
- Ticket marked with `deleted_at = NOW()`
- Returns 204 No Content
- Ticket excluded from list/retrieve afterward
- Ticket messages remain in database (no cascade delete)
- No API recovery mechanism (admin-only database restore)

**Contrast with Clients:**
- Clients use **hard delete** with FK guard (409 if dependencies exist)
- Tickets use **soft delete** (always succeeds, reversible)

---

## 1. Purpose

Soft-delete a ticket. The ticket becomes inaccessible via API but is retained in the database.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated user with `ticket_management` permission.

---

## 3. Request

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | uuid | **Yes** | Ticket UUID. |

### Query Parameters

None.

### Request Body

None.

---

## 4. Field Semantics

Not applicable (no response body).

---

## 5. Side Effects

| Effect | Description |
|--------|-------------|
| `deleted_at` set to NOW() | Ticket soft-deleted |
| `updated_at` set to NOW() | Timestamp updated |
| Ticket messages retained | No cascade delete |

---

## 6. Response Shape

### Success: 204 No Content

No response body.

---

## 7. Soft-Delete Visibility

After deletion:
- `GET /api/tickets` — ticket excluded from list
- `GET /api/tickets/{id}` — returns 404
- `PUT /api/tickets/{id}` — returns 404
- `DELETE /api/tickets/{id}` — returns 404 (already deleted)

**No `include_deleted` parameter is supported.**

---

## 8. Error Behavior

### 400 Bad Request

Invalid UUID format.

```json
{
  "error": "Invalid ticket ID format."
}
```

### 401 Unauthorized

Missing or invalid authentication token.

### 404 Not Found

Ticket does not exist or has already been soft-deleted.

```json
{
  "error": "Not Found"
}
```

---

## 9. Notes / Edge Cases

### Idempotency

Not idempotent. Deleting an already-deleted ticket returns 404.

### Message preservation

Ticket messages are **not** cascade-deleted. They remain in the database but are inaccessible since the parent ticket returns 404.

### Order reference

If the ticket has an `order_id`, the order is not affected. The ticket is simply unlinked by soft delete.

### Recovery

No API mechanism for recovery. Database-level restore required.
