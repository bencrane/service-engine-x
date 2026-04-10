<!-- Source: https://cal.com/docs/api-reference/v2/cal-unified-calendars/get-meeting-details-from-calendar -->

# Get meeting details from calendar - Cal.com Docs

Cal Unified Calendars
# Get meeting details from calendar
Copy page

Returns detailed information about a meeting including attendance metricsCopy pageGET/v2/calendars/{calendar}/event/{eventUid}Try itGet meeting details from calendar

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/calendars/{calendar}/event/{eventUid} \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": {
    "start": {
      "time": "2023-11-07T05:31:56Z",
      "timeZone": "<string>"
    },
    "end": {
      "time": "2023-11-07T05:31:56Z",
      "timeZone": "<string>"
    },
    "id": "<string>",
    "title": "<string>",
    "source": "google",
    "description": "<string>",
    "locations": [
      {
        "type": "video",
        "url": "<string>",
        "label": "<string>",
        "password": "<string>",
        "meetingCode": "<string>",
        "accessCode": "<string>"
      }
    ],
    "attendees": [
      {
        "email": "<string>",
        "name": "<string>",
        "responseStatus": "accepted",
        "self": true,
        "optional": true,
        "host": true
      }
    ],
    "status": "accepted",
    "hosts": [
      {
        "email": "<string>",
        "name": "<string>",
        "responseStatus": "accepted"
      }
    ],
    "calendarEventOwner": {
      "email": "<string>",
      "name": "<string>"
    }
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​calendarenum<string>requiredAvailable options: `google` ​eventUidstringrequired

The Google Calendar event ID. You can retrieve this by getting booking references from the following endpoints:

- 

For team events: https://cal.com/docs/api-reference/v2/orgs-teams-bookings/get-booking-references-for-a-booking

- 

For user events: https://cal.com/docs/api-reference/v2/bookings/get-booking-references-for-a-booking

#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
