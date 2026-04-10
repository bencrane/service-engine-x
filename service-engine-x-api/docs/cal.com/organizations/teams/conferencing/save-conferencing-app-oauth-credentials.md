<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-conferencing/save-conferencing-app-oauth-credentials -->

# Save conferencing app OAuth credentials

Required membership role: `team admin`. PBAC permission: `team.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/conferencing/{app}/oauth/callback`

**Tags:** Orgs / Teams / Conferencing

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `orgId` **required**

**Type:** `number`

### `app` **required**

**Type:** `string`

## Query Parameters

### `state` **required**

**Type:** `string`

### `code` **required**

**Type:** `string`

## Example Request

```bash
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/conferencing/{app}/oauth/callback" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200
