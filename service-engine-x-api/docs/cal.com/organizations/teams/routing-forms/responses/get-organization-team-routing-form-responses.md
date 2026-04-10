<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-routing-forms-responses/get-organization-team-routing-form-responses -->

# Get organization team routing form responses

Required membership role: `team admin`. PBAC permission: `routingForm.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/routing-forms/{routingFormId}/responses`

**Tags:** Orgs / Teams / Routing forms / Responses

## Path Parameters

### `routingFormId` **required**

**Type:** `string`

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
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/routing-forms/{routingFormId}/responses" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object[]) **required**
  Items:
  - **`id`** (number) **required**
  - **`formId`** (string) **required**
  - **`formFillerId`** (string) **required**
  - **`routedToBookingUid`** (string) **required**
  - **`response`** (object) **required**
  - **`createdAt`** (string) **required**

**Example Response:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 0,
      "formId": "string",
      "formFillerId": "string",
      "routedToBookingUid": "string",
      "response": {
        "f00b26df-f54b-4985-8d98-17c5482c6a24": {
          "label": "participant",
          "value": "mamut"
        }
      },
      "createdAt": "string"
    }
  ]
}
```
