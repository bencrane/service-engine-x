<!-- Source: https://cal.com/docs/api-reference/v2/schedules/get-all-schedules -->

# Get all schedules - Cal.com Docs

Schedules
# Get all schedules
Copy page

Get all schedules of the authenticated user.
Please make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pageGET/v2/schedulesTry itGet all schedules

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/schedules \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
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
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token​cal-api-versionstringdefault:2024-06-11required

Must be set to 2024-06-11. If not set to this value, the endpoint will default to an older version.
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Show child attributes
