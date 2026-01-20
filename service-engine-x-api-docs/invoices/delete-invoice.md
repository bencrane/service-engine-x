# Delete Invoice

```
DELETE /api/invoices/{id}
```

---

## Delete Semantics: Soft Delete

**Invoices use soft delete only.** The `deleted_at` timestamp is set, but the invoice remains in the database. The invoice becomes inaccessible via API afterward.

**Rationale:**
- Invoices are financial records with legal/audit requirements
- Associated orders, subscriptions, and payments reference the invoice
- Reversibility required for accounting reconciliation
- Payment history must be preserved

**Behavior:**
- Invoice marked with `deleted_at = NOW()`
- Returns 204 No Content
- Invoice excluded from list/retrieve afterward
- No API recovery mechanism
- Database record retained indefinitely

---

## 1. Purpose

Soft-delete an invoice. The invoice becomes inaccessible via API but is retained in the database.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated **staff** with invoice management permissions.

| User Type | Can Delete |
|-----------|------------|
| Staff (invoice_management) | ✅ Yes |
| Staff (invoice_access only) | ❌ No |
| Client | ❌ No |

---

## 3. Request

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | **Yes** | Invoice identifier. |

### Request Headers

| Header | Type | Required |
|--------|------|----------|
| `Authorization` | string | Yes |
| `Accept` | string | Yes (`application/json`) |

### Request Body

None. Request body is ignored.

---

## 4. Field Semantics

Not applicable. Delete endpoint has no request body fields.

---

## 5. Side Effects

| Effect | Description |
|--------|-------------|
| **Invoice soft-deleted** | `deleted_at` timestamp set |
| **Items retained** | `invoice_items` remain in database |
| **Orders unaffected** | Associated orders are not deleted |
| **Subscriptions unaffected** | Associated subscriptions continue |

---

## 6. Response Shape

### 204 No Content

Invoice successfully deleted. No response body.

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

Invoice does not exist or is already soft-deleted.

```json
{
  "error": "Not Found"
}
```

**Causes:**
- Invalid UUID format
- Invoice ID does not exist
- Invoice was already soft-deleted

**Note:** 400 and 409 are not applicable.

---

## 8. Notes / Edge Cases

### Soft Delete — No API Recovery

Once deleted:
- Invoice returns 404 on retrieve
- Invoice excluded from list results
- No `include_deleted` parameter exists
- Recovery requires direct database access

### Idempotency

- First delete: 204 No Content
- Subsequent deletes: 404 Not Found
- Not idempotent

### Paid Invoices

Paid invoices can be deleted. However:
- Payment records in processor remain
- Associated orders remain active
- Financial history preserved in database

### Recurring Invoices

Deleting a recurring invoice:
- Does NOT cancel the associated subscription
- Future invoices may still generate
- Cancel subscription separately if needed

### Invoice Items

Invoice items (`invoice_items`) are **not** cascade-deleted:
- Items remain in database with `invoice_id` reference
- Items become orphaned from API perspective
- May be visible in database but not via API

### Contrast with Other Entities

| Entity | Delete Behavior |
|--------|----------------|
| **Invoices** | Soft delete (this endpoint) |
| **Clients** | Hard delete + FK guard |
| **Orders** | Soft delete |
| **Services** | Soft delete |
| **Order Tasks** | Hard delete |
| **Order Messages** | Hard delete |
