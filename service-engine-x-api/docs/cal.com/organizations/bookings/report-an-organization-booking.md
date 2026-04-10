<!-- Source: https://cal.com/docs/api-reference/v2/orgs-bookings/report-an-organization-booking -->

# Report an organization booking - Cal.com Docs

Bookings
# Report an organization booking
Copy page

Report a booking within the organization. A booking report is created and the reported booking along with other matching upcoming bookings are silently cancelled.Copy pagePOST/v2/organizations/{orgId}/bookings/reportTry itReport an organization booking

cURL
```
`curl --request POST \
  --url https://api.cal.com/v2/organizations/{orgId}/bookings/report \
  --header 'Content-Type: application/json' \
  --data '
{
  "bookingUid": "booking-uid-123",
  "reason": "SPAM",
  "reportType": "EMAIL",
  "description": "<string>"
}
'`
```
200
```
`{
  "status": "success",
  "data": {
    "success": true,
    "message": "Booking reported and cancelled successfully",
    "bookingUid": "booking-uid-123",
    "reportedCount": 1,
    "cancelledCount": 3
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

The UID of the booking to reportExample:

`"booking-uid-123"`​reasonenum<string>required

The reason for reporting the bookingAvailable options: `SPAM`, `DONT_KNOW_PERSON`, `OTHER` Example:

`"SPAM"`​reportTypeenum<string>required

Whether to report by email or domain. EMAIL targets the specific booker email. DOMAIN targets all emails from the same domain.Available options: `EMAIL`, `DOMAIN` Example:

`"EMAIL"`​descriptionstring

Additional description for the report
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
