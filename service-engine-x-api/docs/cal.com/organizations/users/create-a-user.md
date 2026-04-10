<!-- Source: https://cal.com/docs/api-reference/v2/orgs-users/create-a-user -->

# Create a user - Cal.com Docs

Users
# Create a user
Copy page

Required membership role: `org admin`. PBAC permission: `organization.invite`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePOST/v2/organizations/{orgId}/usersTry itCreate a user

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/organizations/{orgId}/users \
  --header 'Content-Type: application/json' \
  --data '
{
  "email": "[email protected]",
  "username": "user123",
  "weekday": "Monday",
  "brandColor": "#FFFFFF",
  "bio": "I am a bio",
  "metadata": {
    "key": "value"
  },
  "darkBrandColor": "#000000",
  "hideBranding": false,
  "timeZone": "America/New_York",
  "theme": "dark",
  "appTheme": "light",
  "timeFormat": 24,
  "defaultScheduleId": 1,
  "locale": "en",
  "avatarUrl": "https://example.com/avatar.jpg",
  "organizationRole": "MEMBER",
  "autoAccept": true,
  "skipNotificationEmail": false
}
'`
```
201
```
`{
  "status": "success",
  "data": {
    "id": 1,
    "email": "[email protected]",
    "timeZone": "America/New_York",
    "weekStart": "Monday",
    "hideBranding": false,
    "createdDate": "2022-01-01T00:00:00Z",
    "profile": {
      "id": 1,
      "organizationId": 1,
      "userId": 1,
      "username": "john_doe"
    },
    "username": "john_doe",
    "name": "John Doe",
    "emailVerified": "2022-01-01T00:00:00Z",
    "bio": "I am a software developer",
    "avatarUrl": "https://example.com/avatar.jpg",
    "appTheme": "light",
    "theme": "default",
    "defaultScheduleId": 1,
    "locale": "en-US",
    "timeFormat": 12,
    "brandColor": "#ffffff",
    "darkBrandColor": "#000000",
    "allowDynamicBooking": true,
    "verified": true,
    "invitedTo": 1,
    "metadata": {
      "key": "value"
    }
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
application/json​emailstringrequired

User email addressExample:

`"[email protected]"`​usernamestring

UsernameExample:

`"user123"`​weekdaystring

Preferred weekdayExample:

`"Monday"`​brandColorstring

Brand color in HEX formatExample:

`"#FFFFFF"`​biostring

BioExample:

`"I am a bio"`​metadataobject

You can store any additional data you want here. Metadata must have at most 50 keys, each key up to 40 characters, and values up to 500 characters.Example:
```
`{ "key": "value" }
`
```
​darkBrandColorstring

Dark brand color in HEX formatExample:

`"#000000"`​hideBrandingboolean

Hide brandingExample:

`false`​timeZonestring

Time zoneExample:

`"America/New_York"`​themestring | null

ThemeExample:

`"dark"`​appThemestring | null

Application themeExample:

`"light"`​timeFormatnumber

Time formatExample:

`24`​defaultScheduleIdnumber

Default schedule IDRequired range: `x >= 0`Example:

`1`​localestring | nulldefault:en

LocaleExample:

`"en"`​avatarUrlstring

Avatar URLExample:

`"https://example.com/avatar.jpg"`​organizationRoleenum<string>default:MEMBERAvailable options: `MEMBER`, `ADMIN`, `OWNER` ​autoAcceptbooleandefault:true

Must be true to ensure the organization membership is created in accepted state. If false, the user will have a pending membership and will not be able to access the organization.​skipNotificationEmailbooleandefault:false

If true, the signup notification email will not be sent to the new user.
#### Response
201 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
