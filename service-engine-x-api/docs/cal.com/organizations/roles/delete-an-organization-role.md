<!-- Source: https://cal.com/docs/api-reference/v2/orgs-roles/delete-an-organization-role -->

# Delete an organization role - Cal.com Docs

Roles
# Delete an organization role
Copy page

Required membership role: `org admin`. PBAC permission: `role.delete`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageDELETE/v2/organizations/{orgId}/roles/{roleId}Try itDelete an organization role

cURL
```
`curl --request DELETE \
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
