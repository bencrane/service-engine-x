<!-- Source: https://cal.com/docs/api-reference/v2/teams/create-a-team -->

# Create a team - Cal.com Docs

Teams
# Create a team
Copy pageCopy pagePOST/v2/teamsTry itCreate a team

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/teams \
  --header 'Authorization: <authorization>' \
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
  "hideBranding": false,
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
  "autoAcceptCreator": true
}
'`
```
201
```
`{
  "status": "success",
  "data": {
    "message": "<string>",
    "paymentLink": "<string>",
    "pendingTeam": {
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
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_
#### Body
application/json​namestringrequired

Name of the teamMinimum string length: `1`Example:

`"CalTeam"`​slugstring

Team slug in kebab-case - if not provided will be generated automatically based on name.Example:

`"caltel"`​logoUrlstring

URL of the teams logo imageExample:

`"https://i.cal.com/api/avatar/b0b58752-68ad-4c0d-8024-4fa382a77752.png"`​calVideoLogostring​appLogostring​appIconLogostring​biostring​hideBrandingbooleandefault:false​isPrivateboolean​hideBookATeamMemberboolean​metadataobject

You can store any additional data you want here.
Metadata must have at most 50 keys, each key up to 40 characters.
Values can be strings (up to 500 characters), numbers, or booleans.Example:
```
`{ "key": "value" }`
```
​themestring​brandColorstring​darkBrandColorstring​bannerUrlstring

URL of the teams banner image which is shown on bookerExample:

`"https://i.cal.com/api/avatar/949be534-7a88-4185-967c-c020b0c0bef3.png"`​timeFormatnumber​timeZonestringdefault:Europe/London

Timezone is used to create teams's default schedule from Monday to Friday from 9AM to 5PM. It will default to Europe/London if not passed.Example:

`"America/New_York"`​weekStartstringdefault:SundayExample:

`"Monday"`​autoAcceptCreatorbooleandefault:true

If you are a platform customer, don't pass 'false', because then team creator won't be able to create team event types.
#### Response
201 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Either an Output object or a TeamOutputDto.
- Option 1
- Option 2

Show child attributes
