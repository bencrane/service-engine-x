# 7. Orders - API Documentation Summary

## Overview
The Orders API provides full CRUD operations for managing orders. Orders represent purchased services and contain comprehensive information about clients, pricing, status, and associated entities like invoices and subscriptions.

**Key Concept:** List endpoints return `IndexOrder` objects (simplified), while Retrieve returns full `Order` objects with extended details.

---

## 7.1 List All Orders

### File Path
`spp-api-documentation/7. Orders/7.1 list-orders.md`

### Name
List all orders

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/orders`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |

### Query Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| limit | integer | optional | Items per page | `10` |
| page | integer | optional | Page number | `1` |
| sort | string | optional | Sort by fields | `id:desc` |
| filters[user_id][$in][] | array[integer] | optional | Filter by user IDs | |
| filters[status][$eq] | string | optional | Filter by status | |

**Supported Filter Operators:** `$eq` (=), `$lt` (<), `$gt` (>), `$in` (in array)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

### Response Headers
| Header | Type | Description |
|--------|------|-------------|
| X-Api-Identifier | string | Unique request identifier for support |
| X-Api-Version | string | API version used |

### Response Body Schema (200)
```json
{
  "data": [IndexOrder],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

#### IndexOrder Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | Order ID | `1` |
| created_at | string\<date-time\> | required | Created timestamp | `2021-09-01T00:00:00+00:00` |
| updated_at | string\<date-time\> | required | Updated timestamp | |
| last_message_at | string\<date-time\> | required | Last message timestamp | |
| date_started | string\<date-time\> | required | Work start date | |
| date_completed | string\<date-time\> | required | Completion date | |
| date_due | string\<date-time\> | required | Due date | |
| client | User | required | Client user object | |
| tags | array[string] | required | Tags | `["tag1"]` |
| status | string | required | Order status | `Unpaid` |
| price | number | required | Order price | `100` |
| quantity | integer | required | Order quantity | `1` |
| invoice_id | integer | required | Associated invoice ID | `1` |
| service | string | required | Service name | `Service name` |
| service_id | integer | required | Service ID | `1` |
| user_id | integer | required | Client user ID | `1` |
| employees | array[object] | required | Assigned employees | |
| note | string | required | Internal note | `Note` |
| form_data | object | required | Submitted form data | `{}` |
| paysys | string | required | Payment system | `Stripe` |

#### Employee Object (in employees array)
| Field | Type | Description |
|-------|------|-------------|
| id | integer | User ID |
| name_f | string | First name |
| name_l | string | Last name |
| group_id | integer | Group ID |
| role_id | integer | Role ID |

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/orders \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'X-Api-Version: 2024-03-05'
```

### Notes / Gotchas
- Returns `IndexOrder` (simplified) - use Retrieve for full details
- Orders sorted by creation date in descending order (most recent first)
- Client object includes full user details with role and address

---

## 7.2 Create an Order

### File Path
`spp-api-documentation/7. Orders/7.2 create-order.md`

### Name
Create an order

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/orders`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |
| Content-Type | string | required | Request format | `application/json` |

### Request Body Schema
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| user_id | integer | **required** | Client user ID | `1` |
| service_id | integer | conditional | Service ID | `1` |
| service | string | conditional | Order title (required if no service_id) | `Instagram Followers` |
| status | integer | optional | Status ID | `1` |
| employees[] | array[integer] | optional | Assigned employee IDs | |
| created_at | string\<date-time\> | optional | Creation date | `2021-09-01T00:00:00+00:00` |
| date_started | string\<date-time\> | optional | Start date | |
| date_completed | string\<date-time\> | optional | Completion date | |
| date_due | string\<date-time\> | optional | Due date | |
| tags[] | array[string] | optional | Tags | |
| metadata[] | array[string] | optional | Custom metadata | |
| note | string | optional | Internal note | `Some note` |
| number | string | optional | Custom order number | `B1C2D3E4F5` |

**Note:** Either `service_id` OR `service` must be provided.

### Response Status Codes
| Code | Description |
|------|-------------|
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |

### Response Body Schema (201)
Returns extended Order object with:
- All IndexOrder fields
- `currency` - Currency code
- `subscription` - Subscription details (if recurring)
- `options` - Selected service options
- `invoice` - Full invoice object
- `order_service` - Full service object
- `addons` - Service addons
- `ratings` - Client ratings
- `messages` - Order messages
- `metadata` - Custom metadata

### Side Effects / State Changes
- Creates new order record
- May create associated invoice
- May trigger notifications

### Notes / Gotchas
- `user_id` is the only strictly required field
- Either `service_id` or `service` name must be provided
- Custom order number can be specified via `number` field

---

## 7.3 Retrieve an Order

### File Path
`spp-api-documentation/7. Orders/7.3 retrieve-order.md`

### Name
Retrieve an order

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/orders/{order}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| order | string or allOf | **required** | Order ID or number | `E4A269FC` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

### Response Body Schema (200)
Returns extended Order object with all related entities:

#### Extended Order Fields
| Field | Type | Description |
|-------|------|-------------|
| currency | string | Currency code (e.g., `USD`) |
| subscription | Subscription | Subscription details |
| options | object | Selected service options |
| invoice | Invoice | Full invoice object |
| order_service | Service | Full service object |
| addons | array[object] | Service addons |
| ratings | array[Rating] | Client ratings |
| messages | array[Message] | Order messages |
| metadata | object | Custom metadata |

#### Subscription Object
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Subscription ID |
| number | string | Subscription number |
| status | string | Status (e.g., `Active`) |
| processor_id | string | Stripe subscription ID |
| current_period_end | string\<date-time\> | Current billing period end |
| payments | array[object] | Payment history |
| orders | array[string] | Associated order numbers |
| payment_count | integer | Total payments made |

#### Message Object
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Message ID |
| user_id | integer | Author user ID |
| created_at | string\<date-time\> | Timestamp |
| message | string | Message content |
| staff_only | boolean | Internal note flag |
| files | array[string] | Attachments |

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/orders/E4A269FC \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

### Notes / Gotchas
- Can use order ID (integer) or order number (string)
- Returns full Order object with all nested entities
- More detailed than List endpoint response

---

## 7.4 Update an Order

### File Path
`spp-api-documentation/7. Orders/7.4 update-order.md`

### Name
Update an order

### HTTP Method
`PUT`

### URL Path
`https://{workspaceUrl}/api/orders/{order}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| order | string or allOf | **required** | Order ID or number | `E4A269FC` |

### Request Body Schema
Partial update supported - only provided fields are changed.

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| status | integer | optional | Status ID | `1` |
| employees[] | array[integer] | optional | Assigned employee IDs | |
| created_at | string\<date-time\> | optional | Creation date | |
| date_started | string\<date-time\> | optional | Start date | |
| date_completed | string\<date-time\> | optional | Completion date | |
| date_due | string\<date-time\> | optional | Due date | |
| service_id | integer | optional | Service ID | `1` |
| tags[] | array[string] | optional | Tags | |
| form_data[] | array[string] | optional | Form data | |
| metadata[] | array[string] | optional | Metadata | |
| note | string | optional | Internal note | `Some note` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |

### Response Body Schema (200)
Returns updated Order object (same as Retrieve)

### Side Effects / State Changes
- Updates order record
- Updates `updated_at` timestamp
- May trigger status change notifications

### Notes / Gotchas
- Partial update - only provided fields change
- Cannot change `user_id` (client) after creation
- `status` is integer ID, not string

---

## 7.5 Delete an Order

### File Path
`spp-api-documentation/7. Orders/7.5 delete-order.md`

### Name
Delete an order

### HTTP Method
`DELETE`

### URL Path
`https://{workspaceUrl}/api/orders/{order}`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| order | string or allOf | **required** | Order ID or number | `E4A269FC` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 204 | No Content - Deleted |
| 401 | Unauthorized |
| 404 | Not Found |

### Response Body Schema
No body (204)

### Example Request
```bash
curl --request DELETE \
  --url https://example.spp.co/api/orders/E4A269FC \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

### Side Effects / State Changes
- Soft deletes order (can be undone)

### Notes / Gotchas
- **Soft delete** - deletion can be undone
- Associated invoice/subscription may remain

---

## Common Nested Objects

### User Object (Client)
| Field | Type | Description |
|-------|------|-------------|
| id | integer | User ID |
| name | string | Full name |
| name_f | string | First name |
| name_l | string | Last name |
| email | string | Email address |
| company | string | Company name |
| tax_id | string | Tax ID |
| phone | string | Phone number |
| address | Address | Full address object |
| note | string | Internal note |
| balance | number | Account balance |
| spent | string | Total spent |
| optin | string | Marketing consent |
| stripe_id | string | Stripe customer ID |
| custom_fields | object | Custom field data |
| status | integer | Account status |
| role_id | integer | Role ID |
| role | Role | Full role object |
| aff_id | integer | Affiliate ID |
| aff_link | string | Affiliate link |

### Address Object
| Field | Type | Description |
|-------|------|-------------|
| line_1 | string | Address line 1 |
| line_2 | string | Address line 2 |
| city | string | City |
| state | string | State/Province |
| country | string | Country code |
| postcode | string | Postal code |
| name_f | string | First name |
| name_l | string | Last name |
| tax_id | string | Tax ID |
| company_name | string | Company name |
| company_vat | string | Company VAT |

### Role Object
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Role ID |
| name | string | Role name (e.g., `Administrator`) |
| dashboard_access | integer | Dashboard access level (0-3) |
| order_access | integer | Order access level |
| order_management | integer | Order management level |
| ticket_access | integer | Ticket access level |
| ticket_management | integer | Ticket management level |
| invoice_access | integer | Invoice access level |
| invoice_management | integer | Invoice management level |
| clients | integer | Clients permission |
| services | integer | Services permission |
| ... | ... | Various settings_* permissions |

**Permission Levels:** 0=None, 1=Own, 2=Group, 3=All

---

## Ambiguities and Missing Information

1. **Status Values:** Integer status IDs not mapped to string status names
2. **Service vs Service ID:** Interaction between `service` (string name) and `service_id` when both provided
3. **Form Data Format:** Structure of `form_data` object not fully documented
4. **Metadata Format:** Structure and allowed values for `metadata` not documented
5. **Pagination on Single Resources:** Pagination links appear on retrieve/update docs (likely documentation error)
6. **Order Number Generation:** How auto-generated order numbers work not documented

---

## Cross-references

- Invoices (4. Invoices) - `invoice_id`, `invoice` object
- OrderMessages (8. OrderMessages) - `messages` array
- OrderTasks (9. OrderTasks) - Tasks associated with orders
- Services (10. Services) - `service_id`, `order_service` object
- Subscriptions (11. Subscriptions) - `subscription` object
- Tags (12. Tags) - `tags` array
- Clients (17. Clients) - `client`, `user_id`
