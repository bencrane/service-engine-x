<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-conferencing/set-team-default-conferencing-application -->

# Set team default conferencing application

Required membership role: `team admin`. PBAC permission: `team.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`POST /v2/organizations/{orgId}/teams/{teamId}/conferencing/{app}/default`

**Tags:** Orgs / Teams / Conferencing

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `app` **required**

**Type:** ``"google-meet"` | `"zoom"` | `"msteams"` | `"daily-video"``

Conferencing application type

**Allowed values:** `google-meet`, `zoom`, `msteams`, `daily-video`

### `orgId` **required**

**Type:** `number`

## Example Request

```bash
curl -X POST "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/conferencing/{app}/default" \
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
