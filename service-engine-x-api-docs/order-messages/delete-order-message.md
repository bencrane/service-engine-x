# Delete Order Message

```
DELETE /api/order-messages/{id}
```

---

## Delete Semantics: Hard Delete

**Order messages use hard delete.** The message is permanently removed from the database. This action cannot be undone.

**Rationale:**
- Messages are immutable (no edit capability) — deletion is the only modification
- No downstream entities depend on messages via FK
- Message history can be exported before deletion if needed
- Aligns with SPP behavior: "This action cannot be undone"

**Contrast with Orders:** Orders use soft delete because they are the economic spine referenced by invoices, subscriptions, and financial records. Messages have no such downstream dependencies.

---

## 1. Purpose

Permanently delete an order message. The message is removed from the database and cannot be recovered.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with messaging permissions.

---

## 3. Request Parameters

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | **Yes** | Message identifier. |

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
| **Message hard-deleted** | Row permanently removed from `order_messages` |
| **Order timestamp NOT updated** | `last_message_at` is NOT recalculated |

### Note on last_message_at

Deleting a message does **not** recalculate `orders.last_message_at`. The timestamp reflects when the last message was *created*, not the current state. This is intentional:
- Recalculation would be expensive (requires scanning remaining messages)
- The field indicates activity timing, not current message count
- Consistent with SPP behavior

---

## 5. Response Shape

### 204 No Content

Message successfully deleted. No response body.

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

Message does not exist.

```json
{
  "error": "Not Found"
}
```

**Causes:**
- Invalid UUID format
- Message ID does not exist
- Message was already deleted

**Note:** 400 and 409 are not applicable to message deletion.

---

## 8. Notes / Edge Cases

### Hard Delete — No Recovery, No Audit Log

Unlike soft-deleted entities (orders, services), message deletion is **permanent and irreversible**:
- Row is removed from database
- No `deleted_at` column exists
- Cannot be restored via API or admin action
- **No audit log** of deleted messages
- File references are lost (external files may remain in storage)
- Consider implementing export/backup before deletion in production workflows

### Idempotency

- First delete: 204 No Content
- Subsequent deletes: 404 Not Found
- Not idempotent

### Soft-Deleted Parent Order

Messages belonging to soft-deleted orders:
- Can still be deleted via this endpoint (if message ID is known)
- The message row is removed regardless of parent order state
- Order itself remains soft-deleted

### Cascade Behavior

| Scenario | Behavior |
|----------|----------|
| Delete message | Message row removed |
| Delete user (author) | `user_id` set to NULL (ON DELETE SET NULL) |
| Delete order (soft) | Messages preserved; order hidden |

Messages are preserved when their parent order is soft-deleted. Only explicit message deletion removes them.

### No Bulk Delete

Only single-message deletion is supported. To delete multiple messages, make multiple requests.

### Audit Considerations

Since deletion is permanent and cannot be undone:
- Consider logging deletions externally for audit purposes
- Implement confirmation dialogs in UI
- Restrict delete permissions appropriately

### File Attachments

When a message with files is deleted:
- The `files` array (URLs/IDs) is removed with the message
- **External files are NOT deleted** — they remain in storage
- No cleanup mechanism is triggered
- Orphaned files must be handled separately if storage cleanup is needed
