# 1. Tasks - API Documentation Summary

## Overview
The Tasks API provides endpoints for managing task completion status on orders. Tasks are associated with orders and can be marked as complete or incomplete.

---

## 1.1 Mark Task as Complete

### File Path
`spp-api-documentation/1. Tasks/1.1 mark-task-complete.md`

### Name
Mark task as complete

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/order_tasks/{task}/complete`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`
- **Description:** Provide your bearer token in the Authorization header when making requests to protected resources.

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier for support | `2024-03-05` |
| Accept | string | required | Response format | `application/json` |
| Content-Type | string | required | Request format | `application/json` |

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| task | integer or allOf | required | Task ID | `1` |

### Query Parameters
Not specified

### Request Body Schema
Not specified (no body required)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

### Response Body Schema
Not specified in documentation

### Example Request
```bash
curl --request POST \
  --url https://example.spp.co/api/order_tasks/{task}/complete \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'Content-Type: application/json' \
  --header 'X-Api-Version: '
```

### Example Response
Not provided

### Side Effects / State Changes
- Marks the specified task as complete
- Updates the task's completion status in the system

### Preconditions / Invariants
- Task must exist
- Task must be associated with an order
- User must have appropriate permissions

### Error Cases
| Code | Description |
|------|-------------|
| 401 | Authentication failed - invalid or missing bearer token |

### Notes / Gotchas
- The `X-Api-Version` header should be provided for support purposes
- Task ID can be integer or allOf type (documentation ambiguity)

### Cross-references
- Related to Order Tasks endpoints (9. OrderTasks)
- Tasks are associated with Orders (7. Orders)

---

## 1.2 Mark Task as Incomplete

### File Path
`spp-api-documentation/1. Tasks/1.2 mark-task-incomplete.md`

### Name
Mark task as incomplete

### HTTP Method
`DELETE`

### URL Path
`https://{workspaceUrl}/api/order_tasks/{task}/complete`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`
- **Description:** Provide your bearer token in the Authorization header when making requests to protected resources.

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier for support | `2024-03-05` |
| Accept | string | required | Response format | `application/json` |
| Content-Type | string | required | Request format | `application/json` |

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| task | integer or allOf | required | Task ID | `1` |

### Query Parameters
Not specified

### Request Body Schema
Not specified (no body required)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

### Response Body Schema
Not specified in documentation

### Example Request
```bash
curl --request DELETE \
  --url https://example.spp.co/api/order_tasks/{task}/complete \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'Content-Type: application/json' \
  --header 'X-Api-Version: '
```

### Example Response
Not provided

### Side Effects / State Changes
- Marks the specified task as incomplete
- Reverses completion status of the task

### Preconditions / Invariants
- Task must exist
- Task should be currently marked as complete
- User must have appropriate permissions

### Error Cases
| Code | Description |
|------|-------------|
| 401 | Authentication failed - invalid or missing bearer token |

### Notes / Gotchas
- Uses DELETE method on the same `/complete` endpoint (not a typical REST pattern)
- This effectively "deletes" the completion status rather than the task itself

### Cross-references
- Related to Order Tasks endpoints (9. OrderTasks)
- Inverse of 1.1 Mark Task as Complete

---

## Ambiguities and Missing Information

1. **Response Body Schema:** Neither endpoint documents the response body structure for successful (200) responses.
2. **Task Type:** The `task` parameter type is listed as "integer or allOf" which is ambiguous - unclear what "allOf" refers to.
3. **Error Response Bodies:** No documentation on the structure of error responses (401).
4. **Rate Limits:** No rate limiting information provided.
5. **Idempotency:** Not documented whether these operations are idempotent.
6. **404 Case:** No documentation on what happens if the task ID doesn't exist.
