<!-- Source: https://cal.com/docs/api-reference/v2/teams-verified-resources/get-list-of-verified-emails-of-a-team -->

# Get list of verified emails of a team

`GET /v2/teams/{teamId}/verified-resources/emails`

Get list of verified emails of a team

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
  - **`id`** **required** (`number`): The unique identifier for the verified email.
    - Example: `789`
  - **`email`** **required** (`string (email)`): The verified email address.
    - Example: `user@example.com`
  - **`teamId`** **required** (`number`): The ID of the associated team, if applicable.
    - Example: `89`
  - **`userId`** (`number`): The ID of the associated user, if applicable.
    - Example: `45`

## Example Request

```bash
curl -X GET \
  "https://api.cal.com/v2/teams/<teamId>/verified-resources/emails" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
