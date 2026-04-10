<!-- Source: https://cal.com/docs/api-reference/v2/calendars/get-oauth-connect-url -->

# Get OAuth connect URL - Cal.com Docs

Calendars
# Get OAuth connect URL
Copy pageCopy pageGET/v2/calendars/{calendar}/connectTry itGet OAuth connect URL

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/calendars/{calendar}/connect \
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
​calendarenum<string>requiredAvailable options: `office365`, `google` 
#### Query Parameters
​isDryRunbooleanrequired​redirstring

Redirect URL after successful calendar authorization.
#### Response
200 - application/json

The response is of type `object`.
