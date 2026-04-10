<!-- Source: https://cal.com/docs/api-reference/v2/bookings/get-all-the-recordings-for-the-booking -->

# Get all the recordings for the booking - Cal.com Docs

Bookings
# Get all the recordings for the booking
Copy page

Fetches all the recordings for the booking `:bookingUid`. Requires authentication and proper authorization. Access is granted if you are the booking organizer, team admin or org admin/owner.
cal-api-version: `2026-02-25` is required in the request header.Copy pageGET/v2/bookings/{bookingUid}/recordingsTry itGet all the recordings for the booking

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/bookings/{bookingUid}/recordings \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "id": "1234567890",
      "roomName": "daily-video-room-123",
      "startTs": 1678901234,
      "status": "completed",
      "duration": 3600,
      "shareToken": "share-token-123",
      "maxParticipants": 10,
      "downloadLink": "https://cal-video-recordings.s3.us-east-2.amazonaws.com/meetco/123s",
      "error": "Error message"
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
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Show child attributes
