# 12. Tags - API Documentation Summary

## Overview
The Tags API provides read-only access to tags used for categorization of orders, tickets, and other entities. Tags are managed through the admin UI, not the API.

**Note:** No create, update, or delete endpoints exist - tags are read-only via API.

---

## 12.1 List All Tags

### File Path
`spp-api-documentation/12. Tags/12.1 list-tags.md`

### Name
List all tags

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/tags`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |

### Query Parameters
None documented (likely doesn't support pagination/filtering)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

### Response Body Schema (200)
Returns array of Tag objects (not paginated wrapper)

```json
[Tag]
```

#### Tag Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | Tag ID | `1` |
| name | string | required | Tag name | `Tag name` |
| created_at | string\<date-time\> | required | Created timestamp | `2021-09-01T00:00:00+00:00` |
| updated_at | string\<date-time\> | required | Updated timestamp | `2021-09-01T00:00:00+00:00` |

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/tags \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123'
```

### Example Response
```json
[
  {
    "id": 1,
    "name": "Tag name",
    "created_at": "2021-09-01T00:00:00+00:00",
    "updated_at": "2021-09-01T00:00:00+00:00"
  }
]
```

### Notes / Gotchas
- Tags sorted by creation date in descending order
- Response is a simple array, not paginated wrapper
- Tags are read-only via API - manage through admin UI

---

## Ambiguities and Missing Information

1. **No CRUD Operations:** Only list endpoint exists
2. **No Pagination:** Response is simple array
3. **No Filtering:** Cannot filter tags
4. **Tag Usage:** How tags are applied to entities not documented here
5. **Tag Colors/Categories:** No additional metadata documented

---

## Cross-references

- Orders (7. Orders) - Orders have `tags` array
- Tickets (14. Tickets) - Tickets have `tags` array
- Clients (17. Clients) - Clients may have tags
