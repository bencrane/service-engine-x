# 15. TicketMessages - API Documentation Summary

## Overview
The TicketMessages API provides endpoints for managing messages on tickets. Similar to OrderMessages, this API supports listing, creating, and deleting messages for ticket-based communication.

**Note:** No update endpoint exists - messages cannot be edited after creation.

---

## 15.1 List All Messages for a Ticket

### File Path
`spp-api-documentation/15. TicketMessages/15.1 list-ticket-messages.md`

### Name
List all messages for a ticket

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/ticket_messages/{ticket}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| ticket | string or allOf | **required** | Ticket ID or number | `E4A269FC` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

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

### Notes / Gotchas
- Messages sorted by creation date in descending order
- `staff_only: true` messages are internal notes not visible to clients
- **Note:** 15.1 list-ticket-messages.md appears to be empty in source documentation

---

## 15.2 Create a Message for a Ticket

### File Path
`spp-api-documentation/15. TicketMessages/15.2 create-ticket-message.md`

### Name
Create a message for a ticket

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/ticket_messages/{ticket}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| ticket | string or allOf | **required** | Ticket ID or number | `E4A269FC` |

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
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |

### Response Body Schema (201)
Returns `Message` object (see 15.1 for schema)

### Side Effects / State Changes
- Creates new message record
- Updates ticket's `last_message_at` timestamp
- May trigger notification to client (if not staff_only)
- May trigger notification to assigned employees

---

## 15.3 Delete a Message

### File Path
`spp-api-documentation/15. TicketMessages/15.3 delete-ticket-message.md`

### Name
Delete a message

### HTTP Method
`DELETE`

### URL Path
`https://{workspaceUrl}/api/ticket_messages/{message}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| message | MessagePathIdentifier | **required** | Message ID | `123` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 204 | No Content - Deleted |
| 401 | Unauthorized |
| 404 | Not Found |

### Side Effects / State Changes
- **PERMANENT** deletion - cannot be undone
- Associated file attachments may also be deleted

### Notes / Gotchas
- **WARNING:** Hard delete - cannot be undone
- Delete uses message ID, not ticket ID
- Different URL pattern than list/create

---

## Ambiguities and Missing Information

1. **Empty Source File:** 15.1 list-ticket-messages.md appears to be empty
2. **No Update Endpoint:** Messages cannot be edited after creation
3. **Attachments Format:** Exact format for uploading attachments not documented
4. **Notification Triggers:** When exactly notifications are sent not documented

---

## Cross-references

- Tickets (14. Tickets) - Messages belong to tickets
- OrderMessages (8. OrderMessages) - Similar API for order messages
- Clients (17. Clients) - `user_id` references users
- Team (13. Team) - Staff users can create internal notes
