<!-- Source: https://cal.com/docs/api-reference/v2/deprecated:-platform-oauth-clients/get-an-oauth-client -->

# Get an OAuth client - Cal.com Docs

Platform OAuth Clients
# Get an OAuth client
Copy pageThese endpoints are deprecated and will be removed in the future.Copy pageGET/v2/oauth-clients/{clientId}Try itGet an OAuth client

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/oauth-clients/{clientId} \
  --header 'Authorization: <authorization>'`
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
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
