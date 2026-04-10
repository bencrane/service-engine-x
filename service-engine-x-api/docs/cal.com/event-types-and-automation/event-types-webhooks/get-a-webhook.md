<!-- Source: https://cal.com/docs/api-reference/v2/event-types-webhooks/get-a-webhook -->

# Get a webhook - Cal.com Docs

Webhooks
# Get a webhook
Copy pageCopy pageGET/v2/event-types/{eventTypeId}/webhooks/{webhookId}Try itGet a webhook

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/event-types/{eventTypeId}/webhooks/{webhookId} \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": {
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
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​webhookIdstringrequired​eventTypeIdnumberrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
