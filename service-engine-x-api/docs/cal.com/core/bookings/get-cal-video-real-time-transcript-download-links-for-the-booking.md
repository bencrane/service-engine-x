<!-- Source: https://cal.com/docs/api-reference/v2/bookings/get-cal-video-real-time-transcript-download-links-for-the-booking -->

# Get Cal Video real time transcript download links for the booking - Cal.com Docs

Bookings
# Get Cal Video real time transcript download links for the booking
Copy page

Fetches all the transcript download links for the booking `:bookingUid`

Transcripts are generated when clicking “Transcribe” during a Cal Video meeting. Download links are valid for 1 hour only - make a new request to generate fresh links after expiration.

Please make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pageGET/v2/bookings/{bookingUid}/transcriptsTry itGet Cal Video real time transcript download links for the booking

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/bookings/{bookingUid}/transcripts \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": [
    "https://transcript1.com",
    "https://transcript2.com"
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
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​datastring[]requiredExample:
```
`[
  "https://transcript1.com",
  "https://transcript2.com"
]`
```
