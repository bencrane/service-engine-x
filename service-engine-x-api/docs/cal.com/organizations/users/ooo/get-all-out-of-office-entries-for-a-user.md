<!-- Source: https://cal.com/docs/api-reference/v2/orgs-users-ooo/get-all-out-of-office-entries-for-a-user -->

# Get all out-of-office entries for a user - Cal.com Docs

OOO
# Get all out-of-office entries for a user
Copy pageCopy pageGET/v2/organizations/{orgId}/users/{userId}/oooTry itGet all out-of-office entries for a user

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/users/{userId}/ooo`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "userId": 2,
      "id": 2,
      "uuid": "e84be5a3-4696-49e3-acc7-b2f3999c3b94",
      "start": "2023-05-01T00:00:00.000Z",
      "end": "2023-05-10T23:59:59.999Z",
      "toUserId": 2,
      "notes": "Vacation in Hawaii",
      "reason": "vacation"
    }
  ]
}`
```

#### Headers
​Authorizationstring

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​userIdnumberrequired​orgIdnumberrequired
#### Query Parameters
​takenumberdefault:250

Maximum number of items to returnRequired range: `1 <= x <= 250`Example:

`25`​skipnumberdefault:0

Number of items to skipRequired range: `x >= 0`Example:

`0`​sortStartenum<string>

Sort results by their start time in ascending or descending order.Available options: `asc`, `desc` Example:

`"?sortStart=asc OR ?sortStart=desc"`​sortEndenum<string>

Sort results by their end time in ascending or descending order.Available options: `asc`, `desc` Example:

`"?sortEnd=asc OR ?sortEnd=desc"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Show child attributes
