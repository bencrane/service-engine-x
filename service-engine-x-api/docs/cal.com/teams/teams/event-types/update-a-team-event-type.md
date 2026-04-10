<!-- Source: https://cal.com/docs/api-reference/v2/teams-event-types/update-a-team-event-type -->

# Update a team event type

`PATCH /v2/teams/{teamId}/event-types/{eventTypeId}`

Update a team event type

## Authorization

This endpoint requires authentication with a **Bearer token**.

```
Authorization: Bearer <your_api_key>
```

## Headers

| Name | Required | Description |
|------|----------|-------------|
| `Authorization` | Yes | Bearer token |
| `cal-api-version` | Yes | API version: `2024-08-13` |

## Path Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `teamId` | `number` | Yes |  |
| `eventTypeId` | `number` | Yes |  |

## Request Body

- **`lengthInMinutes`** (`number`)
  - Example: `60`
- **`lengthInMinutesOptions`** (`number[]`): If you want that user can choose between different lengths of the event you can specify them here. Must include the provided `lengthInMinutes`.
- **`title`** (`string`)
  - Example: `Learn the secrets of masterchief!`
- **`slug`** (`string`)
  - Example: `learn-the-secrets-of-masterchief`
- **`description`** (`string`)
  - Example: `Discover the culinary wonders of the Argentina by making the best flan ever!`
- **`bookingFields`** (`object | object | object[]`): Complete set of booking form fields. This array replaces all existing booking fields. To modify existing fields, first fetch the current event type, then include all desired fields in this array. Sending only one field will remove all other custom fi...
- **`disableGuests`** (`boolean`): If true, person booking this event can't add guests via their emails.
- **`slotInterval`** (`number`): Number representing length of each slot when event is booked. By default it equal length of the event type.
      If event length is 60 minutes then we would have slots 9AM, 10AM, 11AM etc. but if it was changed to 30 minutes then
      we would have...
- **`minimumBookingNotice`** (`number`): Minimum number of minutes before the event that a booking can be made.
- **`beforeEventBuffer`** (`number`): Extra time automatically blocked on your calendar before a meeting starts. This gives you time to prepare, review notes, or transition from your previous activity.
- **`afterEventBuffer`** (`number`): Extra time automatically blocked on your calendar after a meeting ends. This gives you time to wrap up, add notes, or decompress before your next commitment.
- **`scheduleId`** (`number`): If you want that this event has different schedule than user's default one you can specify it here.
- **`bookingLimitsCount`** (`object | object`): Limit how many times this event can be booked
- **`bookerActiveBookingsLimit`** (`object | object`): Limit the number of active bookings a booker can make for this event type.
- **`onlyShowFirstAvailableSlot`** (`boolean`): This will limit your availability for this event type to one slot per day, scheduled at the earliest available time.
- **`bookingLimitsDuration`** (`object | object`): Limit total amount of time that this event can be booked
- **`bookingWindow`** (`object | object | object`): Limit how far in the future this event can be booked
- **`offsetStart`** (`number`): Offset timeslots shown to bookers by a specified number of minutes
- **`bookerLayouts`** (`object`): Should booker have week, month or column view. Specify default layout and enabled layouts user can pick.
- **`confirmationPolicy`** (`object | object`): Specify how the booking needs to be manually confirmed before it is pushed to the integrations and a confirmation mail is sent.
- **`recurrence`** (`object | object`): Create a recurring event type.
- **`requiresBookerEmailVerification`** (`boolean`)
- **`hideCalendarNotes`** (`boolean`)
- **`lockTimeZoneToggleOnBookingPage`** (`boolean`)
- **`color`** (`object`)
  - **`lightThemeHex`** **required** (`string`): Color used for event types in light theme
    - Example: `#292929`
  - **`darkThemeHex`** **required** (`string`): Color used for event types in dark theme
    - Example: `#fafafa`
