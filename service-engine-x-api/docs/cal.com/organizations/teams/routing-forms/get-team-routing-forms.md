<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-routing-forms/get-team-routing-forms -->

# Get team routing forms

Required membership role: `team admin`. PBAC permission: `routingForm.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/routing-forms`

**Tags:** Orgs / Teams / Routing forms

## Path Parameters

### `orgId` **required**

**Type:** `number`

### `teamId` **required**

**Type:** `number`

## Query Parameters

### `skip` *optional*

**Type:** `number`

Number of responses to skip

### `take` *optional*

**Type:** `number`

Number of responses to take

### `sortCreatedAt` *optional*

**Type:** ``"asc"` | `"desc"``

Sort by creation time

**Allowed values:** `asc`, `desc`

### `sortUpdatedAt` *optional*

**Type:** ``"asc"` | `"desc"``

Sort by update time

**Allowed values:** `asc`, `desc`

### `afterCreatedAt` *optional*

**Type:** `string`

Filter by responses created after this date

### `beforeCreatedAt` *optional*

**Type:** `string`

Filter by responses created before this date

### `afterUpdatedAt` *optional*

**Type:** `string`

Filter by responses created after this date

### `beforeUpdatedAt` *optional*

**Type:** `string`

Filter by responses updated before this date

### `routedToBookingUid` *optional*

**Type:** `string`

Filter by responses routed to a specific booking

## Header Parameters

### `Authorization` **required**

**Type:** `string`

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_

## Example Request

```bash
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/routing-forms" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object[]) **required**
  Items:
  - **`name`** (string) **required**
  - **`description`** (string) **required**
  - **`position`** (number) **required**
  - **`routes`** (object) *optional*
    Routing form routes configuration
  - **`createdAt`** (string) **required**
  - **`updatedAt`** (string) **required**
  - **`fields`** (object) *optional*
    Routing form fields configuration
  - **`userId`** (number) **required**
  - **`teamId`** (number) **required**
  - **`disabled`** (boolean) **required**
  - **`settings`** (object) *optional*
    Routing form settings
  - **`id`** (string) **required**

**Example Response:**

```json
{
  "status": "success",
  "data": [
    {
      "name": "My Form",
      "description": "This is the description.",
      "position": 0,
      "createdAt": "2024-03-28T10:00:00.000Z",
      "updatedAt": "2024-03-28T10:00:00.000Z",
      "userId": 2313,
      "teamId": 4214321,
      "disabled": false,
      "id": "string"
    }
  ]
}
```
