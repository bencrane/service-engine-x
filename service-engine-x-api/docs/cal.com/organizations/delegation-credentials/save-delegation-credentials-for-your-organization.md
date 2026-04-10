<!-- Source: https://cal.com/docs/api-reference/v2/orgs-delegation-credentials/save-delegation-credentials-for-your-organization -->

# Save delegation credentials for your organization - Cal.com Docs

Delegation Credentials
# Save delegation credentials for your organization
Copy page

Required membership role: `org admin`. PBAC permission: `organization.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePOST/v2/organizations/{orgId}/delegation-credentialsTry itSave delegation credentials for your organization

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/organizations/{orgId}/delegation-credentials \
  --header 'Content-Type: application/json' \
  --data '
{
  "workspacePlatformSlug": "<string>",
  "domain": "<string>",
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
201
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
​orgIdnumberrequired
#### Body
application/json​workspacePlatformSlugstringrequired​domainstringrequired​serviceAccountKeyobject[]required
- Option 1
- Option 2

Show child attributes
#### Response
201 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
