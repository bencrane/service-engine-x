<!-- Source: https://cal.com/docs/api-reference/v2/organization-team-verified-resources/get-list-of-verified-emails-of-an-org-team -->

# Get list of verified emails of an org team - Cal.com Docs

Organization Team Verified Resources
# Get list of verified emails of an org team
Copy page

Required membership role: `team admin`. PBAC permission: `team.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/teams/{teamId}/verified-resources/emailsTry itGet list of verified emails of an org team

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/verified-resources/emails \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "id": 789,
      "email": "[email protected]",
      "teamId": 89,
      "userId": 45
    }
  ]
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​teamIdnumberrequired​orgIdnumberrequired
#### Query Parameters
​takenumberdefault:250

Maximum number of items to returnRequired range: `1 <= x <= 250`Example:

`25`​skipnumberdefault:0

Number of items to skipRequired range: `x >= 0`Example:

`0`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Show child attributes
