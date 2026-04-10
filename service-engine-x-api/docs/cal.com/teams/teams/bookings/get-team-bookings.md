<!-- Source: https://cal.com/docs/api-reference/v2/teams-bookings/get-team-bookings -->

# Get team bookings

`GET /v2/teams/{teamId}/bookings`

Get team bookings

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
| `status` | `enum[]` | No | Filter bookings by status. If you want to filter by multiple statuses, separate them with a comma. |
| `attendeeEmail` | `string` | No | Filter bookings by the attendee's email address. |
| `attendeeName` | `string` | No | Filter bookings by the attendee's name. |
| `bookingUid` | `string` | No | Filter bookings by the booking Uid. |
| `eventTypeIds` | `string` | No | Filter bookings by event type ids belonging to the team. Event type ids must be separated by a comma. |
| `eventTypeId` | `string` | No | Filter bookings by event type id belonging to the team. |
| `afterStart` | `string` | No | Filter bookings with start after this date string. |
| `beforeEnd` | `string` | No | Filter bookings with end before this date string. |
| `sortStart` | `enum` | No | Sort results by their start time in ascending or descending order. Values: `asc`, `desc` |
| `sortEnd` | `enum` | No | Sort results by their end time in ascending or descending order. Values: `asc`, `desc` |
| `sortCreated` | `enum` | No | Sort results by their creation time (when booking was made) in ascending or descending order. Values: `asc`, `desc` |
| `take` | `number` | No | The number of items to return |
| `skip` | `number` | No | The number of items to skip |

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object | object | object[]`): Array of booking data, which can contain either BookingOutput objects or RecurringBookingOutput objects
- **`pagination`** **required** (`object`)
  - **`totalItems`** **required** (`number`): The total number of items available across all pages, matching the query criteria.
    - Example: `123`
  - **`remainingItems`** **required** (`number`): The number of items remaining to be fetched *after* the current page. Calculated as: `totalItems - (skip + itemsPerPage)`.
    - Example: `103`
  - **`returnedItems`** **required** (`number`): The number of items returned in the current page.
    - Example: `10`
  - **`itemsPerPage`** **required** (`number`): The maximum number of items requested per page.
    - Example: `10`
  - **`currentPage`** **required** (`number`): The current page number being returned.
    - Example: `2`
  - **`totalPages`** **required** (`number`): The total number of pages available.
    - Example: `13`
  - **`hasNextPage`** **required** (`boolean`): Indicates if there is a subsequent page available after the current one.
    - Example: `True`
  - **`hasPreviousPage`** **required** (`boolean`): Indicates if there is a preceding page available before the current one.
    - Example: `True`

## Example Request

```bash
curl -X GET \
  "https://api.cal.com/v2/teams/<teamId>/bookings" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
