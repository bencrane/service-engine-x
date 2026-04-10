<!-- Source: https://cal.com/docs/api-reference/v2/bookings/get-all-bookings -->

# Get all bookings - Cal.com Docs

Bookings
# Get all bookings
Copy pagePlease make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pageGET/v2/bookingsTry itGet all bookings

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/bookings \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "id": 123,
      "uid": "booking_uid_123",
      "title": "Consultation",
      "description": "Learn how to integrate scheduling into marketplace.",
      "hosts": [
        {
          "id": 1,
          "name": "Jane Doe",
          "email": "[email protected]",
          "displayEmail": "[email protected]",
          "username": "jane100",
          "timeZone": "America/Los_Angeles"
        }
      ],
      "status": "accepted",
      "start": "2024-08-13T15:30:00Z",
      "end": "2024-08-13T16:30:00Z",
      "duration": 60,
      "eventTypeId": 50,
      "eventType": {
        "id": 1,
        "slug": "some-event"
      },
      "location": "https://example.com/meeting",
      "absentHost": true,
      "createdAt": "2024-08-13T15:30:00Z",
      "updatedAt": "2024-08-13T15:30:00Z",
      "attendees": [
        {
          "name": "John Doe",
          "email": "[email protected]",
          "displayEmail": "[email protected]",
          "timeZone": "America/New_York",
          "absent": false,
          "language": "en",
          "phoneNumber": "+1234567890"
        }
      ],
      "bookingFieldsResponses": {
        "customField": "customValue"
      },
      "cancellationReason": "User requested cancellation",
      "cancelledByEmail": "[email protected]",
      "reschedulingReason": "User rescheduled the event",
      "rescheduledByEmail": "[email protected]",
      "rescheduledFromUid": "previous_uid_123",
      "rescheduledToUid": "new_uid_456",
      "meetingUrl": "https://example.com/recurring-meeting",
      "metadata": {
        "key": "value"
      },
      "rating": 4,
      "icsUid": "ics_uid_123",
      "guests": [
        "[email protected]",
        "[email protected]"
      ]
    }
  ],
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
}`
```

#### Headers
​cal-api-versionstringdefault:2026-02-25required

Must be set to 2026-02-25.​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Query Parameters
​statusenum<string>[]

Filter bookings by status. If you want to filter by multiple statuses, separate them with a comma.Available options: `upcoming`, `recurring`, `past`, `cancelled`, `unconfirmed` Example:

`"?status=upcoming,past"`​attendeeEmailstring

Filter bookings by the attendee's email address.Example:

`"[email protected]"`​attendeeNamestring

Filter bookings by the attendee's name.Example:

`"John Doe"`​bookingUidstring

Filter bookings by the booking Uid.Example:

`"2NtaeaVcKfpmSZ4CthFdfk"`​eventTypeIdsstring

Filter bookings by event type ids belonging to the user. Event type ids must be separated by a comma.Example:

`"?eventTypeIds=100,200"`​eventTypeIdstring

Filter bookings by event type id belonging to the user.Example:

`"?eventTypeId=100"`​teamsIdsstring

Filter bookings by team ids that user is part of. Team ids must be separated by a comma.Example:

`"?teamIds=50,60"`​teamIdstring

Filter bookings by team id that user is part ofExample:

`"?teamId=50"`​afterStartstring

Filter bookings with start after this date string.Example:

`"?afterStart=2025-03-07T10:00:00.000Z"`​beforeEndstring

Filter bookings with end before this date string.Example:

`"?beforeEnd=2025-03-07T11:00:00.000Z"`​afterCreatedAtstring

Filter bookings that have been created after this date string.Example:

`"?afterCreatedAt=2025-03-07T10:00:00.000Z"`​beforeCreatedAtstring

Filter bookings that have been created before this date string.Example:

`"?beforeCreatedAt=2025-03-14T11:00:00.000Z"`​afterUpdatedAtstring

Filter bookings that have been updated after this date string.Example:

`"?afterUpdatedAt=2025-03-07T10:00:00.000Z"`​beforeUpdatedAtstring

Filter bookings that have been updated before this date string.Example:

`"?beforeUpdatedAt=2025-03-14T11:00:00.000Z"`​sortStartenum<string>

Sort results by their start time in ascending or descending order.Available options: `asc`, `desc` Example:

`"?sortStart=asc OR ?sortStart=desc"`​sortEndenum<string>

Sort results by their end time in ascending or descending order.Available options: `asc`, `desc` Example:

`"?sortEnd=asc OR ?sortEnd=desc"`​sortCreatedenum<string>

Sort results by their creation time (when booking was made) in ascending or descending order.Available options: `asc`, `desc` Example:

`"?sortCreated=asc OR ?sortCreated=desc"`​sortUpdatedAtenum<string>

Sort results by their updated time (for example when booking status changes) in ascending or descending order.Available options: `asc`, `desc` Example:

`"?sortUpdated=asc OR ?sortUpdated=desc"`​takenumberdefault:100

The number of items to returnExample:

`10`​skipnumberdefault:0

The number of items to skipExample:

`0`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Array of booking data, which can contain either BookingOutput objects or RecurringBookingOutput objects
- Option 1
- Option 2
- Option 3
- Option 4

Show child attributes​paginationobjectrequired

Show child attributes
