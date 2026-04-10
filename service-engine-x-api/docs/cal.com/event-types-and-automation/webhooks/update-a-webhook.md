<!-- Source: https://cal.com/docs/api-reference/v2/webhooks/update-a-webhook -->

# Update a webhook - Cal.com Docs

Webhooks
# Update a webhook
Copy pageCopy pagePATCH/v2/webhooks/{webhookId}Try itUpdate a webhook

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/webhooks/{webhookId} \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "payloadTemplate": "{\"content\":\"A new event has been scheduled\",\"type\":\"{{type}}\",\"name\":\"{{title}}\",\"organizer\":\"{{organizer.name}}\",\"booker\":\"{{attendees.0.name}}\"}",
  "active": true,
  "subscriberUrl": "<string>",
  "triggers": [
    "BOOKING_CREATED",
    "BOOKING_RESCHEDULED",
    "BOOKING_CANCELLED",
    "BOOKING_CONFIRMED",
    "BOOKING_REJECTED",
    "BOOKING_COMPLETED",
    "BOOKING_NO_SHOW",
    "BOOKING_REOPENED"
  ],
  "secret": "<string>",
  "version": "2021-10-20"
}
'`
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
#### Body
application/json​payloadTemplatestring

The template of the payload that will be sent to the subscriberUrl, check cal.com/docs/core-features/webhooks for more informationExample:

`"{\"content\":\"A new event has been scheduled\",\"type\":\"{{type}}\",\"name\":\"{{title}}\",\"organizer\":\"{{organizer.name}}\",\"booker\":\"{{attendees.0.name}}\"}"`​activeboolean​subscriberUrlstring​triggersenum<string>[]Available options: `BOOKING_CREATED`, `BOOKING_PAYMENT_INITIATED`, `BOOKING_PAID`, `BOOKING_RESCHEDULED`, `BOOKING_REQUESTED`, `BOOKING_CANCELLED`, `BOOKING_REJECTED`, `BOOKING_NO_SHOW_UPDATED`, `FORM_SUBMITTED`, `MEETING_ENDED`, `MEETING_STARTED`, `RECORDING_READY`, `INSTANT_MEETING`, `RECORDING_TRANSCRIPTION_GENERATED`, `OOO_CREATED`, `AFTER_HOSTS_CAL_VIDEO_NO_SHOW`, `AFTER_GUESTS_CAL_VIDEO_NO_SHOW`, `FORM_SUBMITTED_NO_EVENT`, `ROUTING_FORM_FALLBACK_HIT`, `DELEGATION_CREDENTIAL_ERROR`, `WRONG_ASSIGNMENT_REPORT` Example:
```
`[
  "BOOKING_CREATED",
  "BOOKING_RESCHEDULED",
  "BOOKING_CANCELLED",
  "BOOKING_CONFIRMED",
  "BOOKING_REJECTED",
  "BOOKING_COMPLETED",
  "BOOKING_NO_SHOW",
  "BOOKING_REOPENED"
]`
```
​secretstring​versionenum<string>

The version of the webhookAvailable options: `2021-10-20` Example:

`"2021-10-20"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
