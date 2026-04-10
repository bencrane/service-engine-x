<!-- Source: https://cal.com/docs/api-reference/v2/event-types-private-links/get-all-private-links-for-an-event-type -->

# Get all private links for an event type - Cal.com Docs

Event Types Private Links
# Get all private links for an event type
Copy pageCopy pageGET/v2/event-types/{eventTypeId}/private-linksTry itGet all private links for an event type

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/event-types/{eventTypeId}/private-links \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "linkId": "abc123def456",
      "eventTypeId": 123,
      "isExpired": false,
      "bookingUrl": "https://cal.com/d/abc123def456",
      "expiresAt": "2025-12-31T23:59:59.000Z"
    }
  ]
}`
```

#### Headers
​cal-api-versionstringdefault:2024-09-04required

Must be set to `2024-09-04`. Returns the full booking URL including org slug and event slug.​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​eventTypeIdnumberrequired
#### Response
200 - application/json​statusstringrequired

Response statusExample:

`"success"`​dataobject[]required

Array of private links for the event type (mix of time-based and usage-based)
- Option 1
- Option 2

Show child attributes
