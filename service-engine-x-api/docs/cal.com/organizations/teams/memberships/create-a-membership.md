<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-memberships/create-a-membership -->

# Create a membership

Required membership role: `team admin`. PBAC permission: `team.invite`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`POST /v2/organizations/{orgId}/teams/{teamId}/memberships`

**Tags:** Orgs / Teams / Memberships

## Path Parameters

### `orgId` **required**

**Type:** `number`

### `teamId` **required**

**Type:** `number`

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

## Request Body

**Required:** Yes

**Content-Type:** `application/json`

- **`userId`** (number) **required**
- **`accepted`** (boolean) *optional*
  Default: `False`
- **`role`** (`"MEMBER"` | `"OWNER"` | `"ADMIN"`) **required**
  Default: `MEMBER`
  Allowed values: `MEMBER`, `OWNER`, `ADMIN`
- **`disableImpersonation`** (boolean) *optional*
  Default: `False`

### Example Request Body

```json
{
  "userId": 0,
  "accepted": false,
  "role": "MEMBER",
  "disableImpersonation": false
}
```

## Example Request

```bash
curl -X POST "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/memberships" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '{"userId": 0, "accepted": false, "role": "MEMBER", "disableImpersonation": false}'
```

## Responses

### 201

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object) **required**
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
  "data": {
    "id": 0,
    "userId": 0,
    "teamId": 0,
    "accepted": true,
    "role": "MEMBER",
    "disableImpersonation": true,
    "user": {
      "avatarUrl": "string",
      "username": "string",
      "name": "string",
      "email": "string",
      "bio": "string",
      "metadata": {
        "key": "value"
      }
    }
  }
}
```
