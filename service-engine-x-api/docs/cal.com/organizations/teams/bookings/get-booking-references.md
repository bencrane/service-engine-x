<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-bookings/get-booking-references -->

# Get booking references - Cal.com Docs

Bookings
# Get booking references
Copy page

Required membership role: `team admin`. PBAC permission: `booking.readTeamBookings`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/teams/{teamId}/bookings/{bookingUid}/referencesTry itGet booking references

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/bookings/{bookingUid}/references`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "type": "<string>",
      "eventUid": "<string>",
      "destinationCalendarId": "<string>",
      "id": 123
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
​bookingUidstringrequired​teamIdnumberrequired​orgIdnumberrequired
#### Query Parameters
​typeenum<string>

Filter booking references by typeAvailable options: `google_calendar`, `office365_calendar`, `daily_video`, `google_video`, `office365_video`, `zoom_video` Example:

`"google_calendar"`
#### Response
200 - application/json​statusenum<string>required

The status of the request, always 'success' for successful responsesAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Booking References

Show child attributes
