<!-- Source: https://cal.com/docs/api-reference/v2/event-types-private-links/create-a-private-link-for-an-event-type -->

# Create a private link for an event type - Cal.com Docs

Event Types Private Links
# Create a private link for an event type
Copy pageCopy pagePOST/v2/event-types/{eventTypeId}/private-linksTry itCreate a private link for an event type

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/event-types/{eventTypeId}/private-links \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --header 'cal-api-version: <cal-api-version>' \
  --data '
{
  "expiresAt": "2024-12-31T23:59:59.000Z",
  "maxUsageCount": 10
}
'`
```
201
```
`{
  "status": "success",
  "data": {
    "linkId": "abc123def456",
    "eventTypeId": 123,
    "isExpired": false,
    "bookingUrl": "https://cal.com/d/abc123def456",
    "expiresAt": "2025-12-31T23:59:59.000Z"
  }
}`
```

#### Headers
​cal-api-versionstringdefault:2024-09-04required

Must be set to `2024-09-04`. Returns the full booking URL including org slug and event slug.​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​eventTypeIdnumberrequired
#### Body
application/json​expiresAtstring<date-time>

Expiration date for time-based linksExample:

`"2024-12-31T23:59:59.000Z"`​maxUsageCountnumberdefault:1

Maximum number of times the link can be used. If omitted and expiresAt is not provided, defaults to 1 (one time use).Required range: `x >= 1`Example:

`10`
#### Response
201 - application/json​statusstringrequired

Response statusExample:

`"success"`​dataobjectrequired

Created private link data (either time-based or usage-based)
- Option 1
- Option 2

Show child attributes
