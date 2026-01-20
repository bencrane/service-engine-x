# 16. ClientActivities - API Documentation Summary

## Overview
The ClientActivities API provides CRUD operations for managing client activity/interaction tracking. Activities represent logged events or interactions associated with client users.

---

## 16.1 List All Client Activities

### File Path
`spp-api-documentation/16. ClientActivities/16.1 list-client-activities.md`

### Name
List all client activities

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/client_activities`

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
| filters[user_id][$eq] | integer | optional | Filter by user ID | `1` |

**Supported Filter Operators:** `$eq` (=), `$lt` (<), `$gt` (>), `$in` (in array)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

### Response Body Schema (200)
```json
{
  "data": [Activity],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

#### Activity Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | Activity ID | `1` |
| user_id | integer | required | Client user ID | `1` |
| type | string | required | Activity type | `call` |
| description | string | required | Activity description | `Follow-up call` |
| metadata | object | optional | Additional data | `{}` |
| created_at | string\<date-time\> | required | Created timestamp | |
| updated_at | string\<date-time\> | required | Updated timestamp | |

---

## 16.2 Create a Client Activity

### File Path
`spp-api-documentation/16. ClientActivities/16.2 create-client-activity.md`

### Name
Create a client activity

### HTTP Method
`POST`

### URL Path
`https://{workspaceUrl}/api/client_activities`

### Request Body Schema
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| user_id | integer | **required** | Client user ID | `1` |
| type | string | **required** | Activity type | `call` |
| description | string | optional | Activity description | `Follow-up call` |
| metadata | object | optional | Additional data | `{}` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |

### Response Body Schema (201)
Returns `Activity` object (see 16.1 for schema)

---

## 16.3 Retrieve a Client Activity

### File Path
`spp-api-documentation/16. ClientActivities/16.3 retrieve-client-activity.md`

### Name
Retrieve a client activity

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/client_activities/{activity}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| activity | integer | **required** | Activity ID | `1` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

---

## 16.4 Update a Client Activity

### File Path
`spp-api-documentation/16. ClientActivities/16.4 update-client-activity.md`

### Name
Update a client activity

### HTTP Method
`PUT`

### URL Path
`https://{workspaceUrl}/api/client_activities/{activity}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| activity | integer | **required** | Activity ID | `1` |

### Request Body Schema
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| type | string | optional | Activity type | `call` |
| description | string | optional | Activity description | `Updated description` |
| metadata | object | optional | Additional data | `{}` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |

---

## 16.5 Delete a Client Activity

### File Path
`spp-api-documentation/16. ClientActivities/16.5 delete-client-activity.md`

### Name
Delete a client activity

### HTTP Method
`DELETE`

### URL Path
`https://{workspaceUrl}/api/client_activities/{activity}`

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| activity | integer | **required** | Activity ID | `1` |

### Response Status Codes
| Code | Description |
|------|-------------|
| 204 | No Content - Deleted |
| 401 | Unauthorized |
| 404 | Not Found |

---

## Ambiguities and Missing Information

1. **Activity Types:** List of valid activity types not documented
2. **Metadata Structure:** Structure of metadata object not documented
3. **Delete Behavior:** Whether deletion is soft or hard delete not specified
4. **User Permissions:** What permissions are needed to view/manage activities

---

## Cross-references

- Clients (17. Clients) - `user_id` references client users
- Logs (5. Logs) - System-level activity logging vs client activities
