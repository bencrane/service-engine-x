<!-- Source: https://cal.com/docs/api-reference/v2/orgs-users-ooo/update-an-out-of-office-entry-for-a-user -->

# Update an out-of-office entry for a user - Cal.com Docs

OOO
# Update an out-of-office entry for a user
Copy pageCopy pagePATCH/v2/organizations/{orgId}/users/{userId}/ooo/{oooId}Try itUpdate an out-of-office entry for a user

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/organizations/{orgId}/users/{userId}/ooo/{oooId} \
  --header 'Content-Type: application/json' \
  --data '
{
  "start": "2023-05-01T00:00:00.000Z",
  "end": "2023-05-10T23:59:59.999Z",
  "notes": "Vacation in Hawaii",
  "toUserId": 2,
  "reason": "vacation"
}
'`
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
​userIdnumberrequired​oooIdnumberrequired​orgIdnumberrequired
#### Body
application/json​startstring<date-time>

The start date and time of the out of office period in ISO 8601 format in UTC timezone.Example:

`"2023-05-01T00:00:00.000Z"`​endstring<date-time>

The end date and time of the out of office period in ISO 8601 format in UTC timezone.Example:

`"2023-05-10T23:59:59.999Z"`​notesstring

Optional notes for the out of office entry.Example:

`"Vacation in Hawaii"`​toUserIdnumber

The ID of the user covering for the out of office period, if applicable.Example:

`2`​reasonenum<string>

the reason for the out of office entry, if applicableAvailable options: `unspecified`, `vacation`, `travel`, `sick`, `public_holiday` Example:

`"vacation"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
