<!-- Source: https://cal.com/docs/api-reference/v2/orgs-memberships/create-a-membership -->

# Create a membership - Cal.com Docs

Memberships
# Create a membership
Copy page

Required membership role: `org admin`. PBAC permission: `organization.invite`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePOST/v2/organizations/{orgId}/membershipsTry itCreate a membership

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/organizations/{orgId}/memberships \
  --header 'Content-Type: application/json' \
  --data '
{
  "userId": 123,
  "role": "MEMBER",
  "accepted": false,
  "disableImpersonation": false
}
'`
```
201
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
#### Body
application/json​userIdnumberrequired​roleenum<string>default:MEMBERrequired

If you are platform customer then managed users should only have MEMBER role.Available options: `MEMBER`, `OWNER`, `ADMIN` ​acceptedbooleandefault:false​disableImpersonationbooleandefault:false
#### Response
201 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
