<!-- Source: https://cal.com/docs/api-reference/v2/organization-team-verified-resources/request-email-verification-code -->

# Request email verification code - Cal.com Docs

Organization Team Verified Resources
# Request email verification code
Copy page

Sends a verification code to the email. Required membership role: `team admin`. PBAC permission: `team.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePOST/v2/organizations/{orgId}/teams/{teamId}/verified-resources/emails/verification-code/requestTry itRequest email verification code

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/verified-resources/emails/verification-code/request \
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
#### Path Parameters
​teamIdnumberrequired​orgIdnumberrequired
#### Body
application/json​emailstringrequired

Email to verify.Example:

`"[email protected]"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`
