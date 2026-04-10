<!-- Source: https://cal.com/docs/api-reference/v2/me/update-my-profile -->

# Update my profile - Cal.com Docs

Me
# Update my profile
Copy page

Updates the authenticated user’s profile. Email changes require verification and the primary email stays unchanged until verification completes, unless the new email is already a verified secondary email or the user is platform-managed.Copy pagePATCH/v2/meTry itUpdate my profile

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/me \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "email": "<string>",
  "name": "<string>",
  "timeFormat": 12,
  "defaultScheduleId": 123,
  "weekStart": "Monday",
  "timeZone": "<string>",
  "locale": "en",
  "avatarUrl": "https://cal.com/api/avatar/2b735186-b01b-46d3-87da-019b8f61776b.png",
  "bio": "I am a bio",
  "metadata": {
    "key": "value"
  }
}
'`
```
200
```
`{
  "status": "success",
  "data": {
    "id": 123,
    "username": "<string>",
    "email": "<string>",
    "name": "<string>",
    "avatarUrl": "<string>",
    "bio": "<string>",
    "timeFormat": 123,
    "defaultScheduleId": 123,
    "weekStart": "<string>",
    "timeZone": "<string>",
    "locale": "en",
    "organizationId": 123,
    "organization": {
      "isPlatform": true,
      "id": 123
    }
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Body
application/json​emailstring​namestring​timeFormatenum<number>

Must be 12 or 24Available options: `12`, `24` Example:

`12`​defaultScheduleIdnumber​weekStartenum<string>Available options: `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday` Example:

`"Monday"`​timeZonestring​localeenum<string>Available options: `ar`, `ca`, `de`, `es`, `eu`, `he`, `id`, `ja`, `lv`, `pl`, `ro`, `sr`, `th`, `vi`, `az`, `cs`, `el`, `es-419`, `fi`, `hr`, `it`, `km`, `nl`, `pt`, `ru`, `sv`, `tr`, `zh-CN`, `bg`, `da`, `en`, `et`, `fr`, `hu`, `iw`, `ko`, `no`, `pt-BR`, `sk`, `ta`, `uk`, `zh-TW`, `bn` Example:

`"en"`​avatarUrlstring

URL of the user's avatar imageExample:

`"https://cal.com/api/avatar/2b735186-b01b-46d3-87da-019b8f61776b.png"`​biostring

BioExample:

`"I am a bio"`​metadataobject

You can store any additional data you want here. Metadata must have at most 50 keys, each key up to 40 characters, and values up to 500 characters.Example:
```
`{ "key": "value" }`
```

#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
