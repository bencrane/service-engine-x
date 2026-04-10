<!-- Source: https://cal.com/docs/api-reference/v2/orgs-roles-permissions/add-permissions-to-an-organization-role-single-or-batch -->

# Add permissions to an organization role (single or batch) - Cal.com Docs

Permissions
# Add permissions to an organization role (single or batch)
Copy page

Required membership role: `org admin`. PBAC permission: `role.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePOST/v2/organizations/{orgId}/roles/{roleId}/permissionsTry itAdd permissions to an organization role (single or batch)

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/organizations/{orgId}/roles/{roleId}/permissions \
  --header 'Content-Type: application/json' \
  --data '
{
  "permissions": [
    "eventType.read",
    "booking.read"
  ]
}
'`
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
#### Body
application/json​permissionsenum<string>[]required

Permissions to add (format: resource.action)Available options: `*.*`, `role.create`, `role.read`, `role.update`, `role.delete`, `eventType.create`, `eventType.read`, `eventType.update`, `eventType.delete`, `team.create`, `team.read`, `team.update`, `team.delete`, `team.invite`, `team.remove`, `team.listMembers`, `team.listMembersPrivate`, `team.changeMemberRole`, `team.impersonate`, `organization.create`, `organization.read`, `organization.listMembers`, `organization.listMembersPrivate`, `organization.invite`, `organization.remove`, `organization.manageBilling`, `organization.changeMemberRole`, `organization.impersonate`, `organization.passwordReset`, `organization.editUsers`, `organization.update`, `organization.delete`, `booking.read`, `booking.readOrgBookings`, `booking.readRecordings`, `booking.update`, `booking.readOrgAuditLogs`, `insights.read`, `workflow.create`, `workflow.read`, `workflow.update`, `workflow.delete`, `organization.attributes.read`, `organization.attributes.update`, `organization.attributes.delete`, `organization.attributes.create`, `organization.attributes.editUsers`, `routingForm.create`, `routingForm.read`, `routingForm.update`, `routingForm.delete`, `webhook.create`, `webhook.read`, `webhook.update`, `webhook.delete`, `watchlist.create`, `watchlist.read`, `watchlist.update`, `watchlist.delete`, `featureOptIn.read`, `featureOptIn.update`, `organization.customDomain.create`, `organization.customDomain.read`, `organization.customDomain.update`, `organization.customDomain.delete` Example:
```
`["eventType.read", "booking.read"]`
```

#### Response
200 - application/json​statusstringrequiredExample:

`"success"`​datastring[]required
