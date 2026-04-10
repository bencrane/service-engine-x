<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-conferencing/get-team-default-conferencing-application -->

# Get team default conferencing application

Required membership role: `team admin`. PBAC permission: `team.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/conferencing/default`

**Tags:** Orgs / Teams / Conferencing

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `orgId` **required**

**Type:** `number`

## Example Request

```bash
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/conferencing/default" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object) *optional*
  - **`appSlug`** (string) *optional*
  - **`appLink`** (string) *optional*

**Example Response:**

```json
{
  "status": "success",
  "data": {
    "appSlug": "string",
    "appLink": "string"
  }
}
```
