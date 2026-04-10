<!-- Source: https://cal.com/docs/api-reference/v2/deprecated:-platform-webhooks/get-all-webhooks -->

# Get all webhooks - Cal.com Docs

Platform / Webhooks
# Get all webhooks
Copy pageThese endpoints are deprecated and will be removed in the future.Copy pageGET/v2/oauth-clients/{clientId}/webhooksTry itGet all webhooks

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/oauth-clients/{clientId}/webhooks \
  --header 'Authorization: Bearer <token>' \
  --header 'x-cal-secret-key: <x-cal-secret-key>'`
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
      "oAuthClientId": "<string>",
      "id": 123,
      "subscriberUrl": "<string>",
      "active": true,
      "secret": "<string>"
    }
  ]
}`
```

#### Authorizations
​Authorizationstringheaderrequired

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.
#### Headers
​x-cal-secret-keystringrequired

OAuth client secret key
#### Path Parameters
​clientIdstringrequired
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
