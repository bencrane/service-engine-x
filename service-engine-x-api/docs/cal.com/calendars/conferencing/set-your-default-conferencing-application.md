<!-- Source: https://cal.com/docs/api-reference/v2/conferencing/set-your-default-conferencing-application -->

# Set your default conferencing application - Cal.com Docs

Conferencing
# Set your default conferencing application
Copy pageCopy pagePOST/v2/conferencing/{app}/defaultTry itSet your default conferencing application

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/conferencing/{app}/default \
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

Conferencing application typeAvailable options: `google-meet`, `zoom`, `msteams`, `daily-video` 
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`
