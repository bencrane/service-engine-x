<!-- Source: https://cal.com/docs/api-reference/v2/organization-team-verified-resources/get-verified-phone-number-of-an-org-team-by-id -->

# Get verified phone number of an org team by id - Cal.com Docs

Organization Team Verified Resources
# Get verified phone number of an org team by id
Copy page

Required membership role: `team admin`. PBAC permission: `team.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/teams/{teamId}/verified-resources/phones/{id}Try itGet verified phone number of an org team by id

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/verified-resources/phones/{id} \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": {
    "id": 789,
    "phoneNumber": "+37255556666",
    "teamId": 89,
    "userId": 45
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​teamIdnumberrequired​idnumberrequired​orgIdnumberrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
