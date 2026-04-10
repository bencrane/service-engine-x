<!-- Source: https://cal.com/docs/api-reference/v2/teams-event-types-webhooks/get-all-webhooks-for-a-team-event-type -->

# Get all webhooks for a team event type

`GET /v2/teams/{teamId}/event-types/{eventTypeId}/webhooks`

Get all webhooks for a team event type

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

## Query Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `take` | `number` | No | Maximum number of items to return Default: `250` |
| `skip` | `number` | No | Number of items to skip Default: `0` |

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object[]`)
  Array items:
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
curl -X GET \
  "https://api.cal.com/v2/teams/<teamId>/event-types/<eventTypeId>/webhooks" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
