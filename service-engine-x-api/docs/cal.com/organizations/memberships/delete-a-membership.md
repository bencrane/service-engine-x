<!-- Source: https://cal.com/docs/api-reference/v2/orgs-memberships/delete-a-membership -->

# Delete a membership - Cal.com Docs

Memberships
# Delete a membership
Copy page

Required membership role: `org admin`. PBAC permission: `organization.remove`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageDELETE/v2/organizations/{orgId}/memberships/{membershipId}Try itDelete a membership

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/organizations/{orgId}/memberships/{membershipId}`
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
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
