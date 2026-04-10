<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams/get-teams-membership-for-user -->

# Get teams membership for user - Cal.com Docs

Teams
# Get teams membership for user
Copy page

Required membership role: `org member`. PBAC permission: `team.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/teams/meTry itGet teams membership for user

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/teams/me`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "id": 123,
      "name": "<string>",
      "isOrganization": true,
      "parentId": 123,
      "slug": "<string>",
      "logoUrl": "<string>",
      "calVideoLogo": "<string>",
      "appLogo": "<string>",
      "appIconLogo": "<string>",
      "bio": "<string>",
      "hideBranding": true,
      "isPrivate": true,
      "hideBookATeamMember": false,
      "metadata": {
        "key": "value"
      },
      "theme": "<string>",
      "brandColor": "<string>",
      "darkBrandColor": "<string>",
      "bannerUrl": "<string>",
      "timeFormat": 123,
      "timeZone": "Europe/London",
      "weekStart": "Sunday"
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
