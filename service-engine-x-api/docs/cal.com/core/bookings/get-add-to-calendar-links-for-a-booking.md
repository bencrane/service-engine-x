<!-- Source: https://cal.com/docs/api-reference/v2/bookings/get-add-to-calendar-links-for-a-booking -->

# Get &#x27;Add to Calendar&#x27; links for a booking - Cal.com Docs

Bookings
# Get 'Add to Calendar' links for a booking
Copy page

Retrieve calendar links for a booking that can be used to add the event to various calendar services. Returns links for Google Calendar, Microsoft Office, Microsoft Outlook, and a downloadable ICS file.
Please make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pageGET/v2/bookings/{bookingUid}/calendar-linksTry itGet 'Add to Calendar' links for a booking

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/bookings/{bookingUid}/calendar-links \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "label": "<string>",
      "link": "<string>"
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
#### Response
200 - application/json​statusenum<string>required

The status of the request, always 'success' for successful responsesAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Calendar links for the booking

Show child attributes
