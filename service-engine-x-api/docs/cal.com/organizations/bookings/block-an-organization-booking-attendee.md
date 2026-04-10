<!-- Source: https://cal.com/docs/api-reference/v2/orgs-bookings/block-an-organization-booking-attendee -->

# Block an organization booking attendee - Cal.com Docs

Bookings
# Block an organization booking attendee
Copy page

Add the email or domain of a booking attendee to the organization blocklist. All matching upcoming bookings in the organization are silently cancelled.Copy pagePOST/v2/organizations/{orgId}/bookings/blockTry itBlock an organization booking attendee

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/organizations/{orgId}/bookings/block \
  --header 'Content-Type: application/json' \
  --data '
{
  "bookingUid": "booking-uid-123",
  "blockType": "EMAIL"
}
'`
```
200
```
`{
  "status": "success",
  "data": {
    "success": true,
    "message": "Added to blocklist and 3 bookings cancelled",
    "bookingUid": "booking-uid-123",
    "cancelledCount": 3,
    "blockedValue": "[email protected]"
  }
}`
```

#### Headers
​Authorizationstring

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​orgIdnumberrequired
#### Body
application/json​bookingUidstringrequired

The UID of the booking whose attendee should be blockedExample:

`"booking-uid-123"`​blockTypeenum<string>required

Whether to block by email or domain. EMAIL blocks the specific booker email. DOMAIN blocks all emails from the same domain.Available options: `EMAIL`, `DOMAIN` Example:

`"EMAIL"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
