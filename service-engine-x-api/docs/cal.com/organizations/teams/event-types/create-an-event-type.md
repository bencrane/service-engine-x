<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-event-types/create-an-event-type -->

# Create an event type

Required membership role: `team admin`. PBAC permission: `eventType.create`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`POST /v2/organizations/{orgId}/teams/{teamId}/event-types`

**Tags:** Orgs / Teams / Event Types

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `orgId` **required**

**Type:** `number`

## Header Parameters

### `Authorization` *optional*

**Type:** `string`

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_

### `x-cal-secret-key` *optional*

**Type:** `string`

For platform customers - OAuth client secret key

### `x-cal-client-id` *optional*

**Type:** `string`

For platform customers - OAuth client ID

## Request Body

**Required:** Yes

**Content-Type:** `application/json`

- **`lengthInMinutes`** (number) **required**
- **`lengthInMinutesOptions`** (number[]) *optional*
  If you want that user can choose between different lengths of the event you can specify them here. Must include the provided `lengthInMinutes`.
- **`title`** (string) **required**
- **`slug`** (string) **required**
- **`description`** (string) *optional*
- **`bookingFields`** (object | object | object | object[]) *optional*
  Custom fields that can be added to the booking form when the event is booked by someone. By default booking form has name and email field.
- **`disableGuests`** (boolean) *optional*
  If true, person booking this event can't add guests via their emails.
- **`slotInterval`** (number) *optional*
  Number representing length of each slot when event is booked. By default it equal length of the event type.
      If event length is 60 minutes then we would have slots 9AM, 10AM, 11AM etc. but if it was changed to 30 minutes then
      we would have slots 9AM, 9:30AM, 10AM, 10:30AM etc. as the available times to book the 60 minute event.
- **`minimumBookingNotice`** (number) *optional*
  Minimum number of minutes before the event that a booking can be made.
- **`beforeEventBuffer`** (number) *optional*
  Extra time automatically blocked on your calendar before a meeting starts. This gives you time to prepare, review notes, or transition from your previous activity.
- **`afterEventBuffer`** (number) *optional*
  Extra time automatically blocked on your calendar after a meeting ends. This gives you time to wrap up, add notes, or decompress before your next commitment.
- **`scheduleId`** (number) *optional*
  If you want that this event has different schedule than user's default one you can specify it here.
- **`bookingLimitsCount`** (object | object) *optional*
  Limit how many times this event can be booked
- **`bookerActiveBookingsLimit`** (object | object) *optional*
  Limit the number of active bookings a booker can make for this event type.
- **`onlyShowFirstAvailableSlot`** (boolean) *optional*
  This will limit your availability for this event type to one slot per day, scheduled at the earliest available time.
- **`bookingLimitsDuration`** (object | object) *optional*
  Limit total amount of time that this event can be booked
- **`bookingWindow`** (object | object | object | object) *optional*
  Limit how far in the future this event can be booked
- **`offsetStart`** (number) *optional*
  Offset timeslots shown to bookers by a specified number of minutes
- **`bookerLayouts`** (object) *optional*
  - **`defaultLayout`** (`"month"` | `"week"` | `"column"`) **required**
    Allowed values: `month`, `week`, `column`
  - **`enabledLayouts`** (`"month"` | `"week"` | `"column"`[]) **required**
    Array of valid layouts - month, week or column

- **`confirmationPolicy`** (object | object) *optional*
  Specify how the booking needs to be manually confirmed before it is pushed to the integrations and a confirmation mail is sent.
- **`recurrence`** (object | object) *optional*
  Create a recurring event type.
- **`requiresBookerEmailVerification`** (boolean) *optional*
- **`hideCalendarNotes`** (boolean) *optional*
- **`lockTimeZoneToggleOnBookingPage`** (boolean) *optional*
- **`color`** (object) *optional*
  - **`lightThemeHex`** (string) **required**
    Color used for event types in light theme
  - **`darkThemeHex`** (string) **required**
    Color used for event types in dark theme

- **`seats`** (object | object) *optional*
  Create an event type with multiple seats.
- **`customName`** (string) *optional*
  Customizable event name with valid variables:
      {Event type title}, {Organiser}, {Scheduler}, {Location}, {Organiser first name},
      {Scheduler first name}, {Scheduler last name}, {Event duration}, {LOCATION},
      {HOST/ATTENDEE}, {HOST}, {ATTENDEE}, {USER}
