# 5. Logs - API Documentation Summary

## Overview
The Logs API provides read-only access to system activity logs. Logs track events and changes made to various entities in the system.

---

## 5.1 List All Logs

### File Path
`spp-api-documentation/5. Logs/5.1 list-logs.md`

### Name
List all logs

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/logs`

### Auth Requirements
- **Type:** Bearer Token
- **Header:** `Authorization: Bearer {token}`

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |

### Query Parameters
Not specified in documentation (likely supports standard pagination: `limit`, `page`, `sort`)

### Path Parameters
None

### Request Body Schema
Not applicable (GET request)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

### Response Body Schema (200)
```json
{
  "data": [Log],
  "links": PaginationLinks,
  "meta": PaginationMeta
}
```

#### Log Object
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| id | integer | required | Log ID | `1` |
| time | string\<date-time\> | required | Event timestamp | `2021-08-26T14:55:23.000000Z` |
| loggable_type | string | required | Type of entity logged | `App\Models\OnboardingForm` |
| loggable_id | integer | required | ID of entity logged | `1` |
| user_id | integer or null | required | User who triggered event | `1` |
| owner_id | integer or null | required | Owner ID | `1` |
| event | string | required | Event type | `created` |
| data | string | required | JSON string of change data | `{"old":null,"new":"test"}` |
| created_at | string\<date-time\> | required | Created timestamp | `2021-08-26T14:55:23.000000Z` |
| updated_at | string\<date-time\> | required | Updated timestamp | `2021-08-26T14:55:23.000000Z` |

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/logs \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'X-Api-Version: 2024-03-05'
```

### Example Response
```json
{
  "data": [
    {
      "id": 1,
      "time": "2021-08-26T14:55:23.000000Z",
      "loggable_type": "App\\Models\\OnboardingForm",
      "loggable_id": 1,
      "user_id": 1,
      "owner_id": 1,
      "event": "created",
      "data": "{\"old\":null,\"new\":\"test\"}",
      "created_at": "2021-08-26T14:55:23.000000Z",
      "updated_at": "2021-08-26T14:55:23.000000Z"
    }
  ],
  "links": {
    "first": "https://example.spp.co/api/logs?page=1",
    "last": "https://example.spp.co/api/logs?page=3",
    "prev": null,
    "next": "https://example.spp.co/api/logs?page=2"
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 3,
    "per_page": 20,
    "to": 20,
    "total": 43
  }
}
```

### Side Effects / State Changes
None (read-only)

### Preconditions / Invariants
- Valid authentication token required

### Error Cases
| Code | Error | Description |
|------|-------|-------------|
| 401 | Unauthorized | Invalid or missing bearer token |

### Notes / Gotchas
- Logs are sorted by creation date in descending order (most recent first)
- `data` field is a JSON string, not a parsed object
- `loggable_type` uses fully qualified PHP class names (e.g., `App\Models\OnboardingForm`)
- `user_id` can be null (system-triggered events)

### Cross-references
- All other entities (Orders, Tickets, Clients, etc.) may appear in logs

---

## Ambiguities and Missing Information

1. **Query Parameters:** No filter/pagination parameters documented
2. **Event Types:** Only `created` shown - what other event types exist? (likely: `updated`, `deleted`)
3. **loggable_type Values:** Full list of loggable types not provided
4. **Data Structure:** `data` field format varies by event type - not documented
5. **Retention:** No information on log retention period
6. **Filtering:** No documented way to filter by entity type, user, or date range
