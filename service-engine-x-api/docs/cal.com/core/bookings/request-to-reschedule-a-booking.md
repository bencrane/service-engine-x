<!-- Source: https://cal.com/docs/api-reference/v2/bookings/request-to-reschedule-a-booking -->

# Request to reschedule a booking - Cal.com Docs

Bookings
# Request to reschedule a booking
Copy page

Request to reschedule a booking. The booking will be cancelled and the attendee will receive an email with a link to reschedule.
Please make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pagePOST/v2/bookings/{bookingUid}/request-rescheduleTry itRequest to reschedule a booking

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/bookings/{bookingUid}/request-reschedule \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --header 'cal-api-version: <cal-api-version>' \
  --data '
{
  "rescheduleReason": "I need to reschedule due to a conflict"
}
'`
```
200
```
`{
  "status": "success"
}`
```

#### Headers
​cal-api-versionstringdefault:2026-02-25required

Must be set to 2026-02-25.​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​bookingUidstringrequired
#### Body
application/json​rescheduleReasonstring

Reason for requesting to reschedule the bookingExample:

`"I need to reschedule due to a conflict"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`
