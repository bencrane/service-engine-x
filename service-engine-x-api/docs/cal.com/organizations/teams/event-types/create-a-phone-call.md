<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-event-types/create-a-phone-call -->

# Create a phone call

Required membership role: `team admin`. PBAC permission: `eventType.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`POST /v2/organizations/{orgId}/teams/{teamId}/event-types/{eventTypeId}/create-phone-call`

**Tags:** Orgs / Teams / Event Types

## Path Parameters

### `eventTypeId` **required**

**Type:** `number`

### `orgId` **required**

**Type:** `number`

### `teamId` **required**

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

## Request Body

**Required:** Yes

**Content-Type:** `application/json`

- **`yourPhoneNumber`** (string) **required**
  Your phone number
- **`numberToCall`** (string) **required**
  Number to call
- **`calApiKey`** (string) **required**
  CAL API Key
- **`enabled`** (boolean) **required**
  Enabled status
  Default: `True`
- **`templateType`** (`"CHECK_IN_APPOINTMENT"` | `"CUSTOM_TEMPLATE"`) **required**
  Template type
  Default: `CUSTOM_TEMPLATE`
  Allowed values: `CHECK_IN_APPOINTMENT`, `CUSTOM_TEMPLATE`
- **`schedulerName`** (string) *optional*
  Scheduler name
- **`guestName`** (string) *optional*
  Guest name
- **`guestEmail`** (string) *optional*
  Guest email
- **`guestCompany`** (string) *optional*
  Guest company
- **`beginMessage`** (string) *optional*
  Begin message
- **`generalPrompt`** (string) *optional*
  General prompt

### Example Request Body

```json
{
  "yourPhoneNumber": "string",
  "numberToCall": "string",
  "calApiKey": "string",
  "enabled": true,
  "templateType": "CHECK_IN_APPOINTMENT",
  "schedulerName": "string",
  "guestName": "string",
  "guestEmail": "string",
  "guestCompany": "string",
  "beginMessage": "string",
  "generalPrompt": "string"
}
```

## Example Request

```bash
curl -X POST "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/event-types/{eventTypeId}/create-phone-call" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '{"yourPhoneNumber": "string", "numberToCall": "string", "calApiKey": "string", "enabled": true, "templateType": "CHECK_IN_APPOINTMENT", "schedulerName": "string", "guestName": "string", "guestEmail": "string", "guestCompany": "string", "beginMessage": "string", "generalPrompt": "string"}'
```

## Responses

### 201

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object) **required**
  - **`callId`** (string) **required**
  - **`agentId`** (string) *optional*

**Example Response:**

```json
{
  "status": "success",
  "data": {
    "callId": "string",
    "agentId": "string"
  }
}
```
