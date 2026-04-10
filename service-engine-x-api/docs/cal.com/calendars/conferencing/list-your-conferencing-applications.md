<!-- Source: https://cal.com/docs/api-reference/v2/conferencing/list-your-conferencing-applications -->

# List your conferencing applications - Cal.com Docs

Conferencing
# List your conferencing applications
Copy pageCopy pageGET/v2/conferencingTry itList your conferencing applications

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/conferencing \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "id": 123,
      "type": "google_video",
      "userId": 123,
      "invalid": true
    }
  ]
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` ​dataobject[]required

Show child attributes
