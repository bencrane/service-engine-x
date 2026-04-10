<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-roles-permissions/list-permissions-for-an-organization-team-role -->

# List permissions for an organization team role

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/roles/{roleId}/permissions`

**Tags:** Orgs / Teams / Roles / Permissions

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
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/roles/{roleId}/permissions" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (string) **required**
- **`data`** (string[]) **required**

**Example Response:**

```json
{
  "status": "success",
  "data": [
    "string"
  ]
}
```
