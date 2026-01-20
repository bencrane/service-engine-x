# 9. OrderTasks - API Documentation Summary

## Overview
The OrderTasks API provides endpoints for managing tasks associated with orders. Tasks represent work items that need to be completed as part of order fulfillment. Tasks can be assigned to employees or clients and have configurable deadlines.

**Note:** No retrieve endpoint exists - tasks are retrieved via list or through the order object.

---

## 9.1 List All Tasks for an Order

### File Path
`spp-api-documentation/9. OrderTasks/9.1 list-order-tasks.md`

### Name
List all tasks for an order

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/order_tasks/{order}`

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
  "data": [Task],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

#### Task Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | Task ID | `1` |
| order_id | string | required | Order ID/number | `ABC12345` |
| name | string | required | Task name | `Design Logo` |
| description | string | required | Task description | `Create a new logo for the client` |
| sort_order | integer | required | Display order | `1` |
| is_public | boolean | required | Visible on client portal | `true` |
| for_client | boolean | required | Client can complete task | `false` |
| is_complete | boolean | required | Completion status | `false` |
| completed_by | integer | required | User ID who completed | `2` |
| completed_at | string\<date-time\> | required | Completion timestamp | `2024-01-01 15:00:00` |
| deadline | integer | required | Hours until deadline | `7` |
| due_at | string\<date-time\> | required | Specific due date | `2024-12-31 23:59:59` |

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/order_tasks/E4A269FC \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

### Example Response
```json
{
  "data": [
    {
      "id": 1,
      "order_id": "ABC12345",
      "name": "Design Logo",
      "description": "Create a new logo for the client",
      "sort_order": 1,
      "is_public": true,
      "for_client": false,
      "is_complete": false,
      "completed_by": 2,
      "completed_at": "2024-01-01 15:00:00",
      "deadline": 7,
      "due_at": "2024-12-31 23:59:59"
    }
  ],
  "links": {...},
  "meta": {...}
}
```

### Notes / Gotchas
- Tasks sorted by creation date in descending order
- `deadline` and `due_at` are mutually exclusive - use one or the other
- `deadline` is calculated from previous task completion or order creation

---

## 9.2 Create a Task for an Order

### File Path
`spp-api-documentation/9. OrderTasks/9.2 create-order-task.md`

### Name
Create a task for an order

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/order_tasks/{order}`

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
| name | string | **required** | Task name | `Design Logo` |
| description | string | optional | Task description | `Create a new logo for the client` |
| employee_ids | array[integer] | optional | Assigned employee IDs | `[1]` |
| sort_order | integer | optional | Display order | `1` |
| is_public | boolean | optional | Visible on client portal | `true` |
| for_client | boolean | optional | Client can complete (mutually exclusive with employee_ids) | `false` |
| deadline | integer | optional | Hours until deadline (mutually exclusive with due_at) | `7` |
| due_at | string\<date-time\> | optional | Specific due date (mutually exclusive with deadline) | `2024-12-31T23:59:59+00:00` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 201 | Created |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized |
| 404 | Not Found - Order doesn't exist |

### Response Body Schema (201)
Returns `Task` object (see 9.1 for schema)

### Example Request
```bash
curl --request POST \
  --url https://example.spp.co/api/order_tasks/E4A269FC \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'Content-Type: application/json' \
  --data '{
    "employee_ids": [1],
    "name": "Design Logo",
    "description": "Create a new logo for the client",
    "sort_order": 1,
    "is_public": true,
    "for_client": false,
    "deadline": 7
  }'
```

### Side Effects / State Changes
- Creates new task record
- May trigger notifications to assigned employees

### Notes / Gotchas
- `name` is the only required field
- `employee_ids` and `for_client` are mutually exclusive
- `deadline` and `due_at` are mutually exclusive
- `deadline` is in hours (use 24-hour increments for days)

---

## 9.3 Update a Task

### File Path
`spp-api-documentation/9. OrderTasks/9.3 update-order-task.md`

### Name
Update a task

### HTTP Method
`PUT`

### URL Path
`https://{workspaceUrl}/api/order_tasks/{task}`

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
| task | integer or allOf | **required** | Task ID | `1` |

### Request Body Schema
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| name | string | **required** | Task name | `Design Logo` |
| description | string | optional | Task description | `Create a new logo for the client` |
| employee_ids | array[integer] | optional | Assigned employee IDs | `[1]` |
| sort_order | integer | optional | Display order | `1` |
| is_public | boolean | optional | Visible on client portal | `true` |
| for_client | boolean | optional | Client can complete | `false` |
| deadline | integer | optional | Hours until deadline | `7` |
| due_at | string\<date-time\> | optional | Specific due date | `2024-12-31T23:59:59+00:00` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized |
| 404 | Not Found - Task doesn't exist |

### Response Body Schema (200)
Returns updated `Task` object (see 9.1 for schema)

### Example Request
```bash
curl --request PUT \
  --url https://example.spp.co/api/order_tasks/1 \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "Design Logo Updated",
    "description": "Updated description",
    "is_complete": true
  }'
```

### Notes / Gotchas
- Update uses task ID (not order ID)
- `name` is required even for partial updates
- Cannot change `order_id` after creation

---

## 9.4 Delete a Task

### File Path
`spp-api-documentation/9. OrderTasks/9.4 delete-order-task.md`

### Name
Delete a task

### HTTP Method
`DELETE`

### URL Path
`https://{workspaceUrl}/api/order_tasks/{task}`

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
| task | integer or allOf | **required** | Task ID | `1` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 204 | No Content - Deleted |
| 401 | Unauthorized |
| 404 | Not Found - Task doesn't exist |

### Response Body Schema
No body (204)

### Example Request
```bash
curl --request DELETE \
  --url https://example.spp.co/api/order_tasks/1 \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

### Side Effects / State Changes
- **PERMANENT** deletion - cannot be undone

### Notes / Gotchas
- **WARNING:** Hard delete - cannot be undone
- Delete uses task ID (not order ID)

---

## Task Completion via Tasks API

**Note:** To mark tasks as complete/incomplete, use the Tasks API (Section 1):
- `PUT /api/tasks/{task}/complete` - Mark complete
- `PUT /api/tasks/{task}/incomplete` - Mark incomplete

---

## Ambiguities and Missing Information

1. **No Retrieve Endpoint:** Individual task retrieval not available
2. **Completion via Update:** Whether `is_complete` can be set via update endpoint unclear
3. **Deadline Calculation:** Exact calculation of deadline from previous task not documented
4. **Employee Assignment:** How employee notifications work not documented
5. **Task Templates:** Whether tasks can be templated from services not documented
6. **Duplicate Names:** Whether duplicate task names are allowed not documented

---

## Cross-references

- Tasks (1. Tasks) - Mark complete/incomplete operations
- Orders (7. Orders) - Tasks belong to orders
- Team (13. Team) - `employee_ids` references team members
- Clients (17. Clients) - `for_client` allows client completion
