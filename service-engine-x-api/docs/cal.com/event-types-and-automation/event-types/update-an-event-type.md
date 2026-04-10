<!-- Source: https://cal.com/docs/api-reference/v2/event-types/update-an-event-type -->

# Update an event type - Cal.com Docs

Event Types
# Update an event type
Copy pagePlease make sure to pass in the cal-api-version header value as mentioned in the Headers section. Not passing the correct value will default to an older version of this endpoint.Copy pagePATCH/v2/event-types/{eventTypeId}Try itUpdate an event type

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/event-types/{eventTypeId} \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --header 'cal-api-version: <cal-api-version>' \
  --data '
{
  "lengthInMinutes": 60,
  "lengthInMinutesOptions": [
    15,
    30,
    60
  ],
  "title": "Learn the secrets of masterchief!",
  "slug": "learn-the-secrets-of-masterchief",
  "description": "Discover the culinary wonders of the Argentina by making the best flan ever!",
  "bookingFields": [
    {
      "type": "name",
      "label": "<string>",
      "placeholder": "<string>",
      "disableOnPrefill": true
    }
  ],
  "disableGuests": true,
  "slotInterval": 123,
  "minimumBookingNotice": 123,
  "beforeEventBuffer": 123,
  "afterEventBuffer": 123,
  "scheduleId": 123,
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
  "bookingWindow": {
    "type": "businessDays",
    "value": 5,
    "rolling": true
  },
  "offsetStart": 123,
  "confirmationPolicy": {
    "type": "always",
    "blockUnconfirmedBookingsInBooker": true
  },
  "recurrence": {
    "interval": 10,
    "occurrences": 10,
    "frequency": "yearly"
  },
  "requiresBookerEmailVerification": true,
  "hideCalendarNotes": true,
  "lockTimeZoneToggleOnBookingPage": true,
  "seats": {
    "seatsPerTimeSlot": 4,
    "showAttendeeInfo": true,
    "showAvailabilityCount": true
  },
  "customName": "{Event type title} between {Organiser} and {Scheduler}",
  "useDestinationCalendarEmail": true,
  "hideCalendarEventDetails": true,
  "successRedirectUrl": "https://masterchief.com/argentina/flan/video/9129412",
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
  "hidden": true,
  "bookingRequiresAuthentication": false,
  "disableCancelling": {
    "disabled": true
  },
  "disableRescheduling": {
    "disabled": false,
    "minutesBefore": 60
  },
  "interfaceLanguage": "",
  "allowReschedulingPastBookings": false,
  "allowReschedulingCancelledBookings": false,
  "showOptimizedSlots": false,
  "locations": [
    {
      "type": "address",
      "address": "123 Example St, City, Country",
      "public": true
    }
  ]
}
'`
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
​eventTypeIdnumberrequired
#### Body
application/json​lengthInMinutesnumberExample:

`60`​lengthInMinutesOptionsnumber[]

If you want that user can choose between different lengths of the event you can specify them here. Must include the provided `lengthInMinutes`.Example:
```
`[15, 30, 60]`
```
​titlestringExample:

`"Learn the secrets of masterchief!"`​slugstringExample:

`"learn-the-secrets-of-masterchief"`​descriptionstringExample:

`"Discover the culinary wonders of the Argentina by making the best flan ever!"`​bookingFieldsobject[]

Complete set of booking form fields. This array replaces all existing booking fields. To modify existing fields, first fetch the current event type, then include all desired fields in this array. Sending only one field will remove all other custom fields, keeping only default fields plus the provided one.
- Option 1
- Option 2
- Option 3
- Option 4
- Option 5
- Option 6
- Option 7
- Option 8
- Option 9
- Option 10
- Option 11
- Option 12
- Option 13
- Option 14
- Option 15
- Option 16
- Option 17
- Option 18
- Option 19

Show child attributes​disableGuestsboolean

If true, person booking this event can't add guests via their emails.​slotIntervalnumber

Number representing length of each slot when event is booked. By default it equal length of the event type.
If event length is 60 minutes then we would have slots 9AM, 10AM, 11AM etc. but if it was changed to 30 minutes then
we would have slots 9AM, 9:30AM, 10AM, 10:30AM etc. as the available times to book the 60 minute event.​minimumBookingNoticenumber

Minimum number of minutes before the event that a booking can be made.​beforeEventBuffernumber

Extra time automatically blocked on your calendar before a meeting starts. This gives you time to prepare, review notes, or transition from your previous activity.​afterEventBuffernumber

