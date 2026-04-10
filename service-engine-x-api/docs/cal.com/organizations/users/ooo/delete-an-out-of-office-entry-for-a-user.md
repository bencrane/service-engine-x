<!-- Source: https://cal.com/docs/api-reference/v2/orgs-users-ooo/delete-an-out-of-office-entry-for-a-user -->

# Delete an out-of-office entry for a user - Cal.com Docs

OOO
# Delete an out-of-office entry for a user
Copy pageCopy pageDELETE/v2/organizations/{orgId}/users/{userId}/ooo/{oooId}Try itDelete an out-of-office entry for a user

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/organizations/{orgId}/users/{userId}/ooo/{oooId}`
```
200
```
`{
  "status": "success",
  "data": {
    "userId": 2,
    "id": 2,
    "uuid": "e84be5a3-4696-49e3-acc7-b2f3999c3b94",
    "start": "2023-05-01T00:00:00.000Z",
    "end": "2023-05-10T23:59:59.999Z",
    "toUserId": 2,
    "notes": "Vacation in Hawaii",
    "reason": "vacation"
  }
}`
```

#### Headers
​Authorizationstring

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​oooIdnumberrequired​userIdnumberrequired​orgIdnumberrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
