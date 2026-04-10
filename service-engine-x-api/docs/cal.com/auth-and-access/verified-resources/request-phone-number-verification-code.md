<!-- Source: https://cal.com/docs/api-reference/v2/verified-resources/request-phone-number-verification-code -->

# Request phone number verification code - Cal.com Docs

Verified Resources
# Request phone number verification code
Copy page

Sends a verification code to the phone numberCopy pagePOST/v2/verified-resources/phones/verification-code/requestTry itRequest phone number verification code

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/verified-resources/phones/verification-code/request \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "phone": "+372 5555 6666"
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
application/json​phonestringrequired

Phone number to verify.Example:

`"+372 5555 6666"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`
