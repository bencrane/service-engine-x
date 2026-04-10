<!-- Source: https://cal.com/docs/api-reference/v2/calendars/save-an-ics-feed -->

# Save an ICS feed - Cal.com Docs

Calendars
# Save an ICS feed
Copy pageCopy pagePOST/v2/calendars/ics-feed/saveTry itSave an ICS feed

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/calendars/ics-feed/save \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "urls": [
    "https://cal.com/ics/feed.ics",
    "http://cal.com/ics/feed.ics"
  ],
  "readOnly": false
}
'`
```
201
```
`{
  "status": "success",
  "data": {
    "id": 1234567890,
    "type": "ics-feed_calendar",
    "userId": 1234567890,
    "teamId": 1234567890,
    "appId": "ics-feed",
    "invalid": false
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Body
application/json​urlsstring[]required

An array of ICS URLsExample:
```
`[
  "https://cal.com/ics/feed.ics",
  "http://cal.com/ics/feed.ics"
]`
```
​readOnlybooleandefault:true

Whether to allowing writing to the calendar or notExample:

`false`
#### Response
201 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
