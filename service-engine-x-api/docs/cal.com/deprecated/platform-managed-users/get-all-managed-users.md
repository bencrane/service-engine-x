<!-- Source: https://cal.com/docs/api-reference/v2/deprecated:-platform-managed-users/get-all-managed-users -->

# Get all managed users - Cal.com Docs

Platform / Managed Users
# Get all managed users
Copy pageThese endpoints are deprecated and will be removed in the future.Copy pageGET/v2/oauth-clients/{clientId}/usersTry itGet all managed users

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/oauth-clients/{clientId}/users \
  --header 'Authorization: Bearer <token>' \
  --header 'x-cal-secret-key: <x-cal-secret-key>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
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
  ]
}`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Headers
​x-cal-secret-keystringrequired

OAuth client secret key
#### Path Parameters
​clientIdstringrequired
#### Query Parameters
​limitnumber

The number of items to returnExample:

`10`​offsetnumber

The number of items to skipExample:

`0`​emailsstring[]

Filter managed users by email. If you want to filter by multiple emails, separate them with a comma.Example:

`"[email protected],[email protected]"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Show child attributes
