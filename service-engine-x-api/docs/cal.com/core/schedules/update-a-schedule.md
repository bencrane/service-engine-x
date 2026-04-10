<!-- Source: https://cal.com/docs/api-reference/v2/schedules/update-a-schedule -->

# Update a schedule - Cal.com Docs

Schedules
# Update a schedule
Copy pagePlease make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pagePATCH/v2/schedules/{scheduleId}Try itUpdate a schedule

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/schedules/{scheduleId} \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --header 'cal-api-version: <cal-api-version>' \
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
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token​cal-api-versionstringdefault:2024-06-11required

Must be set to 2024-06-11. If not set to this value, the endpoint will default to an older version.
#### Path Parameters
​scheduleIdstringrequired
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
]`
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
]`
```

#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
