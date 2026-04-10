<!-- Source: https://cal.com/docs/api-reference/v2/event-types/delete-an-event-type -->

# Delete an event type - Cal.com Docs

Event Types
# Delete an event type
Copy pagePlease make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pageDELETE/v2/event-types/{eventTypeId}Try itDelete an event type

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/event-types/{eventTypeId} \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": {
    "id": 1,
    "lengthInMinutes": 60,
    "title": "Learn the secrets of masterchief!",
    "slug": "<string>"
  }
}`
```

#### Headers
​cal-api-versionstringdefault:2024-06-14required

Must be set to 2024-06-14. If not set to this value, the endpoint will default to an older version.​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​eventTypeIdnumberrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
