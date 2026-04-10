<!-- Source: https://cal.com/docs/api-reference/v2/calendars/check-a-calendar-connection -->

# Check a calendar connection - Cal.com Docs

Calendars
# Check a calendar connection
Copy pageCopy pageGET/v2/calendars/{calendar}/checkTry itCheck a calendar connection

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/calendars/{calendar}/check \
  --header 'Authorization: <authorization>'`
```
200
```
`{}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​calendarenum<string>requiredAvailable options: `apple`, `google`, `office365` 
#### Response
200 - application/json

The response is of type `object`.
