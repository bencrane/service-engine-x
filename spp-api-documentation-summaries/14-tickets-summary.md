# 14. Tickets - API Documentation Summary

## Overview
The Tickets API provides full CRUD operations for managing support tickets. Tickets facilitate communication between clients and staff, can be linked to orders, and support assignments, tags, and custom form data.

---

## 14.1 List All Tickets

### File Path
`spp-api-documentation/14. Tickets/14.1 list-tickets.md`

### Name
List all tickets

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/tickets`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Query Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| limit | integer | optional | Items per page | `10` |
| page | integer | optional | Page number | `1` |
| sort | string | optional | Sort by fields | `id:desc` |
| filters[number][$in][] | array | optional | Filter by ticket numbers | |

**Supported Filter Operators:** `$eq` (=), `$lt` (<), `$gt` (>), `$in` (in array)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

### Response Body Schema (200)
```json
{
  "data": [Ticket],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

#### Ticket Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | Ticket ID | `1` |
| subject | string | required | Ticket subject | `Ticket subject` |
| status | string | required | Ticket status | `Open` |
| source | string | required | Ticket source | `API` |
| user_id | integer | required | Client user ID | `1` |
| client | User | required | Client user object | |
| order_id | integer | required | Related order ID | `1` |
| form_data | object | required | Submitted form data | `{"field_1":"value_1"}` |
| tags | array[string] | required | Applied tags | |
| note | string | required | Internal note | `Ticket note` |
| employees | array[object] | required | Assigned staff | |
| created_at | string\<date-time\> | required | Created timestamp | |
| updated_at | string\<date-time\> | required | Updated timestamp | |
| last_message_at | string\<date-time\> | required | Last message timestamp | |
| date_closed | string\<date-time\> | required | Closed timestamp | |

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/tickets \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

---

## 14.2 Create a Ticket

### File Path
`spp-api-documentation/14. Tickets/14.2 create-ticket.md`

### Name
Create a ticket

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/tickets`

### Request Body Schema
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| user_id | integer | **required** | Client user ID | `1` |
| subject | string | **required** | Ticket subject | `Ticket subject` |
| status | integer | optional | Initial status ID | `1` |
| employees[] | array[integer] | optional | Assigned employee IDs | |
| tags[] | array[string] | optional | Tags to apply | |
| order | string | optional | Related order number | `123456` |
| metadata[] | array[string] | optional | Custom metadata | |
| note | string | optional | Internal note | `Ticket note` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |

### Response Body Schema (201)
Returns extended Ticket object with:
- All base ticket fields
- `messages` - Ticket messages array
- `order` - Full order object (if linked)
- `client` - Full client user object
- `metadata` - Custom metadata object

---

## 14.3 Retrieve a Ticket

### File Path
`spp-api-documentation/14. Tickets/14.3 retrieve-ticket.md`

### Name
Retrieve a ticket

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/tickets/{ticket}`

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
Returns extended Ticket object (same as create response)

---

## 14.4 Update a Ticket

### File Path
`spp-api-documentation/14. Tickets/14.4 update-ticket.md`

### Name
Update a ticket

### HTTP Method
`PUT`

### URL Path
`https://{workspaceUrl}/api/tickets/{ticket}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| ticket | string or allOf | **required** | Ticket ID or number | `E4A269FC` |

### Request Body Schema
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| subject | string | optional | Ticket subject | `Ticket subject` |
| status | integer | optional | Status ID | `1` |
| employees[] | array[integer] | optional | Assigned employee IDs | |
| tags[] | array[string] | optional | Tags | |
| order | string | optional | Related order number | `123456` |
| metadata[] | array[string] | optional | Metadata | |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |

---

## 14.5 Delete a Ticket

### File Path
`spp-api-documentation/14. Tickets/14.5 delete-ticket.md`

### Name
Delete a ticket

### HTTP Method
`DELETE`

### URL Path
`https://{workspaceUrl}/api/tickets/{ticket}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| ticket | string or allOf | **required** | Ticket ID or number | `E4A269FC` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 204 | No Content - Deleted |
| 401 | Unauthorized |
| 404 | Not Found |

### Side Effects / State Changes
- **Soft delete** - can be undone

---

## Ambiguities and Missing Information

1. **Status Values:** Integer status IDs not mapped to string status names
2. **Source Values:** Valid ticket source values not documented
3. **Ticket Numbers:** Format and generation of ticket numbers not documented
4. **Note vs Message:** Difference between internal note and messages unclear

---

## Cross-references

- TicketMessages (15. TicketMessages) - `messages` array
- Orders (7. Orders) - `order_id`, `order` object
- Tags (12. Tags) - `tags` array
- Team (13. Team) - `employees` array
- Clients (17. Clients) - `client`, `user_id`
- FilledFormFields (3. FilledFormFields) - `form_data`
