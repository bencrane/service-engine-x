<!-- Source: https://cal.com/docs/api-reference/v2/orgs-memberships/update-a-membership -->

# Update a membership - Cal.com Docs

Memberships
# Update a membership
Copy page

Required membership role: `org admin`. PBAC permission: `organization.changeMemberRole`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePATCH/v2/organizations/{orgId}/memberships/{membershipId}Try itUpdate a membership

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/organizations/{orgId}/memberships/{membershipId} \
  --header 'Content-Type: application/json' \
  --data '
{
  "accepted": true,
  "role": "MEMBER",
  "disableImpersonation": true
}
'`
```
200
```
`{
  "status": "success",
  "data": {
    "id": 123,
    "userId": 123,
    "teamId": 123,
    "accepted": true,
    "role": "MEMBER",
    "user": {
      "email": "<string>",
      "avatarUrl": "<string>",
      "username": "<string>",
      "name": "<string>",
      "bio": "<string>",
      "metadata": {
        "key": "value"
      }
    },
    "attributes": [
      {
        "id": "<string>",
        "name": "<string>",
        "type": "<string>",
        "option": "<string>",
        "optionId": "<string>"
      }
    ],
    "disableImpersonation": true
  }
}`
```

#### Headers
​Authorizationstring

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​orgIdnumberrequired​membershipIdnumberrequired
#### Body
application/json​acceptedboolean​roleenum<string>Available options: `MEMBER`, `OWNER`, `ADMIN` ​disableImpersonationboolean
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