- **`destinationCalendar`** (object) *optional*
  - **`integration`** (string) **required**
    The integration type of the destination calendar. Refer to the /api/v2/calendars endpoint to retrieve the integration type of your connected calendars.
  - **`externalId`** (string) **required**
    The external ID of the destination calendar. Refer to the /api/v2/calendars endpoint to retrieve the external IDs of your connected calendars.

- **`useDestinationCalendarEmail`** (boolean) *optional*
- **`hideCalendarEventDetails`** (boolean) *optional*
- **`successRedirectUrl`** (string) *optional*
  A valid URL where the booker will redirect to, once the booking is completed successfully
- **`hideOrganizerEmail`** (boolean) *optional*
  Boolean to Hide organizer's email address from the booking screen, email notifications, and calendar events
- **`calVideoSettings`** (object) *optional*
  - **`disableRecordingForOrganizer`** (boolean) *optional*
    If true, the organizer will not be able to record the meeting
  - **`disableRecordingForGuests`** (boolean) *optional*
    If true, the guests will not be able to record the meeting
  - **`redirectUrlOnExit`** (string) *optional*
    URL to which participants are redirected when they exit the call
  - **`enableAutomaticRecordingForOrganizer`** (boolean) *optional*
    If true, enables the automatic recording for the event when organizer joins the call
  - **`enableAutomaticTranscription`** (boolean) *optional*
    If true, enables the automatic transcription for the event whenever someone joins the call
  - **`disableTranscriptionForGuests`** (boolean) *optional*
    If true, the guests will not be able to receive transcription of the meeting
  - **`disableTranscriptionForOrganizer`** (boolean) *optional*
    If true, the organizer will not be able to receive transcription of the meeting
  - **`sendTranscriptionEmails`** (boolean) *optional*
    Send emails with the transcription of the Cal Video after the meeting ends.
    Default: `True`

- **`hidden`** (boolean) *optional*
- **`bookingRequiresAuthentication`** (boolean) *optional*
  Boolean to require authentication for booking this event type via api. If true, only authenticated users who are the event-type owner or org/team admin/owner can book this event type.
  Default: `False`
- **`disableCancelling`** (object) *optional*
  - **`disabled`** (boolean) *optional*
    If true, cancelling is always disabled for this event type.

- **`disableRescheduling`** (object) *optional*
  - **`disabled`** (boolean) *optional*
    If true, rescheduling is always disabled for this event type.
  - **`minutesBefore`** (number) *optional*
    Disable rescheduling when less than the specified number of minutes before the meeting. If set, `disabled` should be false or undefined.

- **`interfaceLanguage`** (string (enum)) *optional*
  Set preferred language for the booking interface. Use empty string for visitor's browser language (default).
- **`allowReschedulingPastBookings`** (boolean) *optional*
  Enabling this option allows for past events to be rescheduled.
  Default: `False`
- **`allowReschedulingCancelledBookings`** (boolean) *optional*
  When enabled, users will be able to create a new booking when trying to reschedule a cancelled booking.
  Default: `False`
- **`showOptimizedSlots`** (boolean) *optional*
  Arrange time slots to optimize availability.
  Default: `False`
- **`schedulingType`** (`"collective"` | `"roundRobin"` | `"managed"`) **required**
  The scheduling type for the team event - collective, roundRobin or managed.
  Allowed values: `collective`, `roundRobin`, `managed`
- **`hosts`** (object[]) *optional*
  Hosts contain specific team members you want to assign to this event type, but if you want to assign all team members, use `assignAllTeamMembers: true` instead and omit this field. For platform customers the hosts can include userIds only of managed users. Provide either hosts or assignAllTeamMembers but not both
  Items:
  - **`userId`** (number) **required**
    Which user is the host of this event
  - **`mandatory`** (boolean) *optional*
    Only relevant for round robin event types. If true then the user must attend round robin event always.
  - **`priority`** (`"lowest"` | `"low"` | `"medium"` | `"high"` | `"highest"`) *optional*
    Allowed values: `lowest`, `low`, `medium`, `high`, `highest`

- **`assignAllTeamMembers`** (boolean) *optional*
  If true, all current and future team members will be assigned to this event type. Provide either assignAllTeamMembers or hosts but not both
- **`locations`** (object | object | object | object[]) *optional*
  Locations where the event will take place. If not provided, cal video link will be used as the location. Note: Setting a location to a conferencing app does not install the app - the app must already be installed. Via API, only Google Meet (google-meet), Microsoft Teams (office365-video), and Zoom (zoom) can be installed. Cal Video (cal-video) is installed by default. All other conferencing apps must be connected via the Cal.com web app and are not available for Platform plan customers. You can only set an event type location to an app that has already been installed or connected.
