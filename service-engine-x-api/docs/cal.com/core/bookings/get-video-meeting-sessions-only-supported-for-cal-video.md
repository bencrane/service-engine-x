<!-- Source: https://cal.com/docs/api-reference/v2/bookings/get-video-meeting-sessions-only-supported-for-cal-video -->

# Get Video Meeting Sessions. Only supported for Cal Video - Cal.com Docs

Bookings
# Get Video Meeting Sessions. Only supported for Cal Video
Copy page

Requires authentication and proper authorization. Access is granted if you are the booking organizer, team admin or org admin/owner.
cal-api-version: `2026-02-25` is required in the request header.Copy pageGET/v2/bookings/{bookingUid}/conferencing-sessionsTry itGet Video Meeting Sessions. Only supported for Cal Video

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/bookings/{bookingUid}/conferencing-sessions \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "id": "session123",
      "room": "daily-video-room-123",
      "startTime": 1678901234,
      "duration": 3600,
      "ongoing": false,
      "maxParticipants": 10,
      "participants": [
        {
          "userId": "user123",
          "userName": "John Doe",
          "joinTime": 1678901234,
          "duration": 3600
        }
      ]
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
