# 6. MagicLink - API Documentation Summary

## Overview
The MagicLink API provides a single endpoint for generating passwordless login links for client users. These links allow users to log in without entering credentials.

---

## 6.1 Generate Magic Link

### File Path
`spp-api-documentation/6. MagicLink/6.1 generate-magic-link.md`

### Name
Generate a magic link

### HTTP Method
`GET`

### URL Path
`https://{workspaceUrl}/api/login_links/{user}`

### Auth Requirements
- **Type:** Bearer Token (implied, though documentation shows "No auth selected")
- **Header:** `Authorization: Bearer {token}`

**Note:** Documentation shows "No auth selected" in UI but endpoint likely requires authentication.

### Request Headers
| Header | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| Authorization | string | likely required | Bearer token | `Bearer 123` |
| X-Api-Version | string | optional | API version identifier | `2024-03-05` |

### Query Parameters
None

### Path Parameters
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| user | integer or allOf | **required** | Client user ID to generate link for | `1` |

### Request Body Schema
Not applicable (GET request)

### Response Status Codes
| Code | Description |
|------|-------------|
| 200 | Success - Magic link generated |
| 401 | Unauthorized |
| 403 | Forbidden - User has 2FA enabled or is staff |
| 404 | Not Found - User doesn't exist |

### Response Body Schema (200)
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| link | string | The generated magic login link | `https://example.com/login?token=ewtGwgZ0b3IE1wq7a7vrjhONy0uVBPgT` |

### Example Request
```bash
curl --request GET \
  --url https://example.spp.co/api/login_links/1 \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer 123' \
  --header 'X-Api-Version: 2024-03-05'
```

### Example Response
```json
{
  "link": "https://example.com/login?token=ewtGwgZ0b3IE1wq7a7vrjhONy0uVBPgT"
}
```

### Side Effects / State Changes
- Generates a magic link token for the user
- If user has existing unexpired magic link, it will be reused (not regenerated)

### Preconditions / Invariants
- User must be a **client user** (not staff)
- User must **NOT** have 2FA enabled
- User must exist

### Error Cases
| Code | Error | Description |
|------|-------|-------------|
| 401 | Unauthorized | Invalid or missing bearer token |
| 403 | Forbidden | User has 2FA enabled OR user is staff (not client) |
| 404 | Not Found | User ID doesn't exist |

### Notes / Gotchas
- **IMPORTANT:** Magic link is valid for **2 hours** only
- **IMPORTANT:** If user already has a valid magic link, the same link is returned (not a new one)
- **SECURITY:** Cannot generate magic links for users with 2FA enabled
- **SECURITY:** Only works for client users, not staff users
- The token parameter in the link is a bearer-style token, not user ID

### Cross-references
- Clients (17. Clients) - User must be a client
- Team (13. Team) - Staff users cannot use magic links

---

## Ambiguities and Missing Information

1. **Authentication:** Documentation shows "No auth selected" but this seems like an error - likely requires auth
2. **Token Format:** Token format/length not documented
3. **Reuse Behavior:** "If the user has a previously generated magic link, it will be reused" - unclear if this extends expiration or uses original expiration
4. **Invalidation:** No endpoint to invalidate/revoke magic links
5. **Multiple Links:** Can only one magic link exist per user at a time?
6. **403 Error Body:** Response body for 403 errors not documented
7. **Rate Limiting:** No rate limiting information provided (important for security)
