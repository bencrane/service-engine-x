<!-- Source: https://cal.com/docs/api-reference/v2/orgs-webhooks/get-all-webhooks -->

# Get all webhooks - Cal.com Docs

Webhooks
# Get all webhooks
Copy page

Required membership role: `org admin`. PBAC permission: `webhook.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/webhooksTry itGet all webhooks

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/webhooks`
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
      "teamId": 123,
      "id": 123,
      "subscriberUrl": "<string>",
      "active": true,
      "secret": "<string>"
    }
  ]
}`
```

#### Headers
​Authorizationstring

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​orgIdnumberrequired
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
