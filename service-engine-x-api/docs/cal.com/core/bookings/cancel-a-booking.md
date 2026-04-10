<!-- Source: https://cal.com/docs/api-reference/v2/bookings/cancel-a-booking -->

# Cancel a booking - Cal.com Docs

Bookings
# Cancel a booking
Copy page

:bookingUid can be :bookingUid of an usual booking, individual recurrence or recurring booking to cancel all recurrences.

Cancelling normal bookings:
If the booking is not seated and not recurring, simply pass :bookingUid in the request URL `/bookings/:bookingUid/cancel` and optionally cancellationReason in the request body `{"cancellationReason": "Will travel"}`.

Cancelling seated bookings:
It is possible to cancel specific seat within a booking as an attendee or all of the seats as the host.

- 

As an attendee - provide :bookingUid in the request URL `/bookings/:bookingUid/cancel` and seatUid in the request body `{"seatUid": "123-123-123"}` . This will remove this particular attendance from the booking.

- 

As the host or org admin of host - host can cancel booking for all attendees aka for every seat, this also applies to org admins. Provide :bookingUid in the request URL `/bookings/:bookingUid/cancel` and cancellationReason in the request body `{"cancellationReason": "Will travel"}` and `Authorization: Bearer token` request header where token is event type owner (host) credential. This will cancel the booking for all attendees.

Cancelling recurring seated bookings:
For recurring seated bookings it is not possible to cancel all of them with 1 call
like with non-seated recurring bookings by providing recurring bookind uid - you have to cancel each recurrence booking by its bookingUid + seatUid.

If you are cancelling a seated booking for an event type with ‘show attendees’ disabled, then to retrieve attendees in the response either set ‘show attendees’ to true on event type level or
you have to provide an authentication method of event type owner, host, team admin or owner or org admin or owner.
Please make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pagePOST/v2/bookings/{bookingUid}/cancelTry itCancel a booking

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/bookings/{bookingUid}/cancel \
  --header 'Content-Type: application/json' \
  --header 'cal-api-version: <cal-api-version>' \
  --data '
{
  "cancellationReason": "User requested cancellation",
  "cancelSubsequentBookings": true
}
'`
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
#### Body
application/json

Accepts different types of cancel booking input: Cancel Booking (Option 1 which is for normal or recurring bookings) or Cancel Seated Booking (Option 2 which is for seated bookings)
- Option 1
- Option 2​cancellationReasonstringExample:

`"User requested cancellation"`​cancelSubsequentBookingsboolean

For recurring non-seated booking only - if true, cancel booking with the bookingUid of the individual recurrence and all recurrences that come after it.
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
