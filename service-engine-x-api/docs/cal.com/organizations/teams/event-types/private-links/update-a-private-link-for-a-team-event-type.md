<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-event-types-private-links/update-a-private-link-for-a-team-event-type -->

# Update a private link for a team event type

## Endpoint

`PATCH /v2/organizations/{orgId}/teams/{teamId}/event-types/{eventTypeId}/private-links/{linkId}`

**Tags:** Orgs / Teams / Event Types / Private Links

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `eventTypeId` **required**

**Type:** `number`

### `linkId` **required**

**Type:** `string`

### `orgId` **required**

**Type:** `number`

## Header Parameters

### `cal-api-version` **required**

**Type:** `string`

Must be set to `2024-09-04`. Returns the full booking URL including org slug and event slug.

**Default:** `2024-09-04`

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
curl -X PATCH "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/event-types/{eventTypeId}/private-links/{linkId}" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (string) **required**
  Response status
- **`data`** (object | object) **required**
  Updated private link data (either time-based or usage-based)

**Example Response:**

```json
{
  "status": "success"
}
```
