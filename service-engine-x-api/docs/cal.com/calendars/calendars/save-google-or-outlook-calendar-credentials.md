<!-- Source: https://cal.com/docs/api-reference/v2/calendars/save-google-or-outlook-calendar-credentials -->

# Save Google or Outlook calendar credentials - Cal.com Docs

Calendars
# Save Google or Outlook calendar credentials
Copy pageCopy pageGET/v2/calendars/{calendar}/saveTry itSave Google or Outlook calendar credentials

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/calendars/{calendar}/save \
  --header 'Authorization: Bearer <token>'`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Path Parameters
​calendarenum<string>requiredAvailable options: `office365`, `google` 
#### Query Parameters
​statestringrequired​codestringrequired
#### Response
200 - undefined
