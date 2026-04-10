<!-- Source: https://cal.com/docs/api-reference/v2/teams-event-types-webhooks/delete-a-webhook-for-a-team-event-type -->

# Delete a webhook for a team event type

`DELETE /v2/teams/{teamId}/event-types/{eventTypeId}/webhooks/{webhookId}`

Delete a webhook for a team event type

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
| `webhookId` | `string` | Yes |  |
| `eventTypeId` | `number` | Yes |  |
| `teamId` | `number` | Yes |  |

## Responses

### 200 - 

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
curl -X DELETE \
  "https://api.cal.com/v2/teams/<teamId>/event-types/<eventTypeId>/webhooks/<webhookId>" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
