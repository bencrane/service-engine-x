<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-conferencing/disconnect-team-conferencing-application -->

# Disconnect team conferencing application

Required membership role: `team admin`. PBAC permission: `team.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`DELETE /v2/organizations/{orgId}/teams/{teamId}/conferencing/{app}/disconnect`

**Tags:** Orgs / Teams / Conferencing

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `app` **required**

**Type:** ``"google-meet"` | `"zoom"` | `"msteams"``

Conferencing application type

**Allowed values:** `google-meet`, `zoom`, `msteams`

### `orgId` **required**

**Type:** `number`

## Example Request

```bash
curl -X DELETE "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/conferencing/{app}/disconnect" \
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
