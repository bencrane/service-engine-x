<!-- Source: https://cal.com/docs/api-reference/v2/bookings-attendees/get-a-specific-attendee-for-a-booking -->

# Get a specific attendee for a booking - Cal.com Docs

Attendees
# Get a specific attendee for a booking
Copy page

Retrieve a specific attendee by their ID for a booking identified by its UID.
The cal-api-version header is required for this endpoint. Without it, the request will fail with a 404 error.Copy pageGET/v2/bookings/{bookingUid}/attendees/{attendeeId}Try itGet a specific attendee for a booking

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/bookings/{bookingUid}/attendees/{attendeeId} \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": {
    "name": "John Doe",
    "email": "[email protected]",
    "displayEmail": "[email protected]",
    "timeZone": "America/New_York",
    "absent": false,
    "id": 251,
    "language": "en",
    "phoneNumber": "+1234567890"
  }
}`
```

#### Headers
​cal-api-versionstringrequired

Must be set to 2024-08-13. This header is required as this endpoint does not exist in older API versions.​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​bookingUidstringrequired​attendeeIdnumberrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
