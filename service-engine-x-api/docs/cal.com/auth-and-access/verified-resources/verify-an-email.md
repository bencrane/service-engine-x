<!-- Source: https://cal.com/docs/api-reference/v2/verified-resources/verify-an-email -->

# Verify an email - Cal.com Docs

Verified Resources
# Verify an email
Copy page

Use code to verify an emailCopy pagePOST/v2/verified-resources/emails/verification-code/verifyTry itVerify an email

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/verified-resources/emails/verification-code/verify \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "email": "[email protected]",
  "code": "1ABG2C"
}
'`
```
200
```
`{
  "status": "success",
  "data": {
    "id": 789,
    "email": "[email protected]",
    "userId": 45
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Body
application/json​emailstringrequired

Email to verify.Example:

`"[email protected]"`​codestringrequired

verification code sent to the email to verifyExample:

`"1ABG2C"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
