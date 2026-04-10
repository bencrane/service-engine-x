<!-- Source: https://cal.com/docs/api-reference/v2/organization-team-verified-resources/verify-an-email-for-an-org-team -->

# Verify an email for an org team - Cal.com Docs

Organization Team Verified Resources
# Verify an email for an org team
Copy page

Use code to verify an email. Required membership role: `team admin`. PBAC permission: `team.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePOST/v2/organizations/{orgId}/teams/{teamId}/verified-resources/emails/verification-code/verifyTry itVerify an email for an org team

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/verified-resources/emails/verification-code/verify \
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
    "teamId": 89,
    "userId": 45
  }
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

`"[email protected]"`​codestringrequired

verification code sent to the email to verifyExample:

`"1ABG2C"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
