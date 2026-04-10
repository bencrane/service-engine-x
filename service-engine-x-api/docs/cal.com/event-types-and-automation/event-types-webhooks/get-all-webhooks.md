<!-- Source: https://cal.com/docs/api-reference/v2/event-types-webhooks/get-all-webhooks -->

# Get all webhooks - Cal.com Docs

Webhooks
# Get all webhooks
Copy pageCopy pageGET/v2/event-types/{eventTypeId}/webhooksTry itGet all webhooks

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/event-types/{eventTypeId}/webhooks \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "payloadTemplate": "{\"content\":\"A new event has been scheduled\",\"type\":\"{{type}}\",\"name\":\"{{title}}\",\"organizer\":\"{{organizer.name}}\",\"booker\":\"{{attendees.0.name}}\"}",
      "triggers": [
        "BOOKING_CREATED"
      ],
      "eventTypeId": 123,
      "id": 123,
      "subscriberUrl": "<string>",
      "active": true,
      "secret": "<string>"
    }
  ]
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​eventTypeIdnumberrequired
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
