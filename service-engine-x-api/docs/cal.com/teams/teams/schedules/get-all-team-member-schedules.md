<!-- Source: https://cal.com/docs/api-reference/v2/teams-schedules/get-all-team-member-schedules -->

# Get all team member schedules

`GET /v2/teams/{teamId}/schedules`

Get all team member schedules

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
  - **`id`** **required** (`number`)
    - Example: `254`
  - **`ownerId`** **required** (`number`)
    - Example: `478`
  - **`name`** **required** (`string`)
    - Example: `Catch up hours`
  - **`timeZone`** **required** (`string`)
    - Example: `Europe/Rome`
  - **`availability`** **required** (`object[]`)
    Array items:
    - **`days`** **required** (`enum[]`): Array of days when schedule is active.
      - Enum values: `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday`
    - **`startTime`** **required** (`string`): startTime must be a valid time in format HH:MM e.g. 08:00
      - Example: `08:00`
    - **`endTime`** **required** (`string`): endTime must be a valid time in format HH:MM e.g. 15:00
      - Example: `15:00`
  - **`isDefault`** **required** (`boolean`)
    - Example: `True`
  - **`overrides`** **required** (`object[]`)
    Array items:
    - **`date`** **required** (`string`)
      - Example: `2024-05-20`
    - **`startTime`** **required** (`string`): startTime must be a valid time in format HH:MM e.g. 12:00
      - Example: `12:00`
    - **`endTime`** **required** (`string`): endTime must be a valid time in format HH:MM e.g. 13:00
      - Example: `13:00`

## Example Request

```bash
curl -X GET \
  "https://api.cal.com/v2/teams/<teamId>/schedules" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
