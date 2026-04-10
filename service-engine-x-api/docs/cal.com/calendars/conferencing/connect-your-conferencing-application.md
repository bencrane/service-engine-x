<!-- Source: https://cal.com/docs/api-reference/v2/conferencing/connect-your-conferencing-application -->

# Connect your conferencing application - Cal.com Docs

Conferencing
# Connect your conferencing application
Copy pageCopy pagePOST/v2/conferencing/{app}/connectTry itConnect your conferencing application

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/conferencing/{app}/connect \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": {
    "id": 123,
    "type": "google_video",
    "userId": 123,
    "invalid": true
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​appenum<string>required

Conferencing application typeAvailable options: `google-meet` 
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` ​dataobjectrequired

Show child attributes
