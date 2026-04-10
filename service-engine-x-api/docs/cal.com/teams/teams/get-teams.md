<!-- Source: https://cal.com/docs/api-reference/v2/teams/get-teams -->

# Get teams - Cal.com Docs

Teams
# Get teams
Copy pageCopy pageGET/v2/teamsTry itGet teams

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/teams \
  --header 'Authorization: <authorization>'`
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
      "hideBookATeamMember": true,
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
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Show child attributes
