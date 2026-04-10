<!-- Source: https://cal.com/docs/api-reference/v2/orgs-memberships/get-all-memberships -->

# Get all memberships - Cal.com Docs

Memberships
# Get all memberships
Copy page

Required membership role: `org admin`. PBAC permission: `organization.listMembers`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/membershipsTry itGet all memberships

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/memberships`
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
​orgIdnumberrequired
#### Query Parameters
​takenumberdefault:250

Maximum number of items to returnRequired range: `1 <= x <= 250`Example:

`25`​skipnumberdefault:0

Number of items to skipRequired range: `x >= 0`Example:

`0`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
