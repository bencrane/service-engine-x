<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-bookings/get-organization-team-bookings -->

# Get organization team bookings

Required membership role: `team admin`. PBAC permission: `booking.readTeamBookings`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/bookings`

**Tags:** Orgs / Teams / Bookings

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `orgId` **required**

**Type:** `number`

## Query Parameters

### `status` *optional*

**Type:** ``"upcoming"` | `"recurring"` | `"past"` | `"cancelled"` | `"unconfirmed"`[]`

Filter bookings by status. If you want to filter by multiple statuses, separate them with a comma.

### `attendeeEmail` *optional*

**Type:** `string`

Filter bookings by the attendee's email address.

### `attendeeName` *optional*

**Type:** `string`

Filter bookings by the attendee's name.

### `bookingUid` *optional*

**Type:** `string`

Filter bookings by the booking Uid.

### `eventTypeIds` *optional*

**Type:** `string`

Filter bookings by event type ids belonging to the team. Event type ids must be separated by a comma.

### `eventTypeId` *optional*

**Type:** `string`

Filter bookings by event type id belonging to the team.

### `afterStart` *optional*

**Type:** `string`

Filter bookings with start after this date string.

### `beforeEnd` *optional*

**Type:** `string`

Filter bookings with end before this date string.

### `sortStart` *optional*

**Type:** ``"asc"` | `"desc"``

Sort results by their start time in ascending or descending order.

**Allowed values:** `asc`, `desc`

### `sortEnd` *optional*

**Type:** ``"asc"` | `"desc"``

Sort results by their end time in ascending or descending order.

**Allowed values:** `asc`, `desc`

### `sortCreated` *optional*

**Type:** ``"asc"` | `"desc"``

Sort results by their creation time (when booking was made) in ascending or descending order.

**Allowed values:** `asc`, `desc`

### `take` *optional*

**Type:** `number`

The number of items to return

### `skip` *optional*

**Type:** `number`

The number of items to skip

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
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/bookings" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object | object | object | object[]) **required**
  Array of booking data, which can contain either BookingOutput objects or RecurringBookingOutput objects
- **`pagination`** (object) **required**
  - **`totalItems`** (number) **required**
    The total number of items available across all pages, matching the query criteria.
  - **`remainingItems`** (number) **required**
    The number of items remaining to be fetched *after* the current page. Calculated as: `totalItems - (skip + itemsPerPage)`.
  - **`returnedItems`** (number) **required**
    The number of items returned in the current page.
  - **`itemsPerPage`** (number) **required**
    The maximum number of items requested per page.
  - **`currentPage`** (number) **required**
    The current page number being returned.
  - **`totalPages`** (number) **required**
    The total number of pages available.
  - **`hasNextPage`** (boolean) **required**
    Indicates if there is a subsequent page available after the current one.
  - **`hasPreviousPage`** (boolean) **required**
    Indicates if there is a preceding page available before the current one.

**Example Response:**

```json
{
  "status": "success",
  "data": [],
  "pagination": {
    "totalItems": 123,
    "remainingItems": 103,
    "returnedItems": 10,
    "itemsPerPage": 10,
    "currentPage": 2,
    "totalPages": 13,
    "hasNextPage": true,
    "hasPreviousPage": true
  }
}
```
