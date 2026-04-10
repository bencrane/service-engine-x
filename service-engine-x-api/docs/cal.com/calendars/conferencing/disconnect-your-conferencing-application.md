<!-- Source: https://cal.com/docs/api-reference/v2/conferencing/disconnect-your-conferencing-application -->

# Disconnect your conferencing application - Cal.com Docs

Conferencing
# Disconnect your conferencing application
Copy pageCopy pageDELETE/v2/conferencing/{app}/disconnectTry itDisconnect your conferencing application

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/conferencing/{app}/disconnect \
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

Conferencing application typeAvailable options: `google-meet`, `zoom`, `msteams` 
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`
