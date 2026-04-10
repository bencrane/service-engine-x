<!-- Source: https://cal.com/docs/api-reference/v2/bookings/reschedule-a-booking -->

# Reschedule a booking - Cal.com Docs

Bookings
# Reschedule a booking
Copy page

Reschedule a booking or seated booking
Please make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pagePOST/v2/bookings/{bookingUid}/rescheduleTry itReschedule a booking

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/bookings/{bookingUid}/reschedule \
  --header 'Content-Type: application/json' \
  --header 'cal-api-version: <cal-api-version>' \
  --data '
{
  "start": "2024-08-13T10:00:00Z",
  "rescheduledBy": "<string>",
  "reschedulingReason": "User requested reschedule",
  "emailVerificationCode": "123456"
}
'`
```
201
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
#### Body
application/json

Accepts different types of reschedule booking input: Reschedule Booking (Option 1) or Reschedule Seated Booking (Option 2). If you're rescheduling a seated booking as org admin of booking host, pass booking input for Reschedule Booking (Option 1) along with your access token in the request header.

```
`If you are rescheduling a seated booking for an event type with 'show attendees' disabled, then to retrieve attendees in the response either set 'show attendees' to true on event type level or
  you have to provide an authentication method of event type owner, host, team admin or owner or org admin or owner.`
```

- Option 1
- Option 2​startstring<date-time>required

Start time in ISO 8601 format for the new bookingExample:

`"2024-08-13T10:00:00Z"`​rescheduledBystring

Email of the person who is rescheduling the booking - only needed when rescheduling a booking that requires a confirmation.
If event type owner email is provided then rescheduled booking will be automatically confirmed. If attendee email or no email is passed then the event type
owner will have to confirm the rescheduled booking.​reschedulingReasonstring

Reason for rescheduling the bookingExample:

`"User requested reschedule"`​emailVerificationCodestring

Email verification code required when event type has email verification enabled.Example:

`"123456"`
#### Response
201 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Booking data, which can be either a BookingOutput object or a RecurringBookingOutput object
- Option 1
- Option 2
- Option 3
- Option 4

Show child attributes
