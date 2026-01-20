# Retrieve Ticket

```
GET /api/tickets/{id}
```

---

## 1. Purpose

Retrieve a single ticket by ID, including nested client, order, employees, and messages.

---

## 2. Authorization

Requires Bearer token in the `Authorization` header.

```
Authorization: Bearer {token}
```

**Permission required:** Authenticated user with `ticket_access` permission.

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

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | UUID |
| `subject` | Read-only | Ticket subject |
| `user_id` | Read-only | Client UUID |
| `order_id` | Read-only | Optional; null if no linked order |
| `status` | Read-only | String (mapped from integer) |
| `status_id` | Read-only | Raw integer status |
| `source` | Read-only | Ticket source |
| `note` | Read-only | Internal note |
| `form_data` | Read-only | Form submission data |
| `metadata` | Read-only | Arbitrary metadata |
| `tags` | Read-only | Array of tag strings |
| `employees` | Read-only | Array of assigned employee objects |
| `client` | Read-only | Nested client object (joined) |
| `order` | Read-only | Nested order object if linked; null otherwise |
| `messages` | Read-only | Array of ticket messages (joined) |
| `created_at` | Read-only | ISO 8601 timestamp |
| `updated_at` | Read-only | ISO 8601 timestamp |
| `last_message_at` | Read-only | Timestamp of last message |
| `date_closed` | Read-only | Timestamp when closed |

---

## 5. Side Effects

None.

---

## 6. Response Shape

### Success: 200 OK

```json
{
  "id": "ticket-uuid",
  "subject": "Ticket subject",
  "user_id": "client-uuid",
  "order_id": "order-uuid-or-null",
  "status": "Open",
  "status_id": 1,
  "source": "Dashboard",
  "note": "Internal note",
  "form_data": { "field_1": "value_1" },
  "metadata": { "key": "value" },
  "tags": ["tag1", "tag2"],
  "employees": [
    {
      "id": "employee-uuid",
      "name_f": "John",
      "name_l": "Doe",
      "role_id": "role-uuid"
    }
  ],
  "client": {
    "id": "client-uuid",
    "name": "Jane Smith",
    "name_f": "Jane",
    "name_l": "Smith",
    "email": "jane@example.com",
    "company": "Acme Inc.",
    "phone": "555-1234",
    "address": {
      "line_1": "123 Main St",
      "city": "New York",
      "state": "NY",
      "postcode": "10001",
      "country": "US"
    },
    "balance": 0,
    "role": { "id": "role-uuid", "name": "Client" }
  },
  "order": {
    "id": "order-uuid",
    "status": "In Progress",
    "service": "Service Name",
    "price": 100.00,
    "quantity": 1,
    "created_at": "2024-01-10T08:00:00Z"
  },
  "messages": [
    {
      "id": "message-uuid",
      "user_id": "sender-uuid",
      "message": "Message content",
      "staff_only": false,
      "files": [],
      "created_at": "2024-01-15T11:30:00Z"
    }
  ],
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z",
  "last_message_at": "2024-01-15T11:30:00Z",
  "date_closed": null
}
```

### Nested Objects

| Object | Inclusion | Notes |
|--------|-----------|-------|
| `client` | Always joined | Full client object |
| `employees` | Always joined | Array; empty if none assigned |
| `tags` | Always included | Array; empty if no tags |
| `order` | Joined if `order_id` not null | Full order object or null |
| `messages` | Always joined | Array of all ticket messages |

---

## 7. Soft-Delete Visibility

**Soft-deleted tickets return 404.**

Tickets with `deleted_at IS NOT NULL` are not retrievable.

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

Ticket does not exist or has been soft-deleted.

```json
{
  "error": "Not Found"
}
```

---

## 9. Notes / Edge Cases

### Optional order

If `order_id` is null, the `order` field in the response is `null`.

### Messages visibility

All messages are returned, including `staff_only` messages. Access control for `staff_only` visibility should be handled at the application layer.

### last_message_at

Reflects the `created_at` timestamp of the most recent message. Updated automatically; cannot be set via API.
