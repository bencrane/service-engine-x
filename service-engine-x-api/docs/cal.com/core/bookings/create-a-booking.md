<!-- Source: https://cal.com/docs/api-reference/v2/bookings/create-a-booking -->

# Create a booking - Cal.com Docs

Bookings
# Create a booking
Copy page

POST /v2/bookings is used to create regular bookings, recurring bookings and instant bookings. The request bodies for all 3 are almost the same except:
If eventTypeId in the request body is id of a regular event, then regular booking is created.

If it is an id of a recurring event type, then recurring booking is created.

Meaning that the request bodies are equal but the outcome depends on what kind of event type it is with the goal of making it as seamless for developers as possible.

For team event types it is possible to create instant meeting. To do that just pass `"instant": true` to the request body.

The start needs to be in UTC aka if the timezone is GMT+2 in Rome and meeting should start at 11, then UTC time should have hours 09:00 aka without time zone.

Finally, there are 2 ways to book an event type belonging to an individual user:

- Provide `eventTypeId` in the request body.

- Provide `eventTypeSlug` and `username` and optionally `organizationSlug` if the user with the username is within an organization.

And 2 ways to book and event type belonging to a team:

- Provide `eventTypeId` in the request body.

- Provide `eventTypeSlug` and `teamSlug` and optionally `organizationSlug` if the team with the teamSlug is within an organization.

If you are creating a seated booking for an event type with ‘show attendees’ disabled, then to retrieve attendees in the response either set ‘show attendees’ to true on event type level or
you have to provide an authentication method of event type owner, host, team admin or owner or org admin or owner.

For event types that have SMS reminders workflow, you need to pass the attendee’s phone number in the request body via `attendee.phoneNumber` (e.g., “+19876543210” in international format). This is an optional field, but becomes required when SMS reminders are enabled for the event type. For the complete attendee object structure, see the attendee object documentation.
Please make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pagePOST/v2/bookingsTry itCreate a booking

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/bookings \
  --header 'Content-Type: application/json' \
  --header 'cal-api-version: <cal-api-version>' \
  --data '
{
  "start": "2024-08-13T09:00:00Z",
  "attendee": {
    "name": "John Doe",
    "timeZone": "America/New_York",
    "phoneNumber": "+919876543210",
    "language": "it",
    "email": "[email protected]"
  },
  "bookingFieldsResponses": {
    "customField": "customValue"
  },
  "eventTypeId": 123,
  "eventTypeSlug": "my-event-type",
  "username": "john-doe",
  "teamSlug": "john-doe",
  "organizationSlug": "acme-corp",
  "guests": [
    "[email protected]",
    "[email protected]"
  ],
  "meetingUrl": "https://example.com/meeting",
  "location": {
    "type": "address"
  },
  "metadata": {
    "key": "value"
  },
  "lengthInMinutes": 30,
  "routing": {
    "responseId": 123,
    "teamMemberIds": [
      101,
      102
    ]
  },
  "emailVerificationCode": "123456",
  "allowConflicts": true,
  "allowBookingOutOfBounds": true
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
#### Body
application/json

Accepts different types of booking input: Create Booking (Option 1), Create Instant Booking (Option 2), or Create Recurring Booking (Option 3)
- Option 1
- Option 2
- Option 3​startstring<date-time>required

The start time of the booking in ISO 8601 format in UTC timezone.Example:

`"2024-08-13T09:00:00Z"`​attendeeobjectrequired

The attendee's details.

Show child attributes​bookingFieldsResponsesobject

Booking field responses consisting of an object with booking field slug as keys and user response as values for custom booking fields added by you.Example:
```
`{ "customField": "customValue" }`
```
​eventTypeIdnumber

The ID of the event type that is booked. Required unless eventTypeSlug and username are provided as an alternative to identifying the event type.Example:

`123`​eventTypeSlugstring

The slug of the event type. Required along with username / teamSlug and optionally organizationSlug if eventTypeId is not provided.Example:

`"my-event-type"`​usernamestring

The username of the event owner. Required along with eventTypeSlug and optionally organizationSlug if eventTypeId is not provided.Example:

`"john-doe"`​teamSlugstring

Team slug for team that owns event type for which slots are fetched. Required along with eventTypeSlug and optionally organizationSlug if the team is part of organizationExample:

`"john-doe"`​organizationSlugstring

The organization slug. Optional, only used when booking with eventTypeSlug + username or eventTypeSlug + teamSlug.Example:

`"acme-corp"`​guestsstring[]

An optional list of guest emails attending the event.Example:
```
`["[email protected]", "[email protected]"]`
```
​meetingUrlstringdeprecated

Deprecated - use 'location' instead. Meeting URL just for this booking. Displayed in email and calendar event. If not provided then cal video link will be generated.Example:

`"https://example.com/meeting"`​locationobject

One of the event type locations. If instead of passing one of the location objects as required by schema you are still passing a string please use an object.
- Option 1
- Option 2
- Option 3
- Option 4
- Option 5
- Option 6
- Option 7
- Option 8

Show child attributes​metadataobject

You can store any additional data you want here. Metadata must have at most 50 keys, each key up to 40 characters, and string values up to 500 characters.Example:
```
`{ "key": "value" }`
```
​lengthInMinutesnumber

If it is an event type that has multiple possible lengths that attendee can pick from, you can pass the desired booking length here.
If not provided then event type default length will be used for the booking.Example:

`30`​routingobject

Routing information from routing forms that determined the booking assignment. Both responseId and teamMemberIds are required if provided.

Show child attributesExample:
```
`{
  "responseId": 123,
  "teamMemberIds": [101, 102]
}`
```
​emailVerificationCodestring

Email verification code required when event type has email verification enabled.Example:

`"123456"`​allowConflictsboolean

When true and the authenticated user is a host of the event type, availability conflict checks are bypassed. If the user is not a host or is unauthenticated, this parameter is silently ignored.Example:

`true`​allowBookingOutOfBoundsboolean

When true and the authenticated user is a host of the event type, booking time out-of-bounds checks are bypassed allowing bookings outside the normally permitted scheduling window. If the user is not a host or is unauthenticated, this parameter is silently ignored. Only supported on the 2026-02-25 API version.Example:

`true`
#### Response
201 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Booking data, which can be either a BookingOutput object or an array of RecurringBookingOutput objects
- Option 1 · object
- Option 2 · object[]
- Option 3 · object
- Option 4 · object[]

Show child attributes
