<!-- Source: https://cal.com/docs/api-reference/v2/oauth2/exchange-authorization-code-or-refresh-token-for-tokens -->

# Exchange authorization code or refresh token for tokens - Cal.com Docs

OAuth2
# Exchange authorization code or refresh token for tokens
Copy page

RFC 6749-compliant token endpoint. Pass client_id in the request body (Section 2.3.1). Use grant_type ‘authorization_code’ to exchange an auth code for tokens, or ‘refresh_token’ to refresh an access token. Accepts both application/x-www-form-urlencoded (standard per RFC 6749 Section 4.1.3) and application/json content types.Copy pagePOST/v2/auth/oauth2/tokenTry itExchange authorization code or refresh token for tokens

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/auth/oauth2/token \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "client_id": "my-client-id",
  "grant_type": "authorization_code",
  "code": "abc123",
  "redirect_uri": "https://example.com/callback",
  "client_secret": "<string>"
}
'`
```
200
```
`{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800,
  "scope": "BOOKING_READ BOOKING_WRITE"
}`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Body
application/json

Token request body. client_id is required. Accepts application/x-www-form-urlencoded (RFC 6749 standard) or application/json. Use grant_type 'authorization_code' with client_secret (confidential) or code_verifier (public/PKCE), or grant_type 'refresh_token' with client_secret (confidential) or just the refresh_token (public).
- Option 1
- Option 2
- Option 3
- Option 4​client_idstringrequired

The client identifierExample:

`"my-client-id"`​grant_typeenum<string>required

The grant type — must be 'authorization_code'Available options: `authorization_code` Example:

`"authorization_code"`​codestringrequired

The authorization code received from the authorize endpointExample:

`"abc123"`​redirect_uristringrequired

The redirect URI used in the authorization requestExample:

`"https://example.com/callback"`​client_secretstringrequired

The client secret for confidential clients
#### Response
200 - application/json​access_tokenstringrequired

The access tokenExample:

`"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."`​token_typestringrequired

The token typeExample:

`"bearer"`​refresh_tokenstringrequired

The refresh tokenExample:

`"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."`​expires_innumberrequired

The number of seconds until the access token expiresExample:

`1800`​scopestringrequired

The granted scopes (space-delimited per RFC 6749)Example:

`"BOOKING_READ BOOKING_WRITE"`
