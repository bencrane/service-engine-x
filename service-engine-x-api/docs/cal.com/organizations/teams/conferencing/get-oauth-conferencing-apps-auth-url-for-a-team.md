<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-conferencing/get-oauth-conferencing-apps-auth-url-for-a-team -->

# Get OAuth conferencing app&#x27;s auth URL for a team

Required membership role: `team admin`. PBAC permission: `team.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/conferencing/{app}/oauth/auth-url`

**Tags:** Orgs / Teams / Conferencing

**Summary:** Get OAuth conferencing app's auth URL for a team

## Path Parameters

### `teamId` **required**

**Type:** `string`

### `orgId` **required**

**Type:** `number`

### `app` **required**

**Type:** ``"zoom"` | `"msteams"``

Conferencing application type

**Allowed values:** `zoom`, `msteams`

## Query Parameters

### `returnTo` **required**

**Type:** `string`

### `onErrorReturnTo` **required**

**Type:** `string`

## Header Parameters

### `Authorization` **required**

**Type:** `string`

## Example Request

```bash
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/conferencing/{app}/oauth/auth-url" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`

**Example Response:**

```json
{
  "status": "success"
}
```
