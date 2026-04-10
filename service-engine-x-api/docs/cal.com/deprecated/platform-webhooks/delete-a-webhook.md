<!-- Source: https://cal.com/docs/api-reference/v2/deprecated:-platform-webhooks/delete-a-webhook -->

# Delete a webhook - Cal.com Docs

Platform / Webhooks
# Delete a webhook
Copy pageThese endpoints are deprecated and will be removed in the future.Copy pageDELETE/v2/oauth-clients/{clientId}/webhooks/{webhookId}Try itDelete a webhook

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/oauth-clients/{clientId}/webhooks/{webhookId} \
  --header 'Authorization: Bearer <token>' \
  --header 'x-cal-secret-key: <x-cal-secret-key>'`
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
    "oAuthClientId": "<string>",
    "id": 123,
    "subscriberUrl": "<string>",
    "active": true,
    "secret": "<string>"
  }
}`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Headers
​x-cal-secret-keystringrequired

OAuth client secret key
#### Path Parameters
​webhookIdstringrequired​clientIdstringrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
