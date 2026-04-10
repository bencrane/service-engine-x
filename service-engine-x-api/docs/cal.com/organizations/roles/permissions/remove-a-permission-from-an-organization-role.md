<!-- Source: https://cal.com/docs/api-reference/v2/orgs-roles-permissions/remove-a-permission-from-an-organization-role -->

# Remove a permission from an organization role - Cal.com Docs

Permissions
# Remove a permission from an organization role
Copy page

Required membership role: `org admin`. PBAC permission: `role.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageDELETE/v2/organizations/{orgId}/roles/{roleId}/permissions/{permission}Try itRemove a permission from an organization role

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/organizations/{orgId}/roles/{roleId}/permissions/{permission}`
```

#### Headers
​Authorizationstring

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​orgIdnumberrequired​roleIdstringrequired​permissionstringrequired
#### Response
204 - undefined
