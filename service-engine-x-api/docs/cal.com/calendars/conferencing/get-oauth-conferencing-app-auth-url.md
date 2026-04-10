<!-- Source: https://cal.com/docs/api-reference/v2/conferencing/get-oauth-conferencing-app-auth-url -->

# Get OAuth conferencing app auth URL - Cal.com Docs

Conferencing
# Get OAuth conferencing app auth URL
Copy pageCopy pageGET/v2/conferencing/{app}/oauth/auth-urlTry itGet OAuth conferencing app auth URL

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/conferencing/{app}/oauth/auth-url \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success"
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​appenum<string>required

Conferencing application typeAvailable options: `zoom`, `msteams` 
#### Query Parameters
​returnTostringrequired​onErrorReturnTostringrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`
