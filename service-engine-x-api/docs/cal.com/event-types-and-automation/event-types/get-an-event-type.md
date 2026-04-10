<!-- Source: https://cal.com/docs/api-reference/v2/event-types/get-an-event-type -->

# Get an event type - Cal.com Docs

Event Types
# Get an event type
Copy pagePlease make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.

Access control: This endpoint fetches an event type by ID and returns it only if the authenticated user is authorized. Authorization is granted to:

- System admins

- The event type owner

- Hosts of the event type or users assigned to the event type

- Team admins/owners of the team that owns the team event type

- Organization admins/owners of the event type owner’s organization

- Organization admins/owners of the team’s parent organization

Note: Update and delete endpoints remain restricted to the event type owner only.Copy pageGET/v2/event-types/{eventTypeId}Try itGet an event type

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/event-types/{eventTypeId} \
  --header 'Authorization: <authorization>' \
  --header 'cal-api-version: <cal-api-version>'`
```
200
```
`{
  "status": "success",
  "data": {
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
}`
```

#### Headers
​cal-api-versionstringdefault:2024-06-14required

Must be set to 2024-06-14. If not set to this value, the endpoint will default to an older version.​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​eventTypeIdstringrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired
- Option 1
- Option 2

Show child attributes
