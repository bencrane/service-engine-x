<!-- Source: https://cal.com/docs/api-reference/v2/schedules/delete-a-schedule -->

# Delete a schedule - Cal.com Docs

Schedules
# Delete a schedule
Copy pagePlease make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pageDELETE/v2/schedules/{scheduleId}Try itDelete a schedule

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/schedules/{scheduleId} \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success"
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token​cal-api-versionstringdefault:2024-06-11required

Must be set to 2024-06-11. If not set to this value, the endpoint will default to an older version.
#### Path Parameters
​scheduleIdnumberrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`
