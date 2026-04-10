<!-- Source: https://cal.com/docs/api-reference/v2/event-types-webhooks/delete-a-webhook -->

# Delete a webhook - Cal.com Docs

Webhooks
# Delete a webhook
Copy pageCopy pageDELETE/v2/event-types/{eventTypeId}/webhooks/{webhookId}Try itDelete a webhook

cURL
```
`curl --request DELETE \
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
