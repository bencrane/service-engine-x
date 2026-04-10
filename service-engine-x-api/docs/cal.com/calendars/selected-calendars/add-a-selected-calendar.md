<!-- Source: https://cal.com/docs/api-reference/v2/selected-calendars/add-a-selected-calendar -->

# Add a selected calendar - Cal.com Docs

Selected Calendars
# Add a selected calendar
Copy pageCopy pagePOST/v2/selected-calendarsTry itAdd a selected calendar

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/selected-calendars \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "integration": "<string>",
  "externalId": "<string>",
  "credentialId": 123,
  "delegationCredentialId": "<string>"
}
'`
```
201
```
`{
  "status": "success",
  "data": {
    "userId": 123,
    "integration": "<string>",
    "externalId": "<string>",
    "credentialId": 123
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Body
application/json​integrationstringrequired​externalIdstringrequired​credentialIdnumberrequired​delegationCredentialIdstring
#### Response
201 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
