<!-- Source: https://cal.com/docs/api-reference/v2/oauth2/get-oauth2-client -->

# Get OAuth2 client - Cal.com Docs

OAuth2
# Get OAuth2 client
Copy page

Returns the OAuth2 client information for the given client IDCopy pageGET/v2/auth/oauth2/clients/{clientId}Try itGet OAuth2 client

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/auth/oauth2/clients/{clientId} \
  --header 'Authorization: Bearer <token>'`
```
200
```
`{
  "status": "success",
  "data": {
    "client_id": "clxxxxxxxxxxxxxxxx",
    "redirect_uris": [
      "https://example.com/callback"
    ],
    "name": "My App",
    "is_trusted": false,
    "client_type": "CONFIDENTIAL",
    "logo": "<string>"
  }
}`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Path Parameters
​clientIdstringrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
