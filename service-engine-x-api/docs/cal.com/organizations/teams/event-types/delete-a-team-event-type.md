<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-event-types/delete-a-team-event-type -->

# Delete a team event type

Required membership role: `team admin`. PBAC permission: `eventType.delete`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`DELETE /v2/organizations/{orgId}/teams/{teamId}/event-types/{eventTypeId}`

**Tags:** Orgs / Teams / Event Types

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `eventTypeId` **required**

**Type:** `number`

### `orgId` **required**

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

## Example Request

```bash
curl -X DELETE "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/event-types/{eventTypeId}" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object) **required**
  - **`id`** (number) **required**
  - **`title`** (string) **required**

**Example Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "title": "Team Meeting"
  }
}
```
