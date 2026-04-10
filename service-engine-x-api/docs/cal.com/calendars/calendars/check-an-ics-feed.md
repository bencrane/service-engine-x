<!-- Source: https://cal.com/docs/api-reference/v2/calendars/check-an-ics-feed -->

# Check an ICS feed - Cal.com Docs

Calendars
# Check an ICS feed
Copy pageCopy pageGET/v2/calendars/ics-feed/checkTry itCheck an ICS feed

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/calendars/ics-feed/check \
  --header 'Authorization: <authorization>'`
```
200
```
`{}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Response
200 - application/json

The response is of type `object`.
