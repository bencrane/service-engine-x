<!-- Source: https://cal.com/docs/api-reference/v2/verified-resources/verify-a-phone-number -->

# Verify a phone number - Cal.com Docs

Verified Resources
# Verify a phone number
Copy page

Use code to verify a phone numberCopy pagePOST/v2/verified-resources/phones/verification-code/verifyTry itVerify a phone number

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/verified-resources/phones/verification-code/verify \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "phone": "+37255556666",
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
    "phoneNumber": "+37255556666",
    "userId": 45
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Body
application/json​phonestringrequired

phone number to verify.Example:

`"+37255556666"`​codestringrequired

verification code sent to the phone number to verifyExample:

`"1ABG2C"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
