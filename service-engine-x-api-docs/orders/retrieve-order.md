# Retrieve Order

```
GET /api/orders/{id}
```

---

## 1. Purpose

Retrieve a single order by ID. Returns the **full order object** with all related data including messages, invoice, subscription, and service details.

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
| `id` | UUID | **Yes** | Order identifier. |

### Request Headers

| Header | Type | Required |
|--------|------|----------|
| `Authorization` | string | Yes |
| `Accept` | string | Yes (`application/json`) |
| `X-Api-Version` | string | No |

---

## 4. Side Effects

None. Read-only operation.

---

## 5. Response Shape

### 200 OK

Returns full order object with all relations.

```json
{
  "id": "uuid",
  "number": "ORD-ABC123",
  "created_at": "2024-01-15T10:30:00+00:00",
  "updated_at": "2024-01-15T10:30:00+00:00",
  "last_message_at": "2024-01-16T14:22:00+00:00",
  "date_started": "2024-01-15T10:30:00+00:00",
  "date_completed": null,
  "date_due": "2024-01-22T10:30:00+00:00",
  "client": { ... },
  "tags": ["priority", "vip"],
  "status": "In Progress",
  "price": "299.00",
  "quantity": 1,
  "invoice_id": "uuid-or-null",
  "service": "Monthly SEO Package",
  "service_id": "uuid-or-null",
  "user_id": "uuid",
  "employees": [ ... ],
  "note": "Internal note",
  "form_data": { "field1": "value1" },
  "paysys": "Stripe",
  "currency": "USD",
  "metadata": { "source": "api" },
  "subscription": { ... } | null,
  "invoice": { ... } | null,
  "order_service": { ... } | null,
  "messages": [ ... ],
  "options": {}
}
```

### Response Fields (Extended Order)

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | UUID | No | Order identifier |
| `number` | string | No | Order number |
| `created_at` | datetime | No | Creation timestamp |
| `updated_at` | datetime | No | Last update timestamp |
| `last_message_at` | datetime | Yes | Last message timestamp |
| `date_started` | datetime | Yes | Work start date |
| `date_completed` | datetime | Yes | Completion date |
| `date_due` | datetime | Yes | Due date |
| `client` | object | No | Full client object |
| `tags` | array[string] | No | Tag names |
| `status` | string | No | Status display value |
| `price` | string | No | Order price (snapshot) |
| `quantity` | integer | No | Order quantity |
| `invoice_id` | UUID | Yes | Linked invoice |
| `service` | string | No | Service name (snapshot) |
| `service_id` | UUID | Yes | Service reference |
| `user_id` | UUID | No | Client reference |
| `employees` | array | No | Assigned employees |
| `note` | string | Yes | Internal note |
| `form_data` | object | No | Form field values |
| `paysys` | string | Yes | Payment system |
| `currency` | string | No | Currency (snapshot) |
| `metadata` | object | No | Custom metadata |
| `subscription` | object | Yes | Linked subscription (if recurring) |
| `invoice` | object | Yes | Full invoice object |
| `order_service` | object | Yes | Full service object (live, not snapshot) |
| `messages` | array | No | Order messages |
| `options` | object | No | Selected options |

### Embedded Objects

| Object | Included | Notes |
|--------|----------|-------|
| `client` | Always | Full client with address, role |
| `employees` | Always | Array of assigned employees |
| `subscription` | If exists | Linked subscription details |
| `invoice` | If exists | Full invoice with items, billing address |
| `order_service` | If `service_id` valid | **Live** service object (not snapshot) |
| `messages` | Always | Array of order messages |

---

## 6. Field Semantics

| Field | Semantics | Notes |
|-------|-----------|-------|
| `id` | Read-only | |
| `number` | Read + Write | |
| `created_at` | Read + Write | |
| `updated_at` | Read-only | |
| `last_message_at` | Read-only | Auto-managed |
| `date_started` | Read + Write | |
| `date_completed` | Read + Write | |
| `date_due` | Read + Write | |
| `client` | Read-only (joined) | Live reference |
| `tags` | Write-only input, Read-only output | **Full replacement** on write; returned as string array |
| `status` | Read + Write | Integer stored (default `0` = Unpaid), string returned |
| `price` | Read-only | **Snapshot** at creation |
| `quantity` | Read + Write | |
| `invoice_id` | Read-only | Set via invoice creation |
| `service` | Read-only | **Snapshot** (`service_name`) |
| `service_id` | Read + Write | |
| `user_id` | Read + Write | |
| `employees` | Write-only input, Read-only output | **Full replacement** on write; returned as joined array |
| `note` | Read + Write | |
| `form_data` | Read + Write | |
| `paysys` | Read-only | |
| `currency` | Read-only | **Snapshot** at creation |
| `metadata` | Read + Write | |
| `subscription` | Read-only (joined) | Live reference |
| `invoice` | Read-only (joined) | Live reference |
| `order_service` | Read-only (joined) | Live reference (current service state) |
| `messages` | Read-only (joined) | Managed via OrderMessages API |
| `options` | Read-only | Selected service options |

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

Order does not exist or is soft-deleted.

```json
{
  "error": "Not Found"
}
```

**Causes:**
- Invalid UUID format
- UUID does not match any order
- Order has been soft-deleted (`deleted_at IS NOT NULL`)

**Note:** 400 and 409 are not applicable to retrieve endpoints.

---

## 8. Notes / Edge Cases

### Soft-Delete Visibility

- Soft-deleted orders (`deleted_at IS NOT NULL`) return **404 Not Found**
- There is **no `include_deleted` parameter** — soft-deleted orders cannot be retrieved via this endpoint
- To access deleted orders, direct database query is required

### Snapshot vs Live Data

| Field | Type | Updates When Service Changes? |
|-------|------|-------------------------------|
| `service` | Snapshot | No — captured at order creation |
| `price` | Snapshot | No — captured at order creation |
| `currency` | Snapshot | No — captured at order creation |
| `order_service` | Live | Yes — shows current service state |

The `order_service` object is a **live reference** to the current service record. If the service has been updated, `order_service` reflects the new values while `service`, `price`, and `currency` retain original values.

If the service has been soft-deleted, `order_service` may be `null` even though `service_id` is set.

### IndexOrder vs Extended Order

| Endpoint | Returns | Includes |
|----------|---------|----------|
| `GET /api/orders` | IndexOrder | Basic fields, client, employees, tags |
| `GET /api/orders/{id}` | Extended Order | All above + subscription, invoice, order_service, messages, metadata, currency, options |

### Messages

Messages are embedded in the response as an array:

```json
{
  "messages": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "created_at": "2024-01-16T14:22:00+00:00",
      "message": "Work has started",
      "staff_only": false
    }
  ]
}
```

To manage messages, use the OrderMessages API endpoints.

### Invoice Embedding

If `invoice_id` is set, the full invoice object is embedded:
- Includes invoice items
- Includes billing address (snapshot)
- Includes payment status

### Subscription Embedding

If order is recurring, subscription object includes:
- Current period end
- Payment count
- Processor ID
- Status
