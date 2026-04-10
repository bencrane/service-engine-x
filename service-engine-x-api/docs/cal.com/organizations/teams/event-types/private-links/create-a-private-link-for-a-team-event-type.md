<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-event-types-private-links/create-a-private-link-for-a-team-event-type -->

# Create a private link for a team event type

## Endpoint

`POST /v2/organizations/{orgId}/teams/{teamId}/event-types/{eventTypeId}/private-links`

**Tags:** Orgs / Teams / Event Types / Private Links

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `eventTypeId` **required**

**Type:** `number`

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

## Request Body

**Required:** Yes

**Content-Type:** `application/json`

- **`expiresAt`** (string) *optional*
  Expiration date for time-based links
- **`maxUsageCount`** (number) *optional*
  Maximum number of times the link can be used. If omitted and expiresAt is not provided, defaults to 1 (one time use).
  Default: `1`

### Example Request Body

```json
{
  "expiresAt": "2024-12-31T23:59:59.000Z",
  "maxUsageCount": 10
}
```

## Example Request

```bash
curl -X POST "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/event-types/{eventTypeId}/private-links" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '{"expiresAt": "2024-12-31T23:59:59.000Z", "maxUsageCount": 10}'
```

## Responses

### 201

- **`status`** (string) **required**
  Response status
- **`data`** (object | object) **required**
  Created private link data (either time-based or usage-based)

**Example Response:**

```json
{
  "status": "success"
}
```
