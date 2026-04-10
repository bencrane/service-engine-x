<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-conferencing/connect-your-conferencing-application-to-a-team -->

# Connect your conferencing application to a team

Required membership role: `team admin`. PBAC permission: `team.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`POST /v2/organizations/{orgId}/teams/{teamId}/conferencing/{app}/connect`

**Tags:** Orgs / Teams / Conferencing

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `orgId` **required**

**Type:** `number`

### `app` **required**

**Type:** ``"google-meet"``

Conferencing application type

**Allowed values:** `google-meet`

## Example Request

```bash
curl -X POST "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/conferencing/{app}/connect" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object) **required**
  - **`id`** (number) **required**
    Id of the conferencing app credentials
  - **`type`** (string) **required**
    Type of conferencing app
  - **`userId`** (number) **required**
    Id of the user associated to the conferencing app
  - **`invalid`** (boolean) *optional*
    Whether if the connection is working or not.

**Example Response:**

```json
{
  "status": "success",
  "data": {
    "id": 0,
    "type": "google_video",
    "userId": 0,
    "invalid": true
  }
}
```
