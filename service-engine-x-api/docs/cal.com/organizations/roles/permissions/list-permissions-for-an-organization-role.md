<!-- Source: https://cal.com/docs/api-reference/v2/orgs-roles-permissions/list-permissions-for-an-organization-role -->

# List permissions for an organization role - Cal.com Docs

Permissions
# List permissions for an organization role
Copy page

Required membership role: `org admin`. PBAC permission: `role.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/roles/{roleId}/permissionsTry itList permissions for an organization role

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/roles/{roleId}/permissions`
```
200
```
`{
  "status": "success",
  "data": [
    "<string>"
  ]
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
200 - application/json​statusstringrequiredExample:

`"success"`​datastring[]required
