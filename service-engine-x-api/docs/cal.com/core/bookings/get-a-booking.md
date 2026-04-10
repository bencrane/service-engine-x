<!-- Source: https://cal.com/docs/api-reference/v2/bookings/get-a-booking -->

# Get a booking - Cal.com Docs

Bookings
# Get a booking
Copy page

`:bookingUid` can be

- 

uid of a normal booking

- 

uid of one of the recurring booking recurrences

- 

uid of recurring booking which will return an array of all recurring booking recurrences (stored as recurringBookingUid on one of the individual recurrences).

If you are fetching a seated booking for an event type with ‘show attendees’ disabled, then to retrieve attendees in the response either set ‘show attendees’ to true on event type level or
you have to provide an authentication method of event type owner, host, team admin or owner or org admin or owner.
Please make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pageGET/v2/bookings/{bookingUid}Try itGet a booking

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/bookings/{bookingUid} \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": {
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
}`
```

#### Headers
​cal-api-versionstringdefault:2026-02-25required

Must be set to 2026-02-25.​Authorizationstring

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​bookingUidstringrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Booking data, which can be either a BookingOutput object, a RecurringBookingOutput object, or an array of RecurringBookingOutput objects
- Option 1 · object
- Option 2 · object
- Option 3 · object[]
- Option 4 · object
- Option 5 · object
- Option 6 · object[]

Show child attributes
