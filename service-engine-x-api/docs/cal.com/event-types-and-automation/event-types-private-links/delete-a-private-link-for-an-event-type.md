<!-- Source: https://cal.com/docs/api-reference/v2/event-types-private-links/delete-a-private-link-for-an-event-type -->

# Delete a private link for an event type - Cal.com Docs

Event Types Private Links
# Delete a private link for an event type
Copy pageCopy pageDELETE/v2/event-types/{eventTypeId}/private-links/{linkId}Try itDelete a private link for an event type

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/event-types/{eventTypeId}/private-links/{linkId} \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": {
    "linkId": "abc123def456",
    "message": "Private link deleted successfully"
  }
}`
```

#### Headers
​cal-api-versionstringdefault:2024-09-04required

Must be set to `2024-09-04`. Returns the full booking URL including org slug and event slug.​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​eventTypeIdnumberrequired​linkIdstringrequired
#### Response
200 - application/json​statusstringrequired

Response statusExample:

`"success"`​dataobjectrequired

Deleted link information

Show child attributes
