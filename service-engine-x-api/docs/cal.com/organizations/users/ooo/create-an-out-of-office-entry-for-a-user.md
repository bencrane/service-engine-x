<!-- Source: https://cal.com/docs/api-reference/v2/orgs-users-ooo/create-an-out-of-office-entry-for-a-user -->

# Create an out-of-office entry for a user - Cal.com Docs

OOO
# Create an out-of-office entry for a user
Copy pageCopy pagePOST/v2/organizations/{orgId}/users/{userId}/oooTry itCreate an out-of-office entry for a user

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/organizations/{orgId}/users/{userId}/ooo \
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
201
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
​userIdnumberrequired​orgIdnumberrequired
#### Body
application/json​startstring<date-time>required

The start date and time of the out of office period in ISO 8601 format in UTC timezone.Example:

`"2023-05-01T00:00:00.000Z"`​endstring<date-time>required

The end date and time of the out of office period in ISO 8601 format in UTC timezone.Example:

`"2023-05-10T23:59:59.999Z"`​notesstring

Optional notes for the out of office entry.Example:

`"Vacation in Hawaii"`​toUserIdnumber

The ID of the user covering for the out of office period, if applicable.Example:

`2`​reasonenum<string>

the reason for the out of office entry, if applicableAvailable options: `unspecified`, `vacation`, `travel`, `sick`, `public_holiday` Example:

`"vacation"`
#### Response
201 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
