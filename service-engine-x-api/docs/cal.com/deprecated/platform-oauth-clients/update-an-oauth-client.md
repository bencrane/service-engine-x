<!-- Source: https://cal.com/docs/api-reference/v2/deprecated:-platform-oauth-clients/update-an-oauth-client -->

# Update an OAuth client - Cal.com Docs

Platform OAuth Clients
# Update an OAuth client
Copy pageThese endpoints are deprecated and will be removed in the future.Copy pagePATCH/v2/oauth-clients/{clientId}Try itUpdate an OAuth client

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/oauth-clients/{clientId} \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "logo": "<string>",
  "name": "<string>",
  "redirectUris": [
    "<string>"
  ],
  "bookingRedirectUri": "<string>",
  "bookingCancelRedirectUri": "<string>",
  "bookingRescheduleRedirectUri": "<string>",
  "areEmailsEnabled": true,
  "areDefaultEventTypesEnabled": true,
  "areCalendarEventsEnabled": true
}
'`
```
200
```
`{
  "status": "success",
  "data": {
    "id": "clsx38nbl0001vkhlwin9fmt0",
    "name": "MyClient",
    "secret": "secretValue",
    "permissions": [
      "BOOKING_READ",
      "BOOKING_WRITE"
    ],
    "redirectUris": [
      "https://example.com/callback"
    ],
    "organizationId": 1,
    "createdAt": "2024-03-23T08:33:21.851Z",
    "areEmailsEnabled": true,
    "areDefaultEventTypesEnabled": true,
    "areCalendarEventsEnabled": true,
    "logo": "https://example.com/logo.png",
    "bookingRedirectUri": "https://example.com/booking-redirect",
    "bookingCancelRedirectUri": "https://example.com/booking-cancel",
    "bookingRescheduleRedirectUri": "https://example.com/booking-reschedule"
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_
#### Path Parameters
​clientIdstringrequired
#### Body
application/json​logostring​namestring​redirectUrisstring[]​bookingRedirectUristring​bookingCancelRedirectUristring​bookingRescheduleRedirectUristring​areEmailsEnabledboolean​areDefaultEventTypesEnabledboolean

If true, when creating a managed user the managed user will have 4 default event types: 30 and 60 minutes without Cal video, 30 and 60 minutes with Cal video. Set this as false if you want to create a managed user and then manually create event types for the user.​areCalendarEventsEnabledboolean

If true and if managed user has calendar connected, calendar events will be created. Disable it if you manually create calendar events. Default to true.
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
