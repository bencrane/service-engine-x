<!-- Source: https://cal.com/docs/api-reference/v2/deprecated:-platform-managed-users/refresh-managed-user-tokens -->

# Refresh managed user tokens - Cal.com Docs

Platform / Managed Users
# Refresh managed user tokens
Copy page

These endpoints are deprecated and will be removed in the future. If managed user access token is expired then get a new one using this endpoint - it will also refresh the refresh token, because we use
“refresh token rotation” mechanism. Access token is valid for 60 minutes and refresh token for 1 year. Make sure to store them in your database, for example, in your User database model `calAccessToken` and `calRefreshToken` fields.
Response also contains `accessTokenExpiresAt` and `refreshTokenExpiresAt` fields, but if you decode the jwt token the payload will contain `clientId` (OAuth client ID), `ownerId` (user to whom token belongs ID), `iat` (issued at time) and `expiresAt` (when does the token expire) fields.Copy pagePOST/v2/oauth/{clientId}/refreshTry itRefresh managed user tokens

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/oauth/{clientId}/refresh \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --header 'x-cal-secret-key: <x-cal-secret-key>' \
  --data '
{
  "refreshToken": "<string>"
}
'`
```
200
```
`{
  "status": "success",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
    "accessTokenExpiresAt": 123,
    "refreshTokenExpiresAt": 123
  }
}`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Headers
​x-cal-secret-keystringrequired

OAuth client secret key.
#### Path Parameters
​clientIdstringrequired
#### Body
application/json​refreshTokenstringrequired

Managed user's refresh token.
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
