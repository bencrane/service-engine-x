<!-- Source: https://cal.com/docs/api-reference/v2/bookings/get-booking-references -->

# Get booking references - Cal.com Docs

Bookings
# Get booking references
Copy pagePlease make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pageGET/v2/bookings/{bookingUid}/referencesTry itGet booking references

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/bookings/{bookingUid}/references \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "type": "<string>",
      "eventUid": "<string>",
      "destinationCalendarId": "<string>",
      "id": 123
    }
  ]
}`
```

#### Headers
​cal-api-versionstringdefault:2026-02-25required

Must be set to 2026-02-25.​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​bookingUidstringrequired
#### Query Parameters
​typeenum<string>

Filter booking references by typeAvailable options: `google_calendar`, `office365_calendar`, `daily_video`, `google_video`, `office365_video`, `zoom_video` Example:

`"google_calendar"`
#### Response
200 - application/json​statusenum<string>required

The status of the request, always 'success' for successful responsesAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Booking References

Show child attributes