- **`seats`** (`object | object`): Create an event type with multiple seats.
- **`customName`** (`string`): Customizable event name with valid variables:
      {Event type title}, {Organiser}, {Scheduler}, {Location}, {Organiser first name},
      {Scheduler first name}, {Scheduler last name}, {Event duration}, {LOCATION},
      {HOST/ATTENDEE}, {HOST}, {A...
  - Example: `{Event type title} between {Organiser} and {Scheduler}`
- **`destinationCalendar`** (`object`)
  - **`integration`** **required** (`string`): The integration type of the destination calendar. Refer to the /api/v2/calendars endpoint to retrieve the integration type of your connected calendars.
  - **`externalId`** **required** (`string`): The external ID of the destination calendar. Refer to the /api/v2/calendars endpoint to retrieve the external IDs of your connected calendars.
- **`useDestinationCalendarEmail`** (`boolean`)
- **`hideCalendarEventDetails`** (`boolean`)
- **`successRedirectUrl`** (`string`): A valid URL where the booker will redirect to, once the booking is completed successfully
  - Example: `https://masterchief.com/argentina/flan/video/9129412`
- **`hideOrganizerEmail`** (`boolean`): Boolean to Hide organizer's email address from the booking screen, email notifications, and calendar events
- **`calVideoSettings`** (`object`): Cal video settings for the event type
- **`hidden`** (`boolean`)
- **`bookingRequiresAuthentication`** (`boolean`): Boolean to require authentication for booking this event type via api. If true, only authenticated users who are the event-type owner or org/team admin/owner can book this event type.
  - Default: `False`
- **`disableCancelling`** (`object`): Settings for disabling cancelling of this event type.
- **`disableRescheduling`** (`object`): Settings for disabling rescheduling of this event type. Can be always disabled or disabled when less than X minutes before the meeting.
- **`interfaceLanguage`** (`enum`): Set preferred language for the booking interface. Use empty string for visitor's browser language (default).
  - Enum values: ``, `en`, `ar`, `az`, `bg`, `bn`, `ca`, `cs`, `da`, `de`, `el`, `es`, `es-419`, `eu`, `et`, `fi`, `fr`, `he`, `hu`, `it`, `ja`, `km`, `ko`, `nl`, `no`, `pl`, `pt-BR`, `pt`, `ro`, `ru`, `sk-SK`, `sr`, `sv`, `tr`, `uk`, `vi`, `zh-CN`, `zh-TW`
- **`allowReschedulingPastBookings`** (`boolean`): Enabling this option allows for past events to be rescheduled.
  - Default: `False`
- **`allowReschedulingCancelledBookings`** (`boolean`): When enabled, users will be able to create a new booking when trying to reschedule a cancelled booking.
  - Default: `False`
- **`showOptimizedSlots`** (`boolean`): Arrange time slots to optimize availability.
  - Default: `False`
- **`schedulingType`** (`enum`): The scheduling type for the team event - collective or roundRobin. ❗If you change scheduling type you must also provide `hosts` or `assignAllTeamMembers` in the request body, otherwise the event type will have no hosts - this is required because
    ...
  - Enum values: `collective`, `roundRobin`
  - Example: `collective`
- **`hosts`** (`object[]`): Hosts contain specific team members you want to assign to this event type, but if you want to assign all team members, use `assignAllTeamMembers: true` instead and omit this field. For platform customers the hosts can include userIds only of managed ...
  Array items:
  - **`userId`** **required** (`number`): Which user is the host of this event
  - **`mandatory`** (`boolean`): Only relevant for round robin event types. If true then the user must attend round robin event always.
  - **`priority`** (`enum`)
    - Enum values: `lowest`, `low`, `medium`, `high`, `highest`
- **`assignAllTeamMembers`** (`boolean`): If true, all current and future team members will be assigned to this event type. Provide either assignAllTeamMembers or hosts but not both
- **`locations`** (`object | object | object[]`): Locations where the event will take place. If not provided, cal video link will be used as the location. Note: Setting a location to a conferencing app does not install the app - the app must already be installed. Via API, only Google Meet (google-me...
- **`emailSettings`** (`object`): Email settings for this event type. Only available for organization team event types.
- **`rescheduleWithSameRoundRobinHost`** (`boolean`): Rescheduled events will be assigned to the same host as initially scheduled.

### Example Request Body

```json
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
      "type": "...",
      "label": "...",
      "placeholder": "...",
      "disableOnPrefill": "..."
    }
  ],
  "disableGuests": true,
  "slotInterval": 0.0,
  "minimumBookingNotice": 0.0,
  "beforeEventBuffer": 0.0,
  "afterEventBuffer": 0.0,
  "scheduleId": 0.0,
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
  "offsetStart": 0.0,
  "bookerLayouts": {
    "defaultLayout": "month",
    "enabledLayouts": [
      "..."
    ]
  },
  "confirmationPolicy": {
    "type": "always",
    "noticeThreshold": {},
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
  "color": {
    "lightThemeHex": "#292929",
    "darkThemeHex": "#fafafa"
  },
  "seats": {
    "seatsPerTimeSlot": 4,
    "showAttendeeInfo": true,
    "showAvailabilityCount": true
  },
  "customName": "{Event type title} between {Organiser} and {Scheduler}",
  "destinationCalendar": {
    "integration": "string",
    "externalId": "string"
  },
  "useDestinationCalendarEmail": true,
  "hideCalendarEventDetails": true,
  "successRedirectUrl": "https://masterchief.com/argentina/flan/video/9129412",
  "hideOrganizerEmail": true,
  "calVideoSettings": {
    "disableRecordingForOrganizer": true,
    "disableRecordingForGuests": true,
    "redirectUrlOnExit": "string",
    "enableAutomaticRecordingForOrganizer": true,
    "enableAutomaticTranscription": true,
    "disableTranscriptionForGuests": true,
    "disableTranscriptionForOrganizer": true,
    "sendTranscriptionEmails": true
  },
  "hidden": true,
  "bookingRequiresAuthentication": true,
  "disableCancelling": {
    "disabled": true
  },
  "disableRescheduling": {
    "disabled": false,
    "minutesBefore": 60
  },
  "interfaceLanguage": "",
  "allowReschedulingPastBookings": true,
  "allowReschedulingCancelledBookings": true,
  "showOptimizedSlots": true,
  "schedulingType": "collective",
  "hosts": [
    {
      "userId": 0.0,
      "mandatory": true,
      "priority": "lowest"
    }
  ],
  "assignAllTeamMembers": true,
  "locations": [
    {
      "type": "...",
      "address": "...",
      "public": "..."
    }
  ],
  "emailSettings": {
    "disableEmailsToAttendees": true,
    "disableEmailsToHosts": true
  },
  "rescheduleWithSameRoundRobinHost": true
}
```

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object | object[]`)

## Example Request

```bash
curl -X PATCH \
  "https://api.cal.com/v2/teams/<teamId>/event-types/<eventTypeId>" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '<request_body>'
```
