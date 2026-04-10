<!-- Source: https://cal.com/docs/api-reference/v2/calendars/get-all-calendars -->

# Get all calendars - Cal.com Docs

Calendars
# Get all calendars
Copy pageCopy pageGET/v2/calendarsTry itGet all calendars

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/calendars \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": {
    "connectedCalendars": [
      {
        "integration": {
          "name": "<string>",
          "description": "<string>",
          "type": "<string>",
          "variant": "<string>",
          "categories": [
            "<string>"
          ],
          "logo": "<string>",
          "publisher": "<string>",
          "slug": "<string>",
          "url": "<string>",
          "email": "<string>",
          "locationOption": {
            "label": "Google Meet",
            "value": "integrations:google:meet",
            "icon": "<string>",
            "disabled": false
          },
          "appData": {},
          "dirName": "<string>",
          "__template": "<string>",
          "installed": true,
          "title": "<string>",
          "category": "<string>"
        },
        "credentialId": 123,
        "delegationCredentialId": "<string>",
        "primary": {
          "externalId": "<string>",
          "primary": true,
          "readOnly": true,
          "isSelected": true,
          "credentialId": 123,
          "integration": "<string>",
          "name": "<string>",
          "email": "<string>",
          "delegationCredentialId": "<string>"
        },
        "calendars": [
          {
            "externalId": "<string>",
            "readOnly": true,
            "isSelected": true,
            "credentialId": 123,
            "integration": "<string>",
            "name": "<string>",
            "primary": true,
            "email": "<string>",
            "delegationCredentialId": "<string>"
          }
        ]
      }
    ],
    "destinationCalendar": {
      "id": 123,
      "integration": "<string>",
      "externalId": "<string>",
      "primaryEmail": "<string>",
      "userId": 123,
      "eventTypeId": 123,
      "credentialId": 123,
      "delegationCredentialId": "<string>",
      "name": "<string>",
      "primary": true,
      "readOnly": true,
      "email": "<string>",
      "integrationTitle": "<string>"
    }
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
