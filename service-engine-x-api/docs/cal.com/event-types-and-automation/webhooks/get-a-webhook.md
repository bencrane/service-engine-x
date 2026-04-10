<!-- Source: https://cal.com/docs/api-reference/v2/webhooks/get-a-webhook -->

# Get a webhook - Cal.com Docs

Webhooks
# Get a webhook
Copy pageCopy pageGET/v2/webhooks/{webhookId}Try itGet a webhook

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/webhooks/{webhookId} \
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
    "userId": 123,
    "id": 123,
    "subscriberUrl": "<string>",
    "active": true,
    "secret": "<string>"
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_
#### Path Parameters
​webhookIdstringrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
