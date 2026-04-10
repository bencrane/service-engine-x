<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-roles/get-a-specific-organization-team-role -->

# Get a specific organization team role

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/roles/{roleId}`

**Tags:** Orgs / Teams / Roles

## Path Parameters

### `orgId` **required**

**Type:** `number`

### `teamId` **required**

**Type:** `number`

### `roleId` **required**

**Type:** `string`

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
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/roles/{roleId}" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object) **required**
  - **`id`** (string) **required**
    Unique identifier for the role
  - **`name`** (string) **required**
    Name of the role
  - **`color`** (string) *optional*
    Color for the role (hex code)
  - **`description`** (string) *optional*
    Description of the role
  - **`teamId`** (number) *optional*
    Team ID this role belongs to
  - **`type`** (`"SYSTEM"` | `"CUSTOM"`) **required**
    Type of role
    Allowed values: `SYSTEM`, `CUSTOM`
  - **`permissions`** (string (enum)[]) **required**
    Permissions assigned to this role in 'resource.action' format.
  - **`createdAt`** (string) **required**
    When the role was created
  - **`updatedAt`** (string) **required**
    When the role was last updated

**Example Response:**

```json
{
  "status": "success",
  "data": {
    "id": "string",
    "name": "string",
    "color": "string",
    "description": "string",
    "teamId": 0,
    "type": "SYSTEM",
    "permissions": [
      "booking.read",
      "eventType.create"
    ],
    "createdAt": "string",
    "updatedAt": "string"
  }
}
```
