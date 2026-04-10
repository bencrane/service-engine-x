<!-- Source: https://cal.com/docs/api-reference/v2/deprecated:-platform-webhooks/create-a-webhook -->

# Create a webhook - Cal.com Docs

Platform / Webhooks
# Create a webhook
Copy pageThese endpoints are deprecated and will be removed in the future.Copy pagePOST/v2/oauth-clients/{clientId}/webhooksTry itCreate a webhook

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/oauth-clients/{clientId}/webhooks \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --header 'x-cal-secret-key: <x-cal-secret-key>' \
  --data '
{
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
  "payloadTemplate": "{\"content\":\"A new event has been scheduled\",\"type\":\"{{type}}\",\"name\":\"{{title}}\",\"organizer\":\"{{organizer.name}}\",\"booker\":\"{{attendees.0.name}}\"}",
  "secret": "<string>",
  "version": "2021-10-20"
}
'`
```
201
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
​clientIdstringrequired
#### Body
application/json​activebooleanrequired​subscriberUrlstringrequired​triggersenum<string>[]requiredAvailable options: `BOOKING_CREATED`, `BOOKING_PAYMENT_INITIATED`, `BOOKING_PAID`, `BOOKING_RESCHEDULED`, `BOOKING_REQUESTED`, `BOOKING_CANCELLED`, `BOOKING_REJECTED`, `BOOKING_NO_SHOW_UPDATED`, `FORM_SUBMITTED`, `MEETING_ENDED`, `MEETING_STARTED`, `RECORDING_READY`, `INSTANT_MEETING`, `RECORDING_TRANSCRIPTION_GENERATED`, `OOO_CREATED`, `AFTER_HOSTS_CAL_VIDEO_NO_SHOW`, `AFTER_GUESTS_CAL_VIDEO_NO_SHOW`, `FORM_SUBMITTED_NO_EVENT`, `ROUTING_FORM_FALLBACK_HIT`, `DELEGATION_CREDENTIAL_ERROR`, `WRONG_ASSIGNMENT_REPORT` Example:
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
​payloadTemplatestring

The template of the payload that will be sent to the subscriberUrl, check cal.com/docs/core-features/webhooks for more informationExample:

`"{\"content\":\"A new event has been scheduled\",\"type\":\"{{type}}\",\"name\":\"{{title}}\",\"organizer\":\"{{organizer.name}}\",\"booker\":\"{{attendees.0.name}}\"}"`​secretstring​versionenum<string>

The version of the webhookAvailable options: `2021-10-20` Example:

`"2021-10-20"`
#### Response
201 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
