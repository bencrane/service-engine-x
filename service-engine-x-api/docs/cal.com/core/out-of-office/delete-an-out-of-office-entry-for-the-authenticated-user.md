<!-- Source: https://cal.com/docs/api-reference/v2/out-of-office/delete-an-out-of-office-entry-for-the-authenticated-user -->

# Delete an out-of-office entry for the authenticated user - Cal.com Docs

Out of Office
# Delete an out-of-office entry for the authenticated user
Copy pageCopy pageDELETE/v2/me/ooo/{oooId}Try itDelete an out-of-office entry for the authenticated user

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/me/ooo/{oooId} \
  --header 'Authorization: <authorization>'`
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
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​oooIdnumberrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
