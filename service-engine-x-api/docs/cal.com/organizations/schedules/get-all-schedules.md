<!-- Source: https://cal.com/docs/api-reference/v2/orgs-schedules/get-all-schedules -->

# Get all schedules - Cal.com Docs

Schedules
# Get all schedules
Copy page

Required membership role: `org admin`. PBAC permission: `availability.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/schedulesTry itGet all schedules

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/schedules`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "id": 254,
      "ownerId": 478,
      "name": "Catch up hours",
      "timeZone": "Europe/Rome",
      "availability": [
        {
          "days": [
            "Monday",
            "Tuesday"
          ],
          "startTime": "17:00",
          "endTime": "19:00"
        },
        {
          "days": [
            "Wednesday",
            "Thursday"
          ],
          "startTime": "16:00",
          "endTime": "20:00"
        }
      ],
      "isDefault": true,
      "overrides": [
        {
          "date": "2024-05-20",
          "startTime": "18:00",
          "endTime": "21:00"
        }
      ]
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
​orgIdnumberrequired
#### Query Parameters
​takenumberdefault:250

Maximum number of items to returnRequired range: `1 <= x <= 250`Example:

`25`​skipnumberdefault:0

Number of items to skipRequired range: `x >= 0`Example:

`0`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Show child attributes
