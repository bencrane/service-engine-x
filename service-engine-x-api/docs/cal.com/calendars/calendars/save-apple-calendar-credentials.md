<!-- Source: https://cal.com/docs/api-reference/v2/calendars/save-apple-calendar-credentials -->

# Save Apple calendar credentials - Cal.com Docs

Calendars
# Save Apple calendar credentials
Copy pageCopy pagePOST/v2/calendars/{calendar}/credentialsTry itSave Apple calendar credentials

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/calendars/{calendar}/credentials \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "username": "<string>",
  "password": "<string>"
}
'`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​calendarenum<string>requiredAvailable options: `apple` 
#### Body
application/json​usernamestringrequired​passwordstringrequired
#### Response
201 - undefined