- **`emailSettings`** (object) *optional*
  - **`disableEmailsToAttendees`** (boolean) *optional*
    Disables all email communication to attendees for this event type, including booking confirmations, reminders, and cancellations. This DOES NOT include emails sent by custom email workflows.
  - **`disableEmailsToHosts`** (boolean) *optional*
    Disables all email communication to hosts for this event type, including booking confirmations, reminders, and cancellations. This DOES NOT include emails sent by custom email workflows.

- **`rescheduleWithSameRoundRobinHost`** (boolean) *optional*
  Rescheduled events will be assigned to the same host as initially scheduled.

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
  "bookingFields": [],
  "disableGuests": true,
  "slotInterval": 0,
  "minimumBookingNotice": 0,
  "beforeEventBuffer": 0,
  "afterEventBuffer": 0,
  "scheduleId": 0,
  "onlyShowFirstAvailableSlot": true,
  "offsetStart": 0,
  "bookerLayouts": {
    "defaultLayout": "month",
    "enabledLayouts": [
      "month"
    ]
  },
  "requiresBookerEmailVerification": true,
  "hideCalendarNotes": true,
  "lockTimeZoneToggleOnBookingPage": true,
  "color": {
    "lightThemeHex": "#292929",
    "darkThemeHex": "#fafafa"
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
  "bookingRequiresAuthentication": false,
  "disableCancelling": {
    "disabled": true
  },
  "disableRescheduling": {
    "disabled": true,
    "minutesBefore": 60
  },
  "interfaceLanguage": "",
  "allowReschedulingPastBookings": false,
  "allowReschedulingCancelledBookings": false,
  "showOptimizedSlots": false,
  "schedulingType": "collective",
  "hosts": [
    {
      "userId": 0,
      "mandatory": true,
      "priority": "lowest"
    }
  ],
  "assignAllTeamMembers": true,
  "locations": [],
  "emailSettings": {
    "disableEmailsToAttendees": true,
    "disableEmailsToHosts": true
  },
  "rescheduleWithSameRoundRobinHost": true
}
```

## Example Request

```bash
curl -X POST "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/event-types" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '{"lengthInMinutes": 60, "lengthInMinutesOptions": [15, 30, 60], "title": "Learn the secrets of masterchief!", "slug": "learn-the-secrets-of-masterchief", "description": "Discover the culinary wonders of the Argentina by making the best flan ever!", "bookingFields": [], "disableGuests": true, "slotInterval": 0, "minimumBookingNotice": 0, "beforeEventBuffer": 0, "afterEventBuffer": 0, "scheduleId": 0, "onlyShowFirstAvailableSlot": true, "offsetStart": 0, "bookerLayouts": {"defaultLayout": "month", "enabledLayouts": ["month"]}, "requiresBookerEmailVerification": true, "hideCalendarNotes": true, "lockTimeZoneToggleOnBookingPage": true, "color": {"lightThemeHex": "#292929", "darkThemeHex": "#fafafa"}, "customName": "{Event type title} between {Organiser} and {Scheduler}", "destinationCalendar": {"integration": "string", "externalId": "string"}, "useDestinationCalendarEmail": true, "hideCalendarEventDetails": true, "successRedirectUrl": "https://masterchief.com/argentina/flan/video/9129412", "hideOrganizerEmail": true, "calVideoSettings": {"disableRecordingForOrganizer": true, "disableRecordingForGuests": true, "redirectUrlOnExit": "string", "enableAutomaticRecordingForOrganizer": true, "enableAutomaticTranscription": true, "disableTranscriptionForGuests": true, "disableTranscriptionForOrganizer": true, "sendTranscriptionEmails": true}, "hidden": true, "bookingRequiresAuthentication": false, "disableCancelling": {"disabled": true}, "disableRescheduling": {"disabled": true, "minutesBefore": 60}, "interfaceLanguage": "", "allowReschedulingPastBookings": false, "allowReschedulingCancelledBookings": false, "showOptimizedSlots": false, "schedulingType": "collective", "hosts": [{"userId": 0, "mandatory": true, "priority": "lowest"}], "assignAllTeamMembers": true, "locations": [], "emailSettings": {"disableEmailsToAttendees": true, "disableEmailsToHosts": true}, "rescheduleWithSameRoundRobinHost": true}'
```

## Responses

### 201

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object | object[]) **required**

**Example Response:**

```json
{
  "status": "success"
}
```
