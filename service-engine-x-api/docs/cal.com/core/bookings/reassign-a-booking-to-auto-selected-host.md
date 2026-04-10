<!-- Source: https://cal.com/docs/api-reference/v2/bookings/reassign-a-booking-to-auto-selected-host -->

# Reassign a booking to auto-selected host - Cal.com Docs

Bookings
# Reassign a booking to auto-selected host
Copy page

Currently only supports reassigning host for round robin bookings. The provided authorization header refers to the owner of the booking.
Please make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pagePOST/v2/bookings/{bookingUid}/reassignTry itReassign a booking to auto-selected host

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/bookings/{bookingUid}/reassign \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": "<unknown>"
}`
```

#### Headers
​cal-api-versionstringdefault:2026-02-25required

Must be set to 2026-02-25.​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​bookingUidstringrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataanyrequired

Booking data, which can be either a ReassignAutoBookingOutput object or a ReassignManualBookingOutput object
