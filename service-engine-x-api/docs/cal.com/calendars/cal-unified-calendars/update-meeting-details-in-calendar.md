<!-- Source: https://cal.com/docs/api-reference/v2/cal-unified-calendars/update-meeting-details-in-calendar -->

# Update meeting details in calendar - Cal.com Docs

Cal Unified Calendars
# Update meeting details in calendar
Copy page

Updates event information in the specified calendar providerCopy pagePATCH/v2/calendars/{calendar}/events/{eventUid}Try itUpdate meeting details in calendar

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/calendars/{calendar}/events/{eventUid} \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "start": {
    "time": "2023-11-07T05:31:56Z",
    "timeZone": "<string>"
  },
  "end": {
    "time": "2023-11-07T05:31:56Z",
    "timeZone": "<string>"
  },
  "title": "<string>",
  "description": "<string>",
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
  "status": "accepted"
}
'`
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

#### Body
application/json​startobject

Start date and time of the calendar event with timezone information

Show child attributes​endobject

End date and time of the calendar event with timezone information

Show child attributes​titlestring

Title of the calendar event​descriptionstring | null

Detailed description of the calendar event​attendeesobject[] | null

List of attendees. CAUTION: You must pass the entire array with all updated values. Any attendees not included in this array will be removed from the event.

Show child attributes​statusenum<string> | null

Status of the event (accepted, pending, declined, cancelled)Available options: `accepted`, `pending`, `declined`, `cancelled` Example:

`"accepted"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
