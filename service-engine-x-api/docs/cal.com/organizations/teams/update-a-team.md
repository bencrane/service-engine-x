<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams/update-a-team -->

# Update a team - Cal.com Docs

Teams
# Update a team
Copy page

Required membership role: `org admin`. PBAC permission: `team.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePATCH/v2/organizations/{orgId}/teams/{teamId}Try itUpdate a team

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/organizations/{orgId}/teams/{teamId} \
  --header 'Content-Type: application/json' \
  --data '
{
  "name": "CalTeam",
  "slug": "caltel",
  "logoUrl": "https://i.cal.com/api/avatar/b0b58752-68ad-4c0d-8024-4fa382a77752.png",
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
  "bannerUrl": "https://i.cal.com/api/avatar/949be534-7a88-4185-967c-c020b0c0bef3.png",
  "timeFormat": 123,
  "timeZone": "America/New_York",
  "weekStart": "Monday",
  "bookingLimits": "<string>",
  "includeManagedEventsInLimits": true
}
'`
```
200
```
`{
  "status": "success",
  "data": {
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
}`
```

#### Headers
​Authorizationstring

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​orgIdnumberrequired​teamIdnumberrequired
#### Body
application/json​namestring

Name of the teamMinimum string length: `1`Example:

`"CalTeam"`​slugstring

Team slugExample:

`"caltel"`​logoUrlstring

URL of the teams logo imageExample:

`"https://i.cal.com/api/avatar/b0b58752-68ad-4c0d-8024-4fa382a77752.png"`​calVideoLogostring​appLogostring​appIconLogostring​biostring​hideBrandingboolean​isPrivateboolean​hideBookATeamMemberboolean​metadataobject

You can store any additional data you want here.
Metadata must have at most 50 keys, each key up to 40 characters.
Values can be strings (up to 500 characters), numbers, or booleans.Example:
```
`{ "key": "value" }`
```
​themestring​brandColorstring​darkBrandColorstring​bannerUrlstring

URL of the teams banner image which is shown on bookerExample:

`"https://i.cal.com/api/avatar/949be534-7a88-4185-967c-c020b0c0bef3.png"`​timeFormatnumber​timeZonestring

Timezone is used to create teams's default schedule from Monday to Friday from 9AM to 5PM. It will default to Europe/London if not passed.Example:

`"America/New_York"`​weekStartstringExample:

`"Monday"`​bookingLimitsstring​includeManagedEventsInLimitsboolean
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
