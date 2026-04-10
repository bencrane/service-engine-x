<!-- Source: https://cal.com/docs/api-reference/v2/orgs-users-schedules/delete-a-schedule -->

# Delete a schedule - Cal.com Docs

Schedules
# Delete a schedule
Copy page

Required membership role: `org admin`. PBAC permission: `availability.delete`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageDELETE/v2/organizations/{orgId}/users/{userId}/schedules/{scheduleId}Try itDelete a schedule

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/organizations/{orgId}/users/{userId}/schedules/{scheduleId}`
```
200
```
`{
  "status": "success"
}`
```

#### Headers
​Authorizationstring

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​userIdnumberrequired​scheduleIdnumberrequired​orgIdnumberrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`
