<!-- Source: https://cal.com/docs/api-reference/v2/organization-team-verified-resources/request-phone-number-verification-code -->

# Request phone number verification code - Cal.com Docs

Organization Team Verified Resources
# Request phone number verification code
Copy page

Sends a verification code to the phone number. Required membership role: `team admin`. PBAC permission: `team.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePOST/v2/organizations/{orgId}/teams/{teamId}/verified-resources/phones/verification-code/requestTry itRequest phone number verification code

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/verified-resources/phones/verification-code/request \
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
#### Path Parameters
​teamIdnumberrequired​orgIdnumberrequired
#### Body
application/json​phonestringrequired

Phone number to verify.Example:

`"+372 5555 6666"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`
