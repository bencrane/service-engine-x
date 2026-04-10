<!-- Source: https://cal.com/docs/api-reference/v2/conferencing/get-your-default-conferencing-application -->

# Get your default conferencing application - Cal.com Docs

Conferencing
# Get your default conferencing application
Copy pageCopy pageGET/v2/conferencing/defaultTry itGet your default conferencing application

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/conferencing/default \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": {
    "appSlug": "<string>",
    "appLink": "<string>"
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject

Show child attributes
