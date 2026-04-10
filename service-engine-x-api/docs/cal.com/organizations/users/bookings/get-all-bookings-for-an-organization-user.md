<!-- Source: https://cal.com/docs/api-reference/v2/orgs-users-bookings/get-all-bookings-for-an-organization-user -->

# Get all bookings for an organization user - Cal.com Docs

Bookings
# Get all bookings for an organization user
Copy pageCopy pageGET/v2/organizations/{orgId}/users/{userId}/bookingsTry itGet all bookings for an organization user

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/users/{userId}/bookings`
```

#### Headers
​Authorizationstring

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​orgIdnumberrequired​userIdnumberrequired
#### Query Parameters
​statusenum<string>[]

Filter bookings by status. If you want to filter by multiple statuses, separate them with a comma.Available options: `upcoming`, `recurring`, `past`, `cancelled`, `unconfirmed` Example:

`"?status=upcoming,past"`​attendeeEmailstring

Filter bookings by the attendee's email address.Example:

`"[email protected]"`​attendeeNamestring

Filter bookings by the attendee's name.Example:

`"John Doe"`​bookingUidstring

Filter bookings by the booking Uid.Example:

`"2NtaeaVcKfpmSZ4CthFdfk"`​eventTypeIdsstring

Filter bookings by event type ids belonging to the user. Event type ids must be separated by a comma.Example:

`"?eventTypeIds=100,200"`​eventTypeIdstring

Filter bookings by event type id belonging to the user.Example:

`"?eventTypeId=100"`​teamsIdsstring

Filter bookings by team ids that user is part of. Team ids must be separated by a comma.Example:

`"?teamIds=50,60"`​teamIdstring

Filter bookings by team id that user is part ofExample:

`"?teamId=50"`​afterStartstring

Filter bookings with start after this date string.Example:

`"?afterStart=2025-03-07T10:00:00.000Z"`​beforeEndstring

Filter bookings with end before this date string.Example:

`"?beforeEnd=2025-03-07T11:00:00.000Z"`​afterCreatedAtstring

Filter bookings that have been created after this date string.Example:

`"?afterCreatedAt=2025-03-07T10:00:00.000Z"`​beforeCreatedAtstring

Filter bookings that have been created before this date string.Example:

`"?beforeCreatedAt=2025-03-14T11:00:00.000Z"`​afterUpdatedAtstring

Filter bookings that have been updated after this date string.Example:

`"?afterUpdatedAt=2025-03-07T10:00:00.000Z"`​beforeUpdatedAtstring

Filter bookings that have been updated before this date string.Example:

`"?beforeUpdatedAt=2025-03-14T11:00:00.000Z"`​sortStartenum<string>

Sort results by their start time in ascending or descending order.Available options: `asc`, `desc` Example:

`"?sortStart=asc OR ?sortStart=desc"`​sortEndenum<string>

Sort results by their end time in ascending or descending order.Available options: `asc`, `desc` Example:

`"?sortEnd=asc OR ?sortEnd=desc"`​sortCreatedenum<string>

Sort results by their creation time (when booking was made) in ascending or descending order.Available options: `asc`, `desc` Example:

`"?sortCreated=asc OR ?sortCreated=desc"`​sortUpdatedAtenum<string>

Sort results by their updated time (for example when booking status changes) in ascending or descending order.Available options: `asc`, `desc` Example:

`"?sortUpdated=asc OR ?sortUpdated=desc"`​takenumberdefault:100

The number of items to returnExample:

`10`​skipnumberdefault:0

The number of items to skipExample:

`0`
#### Response
200 - undefined
