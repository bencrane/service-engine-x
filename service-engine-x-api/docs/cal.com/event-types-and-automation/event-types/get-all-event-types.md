<!-- Source: https://cal.com/docs/api-reference/v2/event-types/get-all-event-types -->

# Get all event types - Cal.com Docs

Event Types
# Get all event types
Copy page

Hidden event types are returned only if authentication is provided and it belongs to the event type owner.

Use the optional `sortCreatedAt` query parameter to order results by creation date (by ID). Accepts “asc” (oldest first) or “desc” (newest first). When not provided, no explicit ordering is applied.
Please make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pageGET/v2/event-typesTry itGet all event types

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/event-types \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "id": 1,
      "lengthInMinutes": 60,
      "title": "Learn the secrets of masterchief!",
      "slug": "learn-the-secrets-of-masterchief",
      "description": "Discover the culinary wonders of Argentina by making the best flan ever!",
      "locations": [
        {
          "type": "address",
          "address": "123 Example St, City, Country",
          "public": true
        }
      ],
      "bookingFields": [
        {
          "type": "name",
          "label": "<string>",
          "placeholder": "<string>",
          "isDefault": true,
          "slug": "name",
          "required": true,
          "disableOnPrefill": true
        }
      ],
      "disableGuests": true,
      "recurrence": {
        "interval": 10,
        "occurrences": 10,
        "frequency": "yearly"
      },
      "metadata": {},
      "price": 123,
      "currency": "<string>",
      "lockTimeZoneToggleOnBookingPage": true,
      "forwardParamsSuccessRedirect": true,
      "successRedirectUrl": "<string>",
      "isInstantEvent": true,
      "scheduleId": 123,
      "hidden": true,
      "bookingRequiresAuthentication": true,
      "ownerId": 10,
      "users": [
        {
          "id": 123,
          "name": "<string>",
          "username": "<string>",
          "avatarUrl": "<string>",
          "weekStart": "<string>",
          "brandColor": "<string>",
          "darkBrandColor": "<string>",
          "metadata": {}
        }
      ],
      "bookingUrl": "https://cal.com/john-doe/30min",
      "lengthInMinutesOptions": [
        15,
        30,
        60
      ],
      "slotInterval": 60,
      "minimumBookingNotice": 0,
      "beforeEventBuffer": 0,
      "afterEventBuffer": 0,
      "seatsPerTimeSlot": 123,
      "seatsShowAvailabilityCount": true,
      "bookingLimitsCount": {
        "day": 1,
        "week": 2,
        "month": 3,
        "year": 4
      },
      "bookerActiveBookingsLimit": {
        "maximumActiveBookings": 3,
        "offerReschedule": true
      },
      "onlyShowFirstAvailableSlot": true,
      "bookingLimitsDuration": {
        "day": 60,
        "week": 120,
        "month": 180,
        "year": 240
      },
      "bookingWindow": [
        {
          "type": "businessDays",
          "value": 5,
          "rolling": true
        }
      ],
      "bookerLayouts": {
        "defaultLayout": "month",
        "enabledLayouts": [
          "month"
        ]
      },
      "confirmationPolicy": {
        "type": "always",
        "blockUnconfirmedBookingsInBooker": true,
        "noticeThreshold": {
          "unit": "minutes",
          "count": 30
        }
      },
      "requiresBookerEmailVerification": true,
      "hideCalendarNotes": true,
      "color": {
        "lightThemeHex": "#292929",
        "darkThemeHex": "#fafafa"
      },
      "seats": {
        "seatsPerTimeSlot": 4,
        "showAttendeeInfo": true,
        "showAvailabilityCount": true
      },
      "offsetStart": 123,
      "customName": "<string>",
      "destinationCalendar": {
        "integration": "<string>",
        "externalId": "<string>"
      },
      "useDestinationCalendarEmail": true,
      "hideCalendarEventDetails": true,
      "hideOrganizerEmail": true,
      "calVideoSettings": {
        "disableRecordingForOrganizer": true,
        "disableRecordingForGuests": true,
        "redirectUrlOnExit": "<string>",
        "enableAutomaticRecordingForOrganizer": true,
        "enableAutomaticTranscription": true,
        "disableTranscriptionForGuests": true,
        "disableTranscriptionForOrganizer": true,
        "sendTranscriptionEmails": true
      },
      "disableCancelling": {
        "disabled": true
      },
      "disableRescheduling": {
        "disabled": true,
        "minutesBefore": 60
      },
      "interfaceLanguage": "<string>",
      "allowReschedulingPastBookings": true,
      "allowReschedulingCancelledBookings": true,
      "showOptimizedSlots": true
    }
  ]
}`
```

#### Headers
​cal-api-versionstringdefault:2024-06-14required

Must be set to 2024-06-14. If not set to this value, the endpoint will default to an older version.​Authorizationstring

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Query Parameters
​usernamestring

The username of the user to get event types for. If only username provided will get all event types.​eventSlugstring

Slug of event type to return. Notably, if eventSlug is provided then username must be provided too, because multiple users can have event with same slug.​usernamesstring

Get dynamic event type for multiple usernames separated by comma. e.g `usernames=alice,bob`​orgSlugstring

slug of the user's organization if he is in one, orgId is not required if using this parameter​orgIdnumber

ID of the organization of the user you want the get the event-types of, orgSlug is not needed when using this parameter​sortCreatedAtenum<string>

Sort event types by creation date. When not provided, no explicit ordering is applied.Available options: `asc`, `desc` 
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Show child attributes
