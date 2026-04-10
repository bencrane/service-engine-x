<!-- Source: https://cal.com/docs/api-reference/v2/me/get-my-profile -->

# Get my profile - Cal.com Docs

Me
# Get my profile
Copy pageCopy pageGET/v2/meTry itGet my profile

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/me \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": {
    "id": 123,
    "username": "<string>",
    "email": "<string>",
    "name": "<string>",
    "avatarUrl": "<string>",
    "bio": "<string>",
    "timeFormat": 123,
    "defaultScheduleId": 123,
    "weekStart": "<string>",
    "timeZone": "<string>",
    "locale": "en",
    "organizationId": 123,
    "organization": {
      "isPlatform": true,
      "id": 123
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
