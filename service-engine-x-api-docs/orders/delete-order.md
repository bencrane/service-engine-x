# Delete Order

```
DELETE /api/orders/{id}
```

---

## Delete Semantics: Soft Delete

**Orders use soft delete.** Unlike Clients (which use hard delete with FK guard), Orders are marked as deleted but preserved in the database.

**Rationale:**
- Orders are the economic spine of the system — they must be preserved for audit and reporting
- Invoices, subscriptions, and messages reference orders via FK
- Historical revenue and activity data depends on order existence
- Deleted orders may need to be restored for dispute resolution

**Contrast with Clients:** Clients use hard delete because orphaned user references break FK integrity across the system. Orders have the opposite constraint — they must persist because they are referenced by financial and communication records.

---

## 1. Purpose

Delete an order. Sets `deleted_at` timestamp. The order remains in the database but is excluded from queries. This action can be undone.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated operator with order management permissions.

---

## 3. Request Parameters

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | **Yes** | Order identifier. |

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
| **Order soft-deleted** | `deleted_at` timestamp set |
| **Order hidden from lists** | No longer returned in list queries |
| **Employee assignments preserved** | `order_employees` rows NOT deleted |
| **Tag assignments preserved** | `order_tags` rows NOT deleted |
| **Messages preserved** | `order_messages` rows NOT deleted |
| **Tasks preserved** | `order_tasks` rows NOT deleted |
| **Invoice reference preserved** | Invoice still references this order |

---

## 5. Response Shape

### 204 No Content

Order successfully deleted. No response body.

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

Order does not exist or is already soft-deleted.

```json
{
  "error": "Not Found"
}
```

**Causes:**
- Invalid UUID format
- UUID does not match any order
- Order is already soft-deleted (`deleted_at IS NOT NULL`)

**Note:** 400 is not applicable (no request body). 409 is not applicable (no FK guard for orders — they can be deleted even with dependent records).

---

## 8. Notes / Edge Cases

### Soft Delete Behavior

- Sets `deleted_at = NOW()` on the order record
- Order row remains in database
- Order excluded from list results
- Order returns 404 on retrieve
- All related records (messages, tasks, employees, tags) preserved

### No FK Guard

Unlike clients, orders can be deleted even if they have:
- Linked invoices (`invoice_id`)
- Linked subscriptions (`subscription_id`)
- Order messages
- Order tasks
- Assigned employees
- Assigned tags

This is because:
- Financial records (invoices) maintain their own data integrity
- Messages and tasks are part of the order's history
- Deletion is soft — data remains for audit purposes

### Idempotency

- First delete: 204 No Content
- Subsequent deletes: 404 Not Found
- Not idempotent

### Impact on Related Records

| Related Entity | Impact |
|----------------|--------|
| `invoices` | None — invoice retains `order_id` reference |
| `subscriptions` | None — subscription retains reference |
| `order_messages` | None — messages preserved |
| `order_tasks` | None — tasks preserved |
| `order_employees` | None — assignments preserved |
| `order_tags` | None — tags preserved |

All related records remain intact. If order is restored, all relationships are still valid.

### Restoring Deleted Orders

Not exposed via API. Requires direct database update:
```sql
UPDATE orders SET deleted_at = NULL WHERE id = 'uuid';
```

After restoration:
- Order reappears in list results
- Order retrievable via GET
- All related records (messages, tasks, etc.) immediately visible again

### Invoice Handling

When an order is soft-deleted:
- The linked invoice (if any) remains unchanged
- Invoice is still valid and payable
- Invoice `order_id` still references the deleted order

This is intentional — invoices represent financial obligations independent of order status.

### Cascade Behavior Summary

| Operation | Behavior |
|-----------|----------|
| Order soft delete | Only sets `deleted_at` on order |
| Employee/tag/message/task cascade | None — all preserved |
| Invoice cascade | None — invoice unaffected |
| Subscription cascade | None — subscription unaffected |

### Delete vs Cancel

| Action | Method | Effect |
|--------|--------|--------|
| Delete | `DELETE /api/orders/{id}` | Soft delete; order hidden |
| Cancel | `PUT /api/orders/{id}` with `{ "status": 3 }` | Status change; order visible |

For orders that should remain visible but inactive, use status update (cancel) rather than delete.
