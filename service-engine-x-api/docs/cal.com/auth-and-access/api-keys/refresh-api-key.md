<!-- Source: https://cal.com/docs/api-reference/v2/api-keys/refresh-api-key -->

# Refresh API Key - Cal.com Docs

Api Keys
# Refresh API Key
Copy pageGenerate a new API key and delete the current one. Provide API key to refresh as a Bearer token in the Authorization header (e.g. "Authorization: Bearer <apiKey>").Copy pagePOST/v2/api-keys/refreshTry itRefresh API Key

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/api-keys/refresh \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "apiKeyDaysValid": 60,
  "apiKeyNeverExpires": true
}
'`
```
200
```
`{
  "status": "success",
  "data": {
    "apiKey": "<string>"
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_
#### Body
application/json​apiKeyDaysValidnumberdefault:30

For how many days is managed organization api key valid. Defaults to 30 days.Required range: `x >= 1`Example:

`60`​apiKeyNeverExpiresboolean

If true, organization api key never expires.Example:

`true`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
