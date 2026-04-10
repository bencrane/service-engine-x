<!-- Source: https://cal.com/docs/api-reference/v2/deprecated:-platform-managed-users/delete-a-managed-user -->

# Delete a managed user - Cal.com Docs

Platform / Managed Users
# Delete a managed user
Copy pageThese endpoints are deprecated and will be removed in the future.Copy pageDELETE/v2/oauth-clients/{clientId}/users/{userId}Try itDelete a managed user

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/oauth-clients/{clientId}/users/{userId} \
  --header 'Authorization: Bearer <token>' \
  --header 'x-cal-secret-key: <x-cal-secret-key>'`
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
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