Extra time automatically blocked on your calendar after a meeting ends. This gives you time to wrap up, add notes, or decompress before your next commitment.​scheduleIdnumber

If you want that this event has different schedule than user's default one you can specify it here.​bookingLimitsCountobject

Limit how many times this event can be booked
- Option 1
- Option 2

Show child attributes​bookerActiveBookingsLimitobject

Limit the number of active bookings a booker can make for this event type.
- Option 1
- Option 2

Show child attributes​onlyShowFirstAvailableSlotboolean

This will limit your availability for this event type to one slot per day, scheduled at the earliest available time.​bookingLimitsDurationobject

Limit total amount of time that this event can be booked
- Option 1
- Option 2

Show child attributes​bookingWindowobject

Limit how far in the future this event can be booked
- Option 1
- Option 2
- Option 3
- Option 4

Show child attributes​offsetStartnumber

Offset timeslots shown to bookers by a specified number of minutes​bookerLayoutsobject

Should booker have week, month or column view. Specify default layout and enabled layouts user can pick.

Show child attributes​confirmationPolicyobject

Specify how the booking needs to be manually confirmed before it is pushed to the integrations and a confirmation mail is sent.
- Option 1
- Option 2

Show child attributes​recurrenceobject

Create a recurring event type.
- Option 1
- Option 2

Show child attributes​requiresBookerEmailVerificationboolean​hideCalendarNotesboolean​lockTimeZoneToggleOnBookingPageboolean​colorobject

Show child attributes​seatsobject

Create an event type with multiple seats.
- Option 1
- Option 2

Show child attributes​customNamestring

Customizable event name with valid variables:
{Event type title}, {Organiser}, {Scheduler}, {Location}, {Organiser first name},
{Scheduler first name}, {Scheduler last name}, {Event duration}, {LOCATION},
{HOST/ATTENDEE}, {HOST}, {ATTENDEE}, {USER}Example:

`"{Event type title} between {Organiser} and {Scheduler}"`​destinationCalendarobject

Show child attributes​useDestinationCalendarEmailboolean​hideCalendarEventDetailsboolean​successRedirectUrlstring

A valid URL where the booker will redirect to, once the booking is completed successfullyExample:

`"https://masterchief.com/argentina/flan/video/9129412"`​hideOrganizerEmailboolean

Boolean to Hide organizer's email address from the booking screen, email notifications, and calendar events​calVideoSettingsobject

Cal video settings for the event type

Show child attributes​hiddenboolean​bookingRequiresAuthenticationbooleandefault:false

Boolean to require authentication for booking this event type via api. If true, only authenticated users who are the event-type owner or org/team admin/owner can book this event type.​disableCancellingobject

Settings for disabling cancelling of this event type.

Show child attributesExample:
```
`{ "disabled": true }`
```
​disableReschedulingobject

Settings for disabling rescheduling of this event type. Can be always disabled or disabled when less than X minutes before the meeting.

Show child attributesExample:
```
`{ "disabled": false, "minutesBefore": 60 }`
```
​interfaceLanguageenum<string>

Set preferred language for the booking interface. Use empty string for visitor's browser language (default).Available options: ``, `en`, `ar`, `az`, `bg`, `bn`, `ca`, `cs`, `da`, `de`, `el`, `es`, `es-419`, `eu`, `et`, `fi`, `fr`, `he`, `hu`, `it`, `ja`, `km`, `ko`, `nl`, `no`, `pl`, `pt-BR`, `pt`, `ro`, `ru`, `sk-SK`, `sr`, `sv`, `tr`, `uk`, `vi`, `zh-CN`, `zh-TW` ​allowReschedulingPastBookingsbooleandefault:false

Enabling this option allows for past events to be rescheduled.​allowReschedulingCancelledBookingsbooleandefault:false

When enabled, users will be able to create a new booking when trying to reschedule a cancelled booking.​showOptimizedSlotsbooleandefault:false

Arrange time slots to optimize availability.​locationsobject[]

Locations where the event will take place. If not provided, cal video link will be used as the location. Note: Setting a location to a conferencing app does not install the app - the app must already be installed. Via API, only Google Meet (google-meet), Microsoft Teams (office365-video), and Zoom (zoom) can be installed. Cal Video (cal-video) is installed by default. All other conferencing apps must be connected via the Cal.com web app and are not available for Platform plan customers. You can only set an event type location to an app that has already been installed or connected.
- Option 1
- Option 2
- Option 3
- Option 4
- Option 5
- Option 6
- Option 7

Show child attributes
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
