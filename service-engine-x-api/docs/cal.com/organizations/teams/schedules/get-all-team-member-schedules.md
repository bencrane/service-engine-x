<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-schedules/get-all-team-member-schedules -->

# Get all team member schedules

Required membership role: `team admin`. PBAC permission: `availability.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/schedules`

**Tags:** Orgs / Teams / Schedules

## Path Parameters

### `orgId` **required**

**Type:** `number`

### `teamId` **required**

**Type:** `number`

## Query Parameters

### `take` *optional*

**Type:** `number`

Maximum number of items to return

**Default:** `250`

### `skip` *optional*

**Type:** `number`

Number of items to skip

**Default:** `0`

### `eventTypeId` *optional*

**Type:** `number`

Filter schedules by event type ID

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

## Example Request

```bash
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/schedules" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object[]) **required**
  Items:
  - **`id`** (number) **required**
  - **`ownerId`** (number) **required**
  - **`name`** (string) **required**
  - **`timeZone`** (string) **required**
  - **`availability`** (object[]) **required**
    Items:
    - **`days`** (array (enum)) **required**
      Array of days when schedule is active.
      Allowed values: `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday`
    - **`startTime`** (string) **required**
      startTime must be a valid time in format HH:MM e.g. 08:00
    - **`endTime`** (string) **required**
      endTime must be a valid time in format HH:MM e.g. 15:00

  - **`isDefault`** (boolean) **required**
  - **`overrides`** (object[]) **required**
    Items:
    - **`date`** (string) **required**
    - **`startTime`** (string) **required**
      startTime must be a valid time in format HH:MM e.g. 12:00
    - **`endTime`** (string) **required**
      endTime must be a valid time in format HH:MM e.g. 13:00

**Example Response:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 254,
      "ownerId": 478,
      "name": "Catch up hours",
      "timeZone": "Europe/Rome",
      "availability": [
        {
          "days": [
            "Monday",
            "Tuesday"
          ],
          "startTime": "17:00",
          "endTime": "19:00"
        },
        {
          "days": [
            "Wednesday",
            "Thursday"
          ],
          "startTime": "16:00",
          "endTime": "20:00"
        }
      ],
      "isDefault": true,
      "overrides": [
        {
          "date": "2024-05-20",
          "startTime": "18:00",
          "endTime": "21:00"
        }
      ]
    }
  ]
}
```
