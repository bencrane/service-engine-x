<!-- Source: https://cal.com/docs/api-reference/v2/verified-resources/request-email-verification-code -->

# Request email verification code - Cal.com Docs

Verified Resources
# Request email verification code
Copy page

Sends a verification code to the emailCopy pagePOST/v2/verified-resources/emails/verification-code/requestTry itRequest email verification code

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/verified-resources/emails/verification-code/request \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "email": "[email protected]"
}
'`
```
200
```
`{
  "status": "success"
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Body
application/json​emailstringrequired

Email to verify.Example:

`"[email protected]"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`
