<!-- Source: https://cal.com/docs/api-reference/v2/teams-event-types-webhooks/delete-all-webhooks-for-a-team-event-type -->

# Delete all webhooks for a team event type

`DELETE /v2/teams/{teamId}/event-types/{eventTypeId}/webhooks`

Delete all webhooks for a team event type

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

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`string`)

## Example Request

```bash
curl -X DELETE \
  "https://api.cal.com/v2/teams/<teamId>/event-types/<eventTypeId>/webhooks" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
