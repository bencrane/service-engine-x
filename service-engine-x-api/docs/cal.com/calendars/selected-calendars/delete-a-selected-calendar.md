<!-- Source: https://cal.com/docs/api-reference/v2/selected-calendars/delete-a-selected-calendar -->

# Delete a selected calendar - Cal.com Docs

Selected Calendars
# Delete a selected calendar
Copy pageCopy pageDELETE/v2/selected-calendarsTry itDelete a selected calendar

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/selected-calendars \
  --header 'Authorization: <authorization>'`
```
200
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
#### Query Parameters
​integrationstringrequired​externalIdstringrequired​credentialIdstringrequired​delegationCredentialIdstring
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
