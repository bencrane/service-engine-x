# Create Order Message

```
POST /api/order-messages/{order_id}
```

---

## 1. Purpose

Create a new message on an order. Messages are immutable after creation — there is no update endpoint.

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
| `order_id` | UUID | **Yes** | Order identifier. |

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
  "message": "Work has been completed. Please review.",
  "user_id": "uuid",
  "staff_only": false
}
```

### Body Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `message` | string | **Yes** | — | Message content. Non-empty. |
| `user_id` | UUID | No | Authenticated user | Author override. |
| `staff_only` | boolean | No | `false` | If true, only staff can see. |

### Validation Rules

| Field | Rule |
|-------|------|
| `message` | Required. Non-empty string. |
| `user_id` | If provided, must reference existing user. |
| `staff_only` | Must be boolean if provided. |

---

## 4. Side Effects

| Effect | Description |
|--------|-------------|
| **Message created** | New row in `order_messages` table |
| **Order timestamp updated** | `orders.last_message_at` set to message `created_at` |
| **Order updated_at touched** | `orders.updated_at` refreshed |

---

## 5. Response Shape

### 201 Created

```json
{
  "id": "uuid",
  "order_id": "uuid",
  "user_id": "uuid",
  "message": "Work has been completed. Please review.",
  "staff_only": false,
  "created_at": "2024-01-16T14:22:00+00:00"
}
```

### Response Fields

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | UUID | No | Generated message identifier |
| `order_id` | UUID | No | Parent order reference |
| `user_id` | UUID | Yes | Author (from request or authenticated user) |
| `message` | string | No | Message content |
| `staff_only` | boolean | No | Visibility flag |
| `created_at` | datetime | No | Creation timestamp |

---

## 6. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | Generated UUID |
| `order_id` | Read-only | Set from path parameter |
| `user_id` | Write (optional) | Defaults to authenticated user if omitted |
| `message` | Write (required) | Immutable after creation |
| `staff_only` | Write (optional) | Defaults to `false`; immutable after creation |
| `created_at` | Read-only | Auto-set to `NOW()` |

### User ID Defaulting Behavior

When `user_id` is not provided in the request:
- Defaults to the authenticated user's ID
- This is the standard case for operators posting messages

When `user_id` is provided:
- Must reference a valid, existing user
- Allows posting on behalf of another user (e.g., system messages, migrations)
- 422 returned if user does not exist

### Write-Time Ignored Fields

| Field | Behavior |
|-------|----------|
| `id` | Ignored, always generated |
| `order_id` | Ignored in body, taken from path |
| `created_at` | Ignored, always `NOW()` |

---

## 7. Error Behavior

### 400 Bad Request

Validation failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "message": ["The message field is required."]
  }
}
```

**Common validation errors:**
- Missing `message` field
- Empty `message` string
- Invalid `staff_only` type

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

**Causes:**
- Invalid UUID format for `order_id`
- Order does not exist
- Order has been soft-deleted

### 422 Unprocessable Entity

Referential integrity failure.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "user_id": ["The specified user does not exist."]
  }
}
```

**Causes:**
- `user_id` provided but does not reference existing user

**Note:** 409 is not applicable to message creation.

---

## 8. Notes / Edge Cases

### Message Immutability

Messages are immutable once created:
- No update endpoint exists
- Content, `staff_only`, and `user_id` cannot be modified
- Only hard delete is supported

To "edit" a message, delete and recreate.

### Staff-Only Messages

When `staff_only: true`:
- Message is visible only to operators/staff
- Clients cannot see the message in their portal
- Useful for internal notes, handoff comments, QA feedback

Default is `false` (visible to all).

### Order Timestamp Update

Creating a message updates the parent order:
```sql
UPDATE orders 
SET last_message_at = NOW(), updated_at = NOW() 
WHERE id = {order_id}
```

This allows sorting/filtering orders by recent activity.

### Soft-Deleted Orders

Cannot create messages on soft-deleted orders. Returns 404.

### No File Attachments

File attachments (`attachments` field in SPP) are **not supported** in the current implementation. This feature is deferred.

### Created_at Not Overridable

Unlike orders, messages do not support custom `created_at`. All messages are timestamped at actual creation time.

### Notification Side Effects (Deferred)

In SPP, creating a message may trigger notifications. This is **not implemented** in current version. Notifications are explicitly deferred.
