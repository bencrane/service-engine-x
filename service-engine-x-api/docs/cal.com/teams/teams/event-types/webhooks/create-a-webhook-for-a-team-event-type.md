<!-- Source: https://cal.com/docs/api-reference/v2/teams-event-types-webhooks/create-a-webhook-for-a-team-event-type -->

# Create a webhook for a team event type

`POST /v2/teams/{teamId}/event-types/{eventTypeId}/webhooks`

Create a webhook for a team event type

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
| `eventTypeId` | `number` | Yes |  |
| `teamId` | `number` | Yes |  |

## Request Body

- **`payloadTemplate`** (`string`): The template of the payload that will be sent to the subscriberUrl, check cal.com/docs/core-features/webhooks for more information
  - Example: `{"content":"A new event has been scheduled","type":"{{type}}","name":"{{title}}","organizer":"{{organizer.name}}","booker":"{{attendees.0.name}}"}`
- **`active`** **required** (`boolean`)
- **`subscriberUrl`** **required** (`string`)
- **`triggers`** **required** (`enum[]`)
- **`secret`** (`string`)
- **`version`** (`enum`): The version of the webhook
  - Enum values: `2021-10-20`
  - Example: `2021-10-20`

### Example Request Body

```json
{
  "payloadTemplate": "{\"content\":\"A new event has been scheduled\",\"type\":\"{{type}}\",\"name\":\"{{title}}\",\"organizer\":\"{{organizer.name}}\",\"booker\":\"{{attendees.0.name}}\"}",
  "active": true,
  "subscriberUrl": "string",
  "triggers": [
    "BOOKING_CREATED",
    "BOOKING_RESCHEDULED",
    "BOOKING_CANCELLED",
    "BOOKING_CONFIRMED",
    "BOOKING_REJECTED",
    "BOOKING_COMPLETED",
    "BOOKING_NO_SHOW",
    "BOOKING_REOPENED"
  ],
  "secret": "string",
  "version": "2021-10-20"
}
```

## Responses

### 201 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object`)
  - **`payloadTemplate`** **required** (`string`): The template of the payload that will be sent to the subscriberUrl, check cal.com/docs/core-features/webhooks for more information
    - Example: `{"content":"A new event has been scheduled","type":"{{type}}","name":"{{title}}","organizer":"{{organizer.name}}","booker":"{{attendees.0.name}}"}`
  - **`triggers`** **required** (`enum[]`)
  - **`eventTypeId`** **required** (`number`)
  - **`id`** **required** (`number`)
  - **`subscriberUrl`** **required** (`string`)
  - **`active`** **required** (`boolean`)
  - **`secret`** (`string`)

## Example Request

```bash
curl -X POST \
  "https://api.cal.com/v2/teams/<teamId>/event-types/<eventTypeId>/webhooks" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '<request_body>'
```
