<!-- Source: https://cal.com/docs/api-reference/v2/teams-verified-resources/get-verified-phone-number-of-a-team-by-id -->

# Get verified phone number of a team by id

`GET /v2/teams/{teamId}/verified-resources/phones/{id}`

Get verified phone number of a team by id

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
| `id` | `number` | Yes |  |

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object`)
  - **`id`** **required** (`number`): The unique identifier for the verified email.
    - Example: `789`
  - **`phoneNumber`** **required** (`string (phone)`): The verified phone number.
    - Example: `+37255556666`
  - **`userId`** (`number`): The ID of the associated user, if applicable.
    - Example: `45`
  - **`teamId`** **required** (`number`): The ID of the associated team, if applicable.
    - Example: `89`

## Example Request

```bash
curl -X GET \
  "https://api.cal.com/v2/teams/<teamId>/verified-resources/phones/<id>" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
