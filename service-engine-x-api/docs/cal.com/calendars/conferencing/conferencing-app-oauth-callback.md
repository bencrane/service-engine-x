<!-- Source: https://cal.com/docs/api-reference/v2/conferencing/conferencing-app-oauth-callback -->

# Conferencing app OAuth callback - Cal.com Docs

Conferencing
# Conferencing app OAuth callback
Copy pageCopy pageGET/v2/conferencing/{app}/oauth/callbackTry itConferencing app OAuth callback

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/conferencing/{app}/oauth/callback \
  --header 'Authorization: Bearer <token>'`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Path Parameters
​appenum<string>required

Conferencing application typeAvailable options: `zoom`, `msteams` 
#### Query Parameters
​statestringrequired​codestringrequired
#### Response
200 - undefined
