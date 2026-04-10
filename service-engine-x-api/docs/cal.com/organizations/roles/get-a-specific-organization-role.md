<!-- Source: https://cal.com/docs/api-reference/v2/orgs-roles/get-a-specific-organization-role -->

# Get a specific organization role - Cal.com Docs

Roles
# Get a specific organization role
Copy page

Required membership role: `org admin`. PBAC permission: `role.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/roles/{roleId}Try itGet a specific organization role

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/roles/{roleId}`
```
200
```
`{
  "status": "success",
  "data": {
    "id": "<string>",
    "name": "<string>",
    "type": "SYSTEM",
    "permissions": [
      "booking.read",
      "eventType.create"
    ],
    "createdAt": "<string>",
    "updatedAt": "<string>",
    "color": "<string>",
    "description": "<string>",
    "organizationId": 123
  }
}`
```

#### Headers
​Authorizationstring

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​orgIdnumberrequired​roleIdstringrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
