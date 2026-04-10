<!-- Source: https://cal.com/docs/api-reference/v2/orgs-roles/update-an-organization-role -->

# Update an organization role - Cal.com Docs

Roles
# Update an organization role
Copy page

Required membership role: `org admin`. PBAC permission: `role.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePATCH/v2/organizations/{orgId}/roles/{roleId}Try itUpdate an organization role

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/organizations/{orgId}/roles/{roleId} \
  --header 'Content-Type: application/json' \
  --data '
{
  "color": "<string>",
  "description": "<string>",
  "permissions": [
    "eventType.read",
    "eventType.create",
    "booking.read"
  ],
  "name": "<string>"
}
'`
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
#### Body
application/json​colorstring

Color for the role (hex code)​descriptionstring

Description of the role​permissionsenum<string>[]

Permissions for this role (format: resource.action). On update, this field replaces the entire permission set for the role (full replace). Use granular permission endpoints for one-by-one changes.Available options: `*.*`, `role.create`, `role.read`, `role.update`, `role.delete`, `eventType.create`, `eventType.read`, `eventType.update`, `eventType.delete`, `team.create`, `team.read`, `team.update`, `team.delete`, `team.invite`, `team.remove`, `team.listMembers`, `team.listMembersPrivate`, `team.changeMemberRole`, `team.impersonate`, `organization.create`, `organization.read`, `organization.listMembers`, `organization.listMembersPrivate`, `organization.invite`, `organization.remove`, `organization.manageBilling`, `organization.changeMemberRole`, `organization.impersonate`, `organization.passwordReset`, `organization.editUsers`, `organization.update`, `organization.delete`, `booking.read`, `booking.readOrgBookings`, `booking.readRecordings`, `booking.update`, `booking.readOrgAuditLogs`, `insights.read`, `workflow.create`, `workflow.read`, `workflow.update`, `workflow.delete`, `organization.attributes.read`, `organization.attributes.update`, `organization.attributes.delete`, `organization.attributes.create`, `organization.attributes.editUsers`, `routingForm.create`, `routingForm.read`, `routingForm.update`, `routingForm.delete`, `webhook.create`, `webhook.read`, `webhook.update`, `webhook.delete`, `watchlist.create`, `watchlist.read`, `watchlist.update`, `watchlist.delete`, `featureOptIn.read`, `featureOptIn.update`, `organization.customDomain.create`, `organization.customDomain.read`, `organization.customDomain.update`, `organization.customDomain.delete` Example:
```
`[
  "eventType.read",
  "eventType.create",
  "booking.read"
]`
```
​namestring

Name of the roleMinimum string length: `1`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
