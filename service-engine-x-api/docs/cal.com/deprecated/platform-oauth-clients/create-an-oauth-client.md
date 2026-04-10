<!-- Source: https://cal.com/docs/api-reference/v2/deprecated:-platform-oauth-clients/create-an-oauth-client -->

# Create an OAuth client - Cal.com Docs

Platform OAuth Clients
# Create an OAuth client
Copy pageThese endpoints are deprecated and will be removed in the future.Copy pagePOST/v2/oauth-clientsTry itCreate an OAuth client

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/oauth-clients \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "name": "<string>",
  "redirectUris": [
    "<string>"
  ],
  "permissions": [
    "EVENT_TYPE_READ"
  ],
  "logo": "<string>",
  "bookingRedirectUri": "<string>",
  "bookingCancelRedirectUri": "<string>",
  "bookingRescheduleRedirectUri": "<string>",
  "areEmailsEnabled": true,
  "areDefaultEventTypesEnabled": false,
  "areCalendarEventsEnabled": true
}
'`
```
201
```
`{
  "status": "success",
  "data": {
    "clientId": "clsx38nbl0001vkhlwin9fmt0",
    "clientSecret": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoib2F1dGgtY2xpZW50Iiwi"
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_
#### Body
application/json​namestringrequired​redirectUrisstring[]required​permissionsenum<string>[]required

Array of permission keys like ["BOOKING_READ", "BOOKING_WRITE"]. Use ["*"] to grant all permissions.Available options: `EVENT_TYPE_READ`, `EVENT_TYPE_WRITE`, `BOOKING_READ`, `BOOKING_WRITE`, `SCHEDULE_READ`, `SCHEDULE_WRITE`, `APPS_READ`, `APPS_WRITE`, `PROFILE_READ`, `PROFILE_WRITE`, `*` ​logostring​bookingRedirectUristring​bookingCancelRedirectUristring​bookingRescheduleRedirectUristring​areEmailsEnabledboolean​areDefaultEventTypesEnabledbooleandefault:false

If true, when creating a managed user the managed user will have 4 default event types: 30 and 60 minutes without Cal video, 30 and 60 minutes with Cal video. Set this as false if you want to create a managed user and then manually create event types for the user.​areCalendarEventsEnabledbooleandefault:true

If true and if managed user has calendar connected, calendar events will be created. Disable it if you manually create calendar events. Default to true.
#### Response
201 - application/json

Create an OAuth client​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributesExample:
```
`{
  "clientId": "clsx38nbl0001vkhlwin9fmt0",
  "clientSecret": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoib2F1dGgtY2xpZW50Iiwi"
}`
```
