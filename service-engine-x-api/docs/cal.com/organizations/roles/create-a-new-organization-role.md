<!-- Source: https://cal.com/docs/api-reference/v2/orgs-roles/create-a-new-organization-role -->

# Create a new organization role - Cal.com Docs

Roles
# Create a new organization role
Copy page

Required membership role: `org admin`. PBAC permission: `role.create`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePOST/v2/organizations/{orgId}/rolesTry itCreate a new organization role

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/organizations/{orgId}/roles \
  --header 'Content-Type: application/json' \
  --data '
{
  "name": "<string>",
  "color": "<string>",
  "description": "<string>",
  "permissions": [
    "eventType.read",
    "eventType.create",
    "booking.read"
  ]
}
'`
```
201
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
​orgIdnumberrequired
#### Body
application/json​namestringrequired

Name of the roleMinimum string length: `1`​colorstring

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

#### Response
201 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
