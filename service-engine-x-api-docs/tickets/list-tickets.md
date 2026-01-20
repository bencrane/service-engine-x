# List Tickets

```
GET /api/tickets
```

---

## 1. Purpose

Retrieve a paginated list of tickets. Tickets are sorted by creation date in descending order by default.

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

None.

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | `20` | Items per page (1–100). |
| `page` | integer | No | `1` | Page number. |
| `sort` | string | No | `created_at:desc` | Sort field and direction. |
| `filters[field][$op]` | varies | No | — | Filter by field using operators: `$eq`, `$lt`, `$gt`, `$in`. |

**Supported filter fields:** `user_id`, `status`, `order_id`, `created_at`, `last_message_at`.

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
| `source` | Read-only | Ticket source (e.g., "API", "Dashboard") |
| `note` | Read-only | Internal note |
| `form_data` | Read-only | Form submission data (JSONB) |
| `metadata` | Read-only | Arbitrary metadata (JSONB) |
| `tags` | Read-only | Array of tag strings |
| `employees` | Read-only | Array of assigned employee objects |
| `client` | Read-only | Nested client object (joined) |
| `created_at` | Read-only | ISO 8601 timestamp |
| `updated_at` | Read-only | ISO 8601 timestamp |
| `last_message_at` | Read-only | Timestamp of last message; null if no messages |
| `date_closed` | Read-only | Timestamp when closed; null if open |

---

## 5. Side Effects

None.

---

## 6. Response Shape

### Success: 200 OK

```json
{
  "data": [
    {
      "id": "uuid",
      "subject": "Ticket subject",
      "user_id": "client-uuid",
      "order_id": "order-uuid-or-null",
      "status": "Open",
      "status_id": 1,
      "source": "API",
      "note": "Internal note",
      "form_data": {},
      "metadata": {},
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
        "address": { ... },
        "role": { ... }
      },
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T12:00:00Z",
      "last_message_at": "2024-01-15T11:30:00Z",
      "date_closed": null
    }
  ],
  "links": {
    "first": "/api/tickets?page=1&limit=20",
    "last": "/api/tickets?page=5&limit=20",
    "prev": null,
    "next": "/api/tickets?page=2&limit=20"
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "to": 20,
    "last_page": 5,
    "per_page": 20,
    "total": 100,
    "path": "/api/tickets"
  }
}
```

### Nested Objects

| Object | Inclusion | Notes |
|--------|-----------|-------|
| `client` | Always joined | Client who owns the ticket |
| `employees` | Always joined | Array; empty if none assigned |
| `tags` | Always included | Array; empty if no tags |
| `order` | Not included in list | Use retrieve for full order details |

---

## 7. Soft-Delete Visibility

**Soft-deleted tickets are excluded by default.**

- Tickets with `deleted_at IS NOT NULL` are not returned.
- No `include_deleted` parameter is supported.

---

## 8. Error Behavior

### 400 Bad Request

Invalid query parameters.

```json
{
  "message": "The given data was invalid.",
  "errors": {
    "limit": ["The limit must be between 1 and 100."]
  }
}
```

### 401 Unauthorized

Missing or invalid authentication token.

---

## 9. Notes / Edge Cases

### Filtering by status

Status filter uses integer values:

| Status | ID |
|--------|-----|
| Open | 1 |
| Pending | 2 |
| Closed | 3 |

Example: `filters[status][$eq]=1` for Open tickets.

### Filtering by order_id

- `filters[order_id][$eq]=uuid` — tickets for specific order
- Tickets without an order have `order_id: null`

### last_message_at

- Updated automatically when ticket messages are created
- Null if ticket has no messages
- Read-only; cannot be set via API
