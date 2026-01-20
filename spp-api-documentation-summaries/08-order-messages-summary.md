# 8. OrderMessages - API Documentation Summary

## Overview
The OrderMessages API provides endpoints for managing messages on orders. Messages facilitate communication between staff and clients about specific orders. This API supports listing, creating, and deleting messages.

**Note:** No update endpoint exists - messages cannot be edited after creation.

---

## 8.1 List All Messages for an Order

### File Path
`spp-api-documentation/8. OrderMessages/8.1 list-order-messages.md`

### Name
List all messages for an order

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/order_messages/{order}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| order | string or allOf | **required** | Order ID or number | `E4A269FC` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found - Order doesn't exist |

### Response Body Schema (200)
```json
{
  "data": [Message],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

#### Message Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | Message ID | `1` |
| user_id | integer | required | Author user ID | `1` |
| created_at | string\<date-time\> | required | Creation timestamp | `2021-09-01T00:00:00+00:00` |
| message | string | required | Message content | `Message` |
| staff_only | boolean | required | Internal note flag | `false` |
| files | array[string] | required | Attachment URLs | |
| order | Order | required | Associated order object | |
| ticket | Ticket | required | Associated ticket (if any) | |

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/order_messages/E4A269FC \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'X-Api-Version: 2024-03-05'
```

### Notes / Gotchas
- Messages sorted by creation date in descending order (most recent first)
- Response includes full order and ticket objects (if ticket exists)
- `staff_only: true` messages are internal notes not visible to clients

---

## 8.2 Create a Message for an Order

### File Path
`spp-api-documentation/8. OrderMessages/8.2 create-order-message.md`

### Name
Create a message for an order

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/order_messages/{order}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |
| Content-Type | string | required | Request format | `application/json` |

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| order | string or allOf | **required** | Order ID or number | `E4A269FC` |

### Request Body Schema
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| message | string | **required** | Message content | `Hello world!` |
| user_id | integer | optional | Author user ID (defaults to authenticated user) | `1` |
| staff_only | boolean | optional | Mark as internal note | `false` |
| attachments | array[binary] | optional | File attachments | |

### Response Status Codes
| Code | Description |
|------|-------------|
| 201 | Created |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized |
| 404 | Not Found - Order doesn't exist |

### Response Body Schema (201)
Returns `Message` object (see 8.1 for schema)

### Example Request
```bash
curl --request POST \
  --url https://example.spp.co/api/order_messages/E4A269FC \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'Content-Type: application/json' \
  --data '{
    "message": "Hello world!",
    "staff_only": false
  }'
```

### Side Effects / State Changes
- Creates new message record
- Updates order's `last_message_at` timestamp
- May trigger notification to client (if not staff_only)
- May trigger notification to assigned employees

### Notes / Gotchas
- `user_id` defaults to authenticated user if not specified
- `staff_only: true` creates internal note not visible to clients
- Attachments should be sent as binary data (multipart/form-data)
- `files` in response contains URLs to uploaded attachments

---

## 8.3 Delete a Message

### File Path
`spp-api-documentation/8. OrderMessages/8.3 delete-order-message.md`

### Name
Delete a message

### HTTP Method
`DELETE`

### URL Path
`https://{workspaceUrl}/api/order_messages/{message}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| message | MessagePathIdentifier | **required** | Message ID | `123` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 204 | No Content - Deleted |
| 401 | Unauthorized |
| 404 | Not Found - Message doesn't exist |

### Response Body Schema
No body (204)

### Example Request
```bash
curl --request DELETE \
  --url https://example.spp.co/api/order_messages/123 \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

### Side Effects / State Changes
- **PERMANENT** deletion - cannot be undone
- Associated file attachments may also be deleted

### Notes / Gotchas
- **WARNING:** This is a hard delete - cannot be undone
- Delete uses message ID, not order ID
- Different URL pattern than list/create (message ID instead of order ID)

---

## Ambiguities and Missing Information

1. **No Update Endpoint:** Messages cannot be edited after creation
2. **Attachments Format:** Exact format for uploading attachments not documented (likely multipart/form-data)
3. **File Storage:** How files are stored and URL format not documented
4. **Message Path Identifier:** Type `MessagePathIdentifier` not fully defined
5. **Notification Triggers:** When exactly notifications are sent not documented
6. **Permission Requirements:** What permissions are needed to delete messages not documented

---

## Cross-references

- Orders (7. Orders) - Messages belong to orders
- Tickets (14. Tickets) - Messages can be associated with tickets
- TicketMessages (15. TicketMessages) - Similar API for ticket messages
- Clients (17. Clients) - `user_id` references client users
- Team (13. Team) - Staff users can create internal notes
