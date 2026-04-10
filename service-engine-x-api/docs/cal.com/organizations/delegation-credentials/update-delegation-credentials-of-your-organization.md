<!-- Source: https://cal.com/docs/api-reference/v2/orgs-delegation-credentials/update-delegation-credentials-of-your-organization -->

# Update delegation credentials of your organization - Cal.com Docs

Delegation Credentials
# Update delegation credentials of your organization
Copy page

Required membership role: `org admin`. PBAC permission: `organization.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePATCH/v2/organizations/{orgId}/delegation-credentials/{credentialId}Try itUpdate delegation credentials of your organization

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/organizations/{orgId}/delegation-credentials/{credentialId} \
  --header 'Content-Type: application/json' \
  --data '
{
  "enabled": true,
  "serviceAccountKey": [
    {
      "private_key": "<string>",
      "client_email": "<string>",
      "client_id": "<string>"
    }
  ]
}
'`
```
200
```
`{
  "status": "success",
  "data": {
    "id": "<string>",
    "enabled": true,
    "domain": "<string>",
    "organizationId": 123,
    "workspacePlatform": {
      "name": "<string>",
      "slug": "<string>"
    },
    "createdAt": "2023-11-07T05:31:56Z",
    "updatedAt": "2023-11-07T05:31:56Z"
  }
}`
```

#### Headers
​Authorizationstring

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​orgIdnumberrequired​credentialIdstringrequired
#### Body
application/json​enabledboolean​serviceAccountKeyobject[]
- Option 1
- Option 2

Show child attributes
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
