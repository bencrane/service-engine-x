<!-- Source: https://cal.com/docs/api-reference/v2/orgs-roles/get-all-organization-roles -->

# Get all organization roles - Cal.com Docs

Roles
# Get all organization roles
Copy page

Required membership role: `org admin`. PBAC permission: `role.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/rolesTry itGet all organization roles

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/roles`
```
200
```
`{
  "status": "success",
  "data": [
    {
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
  ]
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

`"success"`​dataobject[]required

Show child attributes
