<!-- Source: https://cal.com/docs/api-reference/v2/orgs-users-schedules/update-a-schedule -->

# Update a schedule - Cal.com Docs

Schedules
# Update a schedule
Copy page

Required membership role: `org admin`. PBAC permission: `availability.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePATCH/v2/organizations/{orgId}/users/{userId}/schedules/{scheduleId}Try itUpdate a schedule

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/organizations/{orgId}/users/{userId}/schedules/{scheduleId} \
  --header 'Content-Type: application/json' \
  --data '
{
  "name": "One-on-one coaching",
  "timeZone": "Europe/Rome",
  "availability": [
    {
      "days": [
        "Monday",
        "Tuesday"
      ],
      "startTime": "09:00",
      "endTime": "10:00"
    }
  ],
  "isDefault": true,
  "overrides": [
    {
      "date": "2024-05-20",
      "startTime": "12:00",
      "endTime": "14:00"
    }
  ]
}
'`
```
200
```
`{
  "status": "success",
  "data": {
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
}`
```

#### Headers
​Authorizationstring

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​userIdnumberrequired​scheduleIdnumberrequired​orgIdnumberrequired
#### Body
application/json​namestringExample:

`"One-on-one coaching"`​timeZonestringExample:

`"Europe/Rome"`​availabilityobject[]

Show child attributesExample:
```
`[
  {
    "days": ["Monday", "Tuesday"],
    "startTime": "09:00",
    "endTime": "10:00"
  }
]
`
```
​isDefaultbooleanExample:

`true`​overridesobject[]

Show child attributesExample:
```
`[
  {
    "date": "2024-05-20",
    "startTime": "12:00",
    "endTime": "14:00"
  }
]
`
```

#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
