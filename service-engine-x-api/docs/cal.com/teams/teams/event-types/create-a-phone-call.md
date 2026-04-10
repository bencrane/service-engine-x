<!-- Source: https://cal.com/docs/api-reference/v2/teams-event-types/create-a-phone-call -->

# Create a phone call

`POST /v2/teams/{teamId}/event-types/{eventTypeId}/create-phone-call`

Create a phone call

## Authorization

This endpoint requires authentication with a **Bearer token**.

```
Authorization: Bearer <your_api_key>
```

## Headers

| Name | Required | Description |
|------|----------|-------------|
| `Authorization` | Yes | Bearer token |
| `cal-api-version` | Yes | API version: `2024-08-13` |

## Path Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `teamId` | `number` | Yes |  |
| `eventTypeId` | `number` | Yes |  |

## Request Body

- **`yourPhoneNumber`** **required** (`string`): Your phone number
- **`numberToCall`** **required** (`string`): Number to call
- **`calApiKey`** **required** (`string`): CAL API Key
- **`enabled`** **required** (`boolean`): Enabled status
  - Default: `True`
- **`templateType`** **required** (`enum`): Template type
  - Enum values: `CHECK_IN_APPOINTMENT`, `CUSTOM_TEMPLATE`
  - Default: `CUSTOM_TEMPLATE`
- **`schedulerName`** (`string`): Scheduler name
- **`guestName`** (`string`): Guest name
- **`guestEmail`** (`string`): Guest email
- **`guestCompany`** (`string`): Guest company
- **`beginMessage`** (`string`): Begin message
- **`generalPrompt`** (`string`): General prompt

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

## Responses

### 201 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object`)
  - **`callId`** **required** (`string`)
  - **`agentId`** (`string`)

## Example Request

```bash
curl -X POST \
  "https://api.cal.com/v2/teams/<teamId>/event-types/<eventTypeId>/create-phone-call" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '<request_body>'
```
