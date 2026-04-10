<!-- Source: https://cal.com/docs/api-reference/v2/calendars/disconnect-a-calendar -->

# Disconnect a calendar - Cal.com Docs

Calendars
# Disconnect a calendar
Copy pageCopy pagePOST/v2/calendars/{calendar}/disconnectTry itDisconnect a calendar

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/calendars/{calendar}/disconnect \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '{
  "id": 10
}'`
```
200
```
`{
  "status": "success",
  "data": {
    "id": 123,
    "type": "<string>",
    "userId": 123,
    "teamId": 123,
    "appId": "<string>",
    "invalid": true
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​calendarenum<string>requiredAvailable options: `apple`, `google`, `office365` 
#### Body
application/json​idintegerrequired

Credential ID of the calendar to delete, as returned by the /calendars endpointExample:

`10`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
