<!-- Source: https://cal.com/docs/api-reference/v2/teams-users-ooo/get-all-out-of-office-entries-for-a-team-member -->

# Get all out-of-office entries for a team member

`GET /v2/teams/{teamId}/users/{userId}/ooo`

Get all out-of-office entries for a team member

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
| `userId` | `number` | Yes |  |

## Query Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `take` | `number` | No | Maximum number of items to return Default: `250` |
| `skip` | `number` | No | Number of items to skip Default: `0` |
| `sortStart` | `enum` | No | Sort results by their start time in ascending or descending order. Values: `asc`, `desc` |
| `sortEnd` | `enum` | No | Sort results by their end time in ascending or descending order. Values: `asc`, `desc` |

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object[]`)
  Array items:
  - **`userId`** **required** (`number`): The ID of the user.
    - Example: `2`
  - **`toUserId`** (`number`): The ID of the user covering for the out of office period, if applicable.
    - Example: `2`
  - **`id`** **required** (`number`): The ID of the ooo entry.
    - Example: `2`
  - **`uuid`** **required** (`string`): The UUID of the ooo entry.
    - Example: `e84be5a3-4696-49e3-acc7-b2f3999c3b94`
  - **`start`** **required** (`string (date-time)`): The start date and time of the out of office period in ISO 8601 format in UTC timezone.
    - Example: `2023-05-01T00:00:00.000Z`
  - **`end`** **required** (`string (date-time)`): The end date and time of the out of office period in ISO 8601 format in UTC timezone.
    - Example: `2023-05-10T23:59:59.999Z`
  - **`notes`** (`string`): Optional notes for the out of office entry.
    - Example: `Vacation in Hawaii`
  - **`reason`** (`enum`): the reason for the out of office entry, if applicable
    - Enum values: `unspecified`, `vacation`, `travel`, `sick`, `public_holiday`
    - Example: `vacation`

## Example Request

```bash
curl -X GET \
  "https://api.cal.com/v2/teams/<teamId>/users/<userId>/ooo" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
