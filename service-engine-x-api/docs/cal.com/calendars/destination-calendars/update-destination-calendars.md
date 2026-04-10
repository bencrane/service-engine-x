<!-- Source: https://cal.com/docs/api-reference/v2/destination-calendars/update-destination-calendars -->

# Update destination calendars - Cal.com Docs

Destination Calendars
# Update destination calendars
Copy pageCopy pagePUT/v2/destination-calendarsTry itUpdate destination calendars

cURL
```
`curl --request PUT \
  --url https://api.cal.com/v2/destination-calendars \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "integration": "apple_calendar",
  "externalId": "https://caldav.icloud.com/26962146906/calendars/1644422A-1945-4438-BBC0-4F0Q23A57R7S/",
  "delegationCredentialId": "<string>"
}
'`
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
#### Body
application/json​integrationenum<string>required

The calendar service you want to integrate, as returned by the /calendars endpointAvailable options: `apple_calendar`, `google_calendar`, `office365_calendar` Example:

`"apple_calendar"`​externalIdstringrequired

Unique identifier used to represent the specific calendar, as returned by the /calendars endpointExample:

`"https://caldav.icloud.com/26962146906/calendars/1644422A-1945-4438-BBC0-4F0Q23A57R7S/"`​delegationCredentialIdstring
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
