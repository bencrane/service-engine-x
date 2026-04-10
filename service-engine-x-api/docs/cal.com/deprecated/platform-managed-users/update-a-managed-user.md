<!-- Source: https://cal.com/docs/api-reference/v2/deprecated:-platform-managed-users/update-a-managed-user -->

# Update a managed user - Cal.com Docs

Platform / Managed Users
# Update a managed user
Copy pageThese endpoints are deprecated and will be removed in the future.Copy pagePATCH/v2/oauth-clients/{clientId}/users/{userId}Try itUpdate a managed user

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/oauth-clients/{clientId}/users/{userId} \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --header 'x-cal-secret-key: <x-cal-secret-key>' \
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
    "id": 1,
    "email": "[email protected]",
    "username": "alice",
    "name": "alice",
    "bio": "bio",
    "timeZone": "America/New_York",
    "weekStart": "Sunday",
    "createdDate": "2024-04-01T00:00:00.000Z",
    "timeFormat": 12,
    "defaultScheduleId": null,
    "locale": "en",
    "avatarUrl": "https://cal.com/api/avatar/2b735186-b01b-46d3-87da-019b8f61776b.png",
    "metadata": {
      "key": "value"
    }
  }
}`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Headers
​x-cal-secret-keystringrequired

OAuth client secret key
#### Path Parameters
​clientIdstringrequired​userIdnumberrequired
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
