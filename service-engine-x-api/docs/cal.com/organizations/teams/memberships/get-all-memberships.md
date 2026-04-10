<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-memberships/get-all-memberships -->

# Get all memberships

Required membership role: `team admin`. PBAC permission: `team.listMembers`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/memberships`

**Tags:** Orgs / Teams / Memberships

## Path Parameters

### `orgId` **required**

**Type:** `number`

### `teamId` **required**

**Type:** `number`

## Query Parameters

### `take` *optional*

**Type:** `number`

Maximum number of items to return

**Default:** `250`

### `skip` *optional*

**Type:** `number`

Number of items to skip

**Default:** `0`

## Header Parameters

### `Authorization` *optional*

**Type:** `string`

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_

### `x-cal-secret-key` *optional*

**Type:** `string`

For platform customers - OAuth client secret key

### `x-cal-client-id` *optional*

**Type:** `string`

For platform customers - OAuth client ID

## Example Request

```bash
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/memberships" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object[]) **required**
  Items:
  - **`id`** (number) **required**
  - **`userId`** (number) **required**
  - **`teamId`** (number) **required**
  - **`accepted`** (boolean) **required**
  - **`role`** (`"MEMBER"` | `"OWNER"` | `"ADMIN"`) **required**
    Allowed values: `MEMBER`, `OWNER`, `ADMIN`
  - **`disableImpersonation`** (boolean) *optional*
  - **`user`** (object) **required**
    - **`avatarUrl`** (string) *optional*
    - **`username`** (string) *optional*
    - **`name`** (string) *optional*
    - **`email`** (string) **required**
    - **`bio`** (string) *optional*
    - **`metadata`** (object) *optional*

**Example Response:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 0,
      "userId": 0,
      "teamId": 0,
      "accepted": true,
      "role": "MEMBER",
      "disableImpersonation": true
    }
  ]
}
```
