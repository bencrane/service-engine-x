<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-event-types/get-team-event-types -->

# Get team event types

Use the optional `sortCreatedAt` query parameter to order results by creation date (by ID). Accepts "asc" (oldest first) or "desc" (newest first). When not provided, no explicit ordering is applied.

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/event-types`

**Tags:** Orgs / Teams / Event Types

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `orgId` **required**

**Type:** `number`

## Query Parameters

### `eventSlug` *optional*

**Type:** `string`

Slug of team event type to return.

### `hostsLimit` *optional*

**Type:** `number`

Specifies the maximum number of hosts to include in the response. This limit helps optimize performance. If not provided, all Hosts will be fetched.

### `sortCreatedAt` *optional*

**Type:** ``"asc"` | `"desc"``

Sort event types by creation date. When not provided, no explicit ordering is applied.

**Allowed values:** `asc`, `desc`

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

## Example Request

```bash
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/event-types" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object[]) **required**
  Items:
  - **`id`** (number) **required**
  - **`lengthInMinutes`** (number) **required**
  - **`lengthInMinutesOptions`** (number[]) *optional*
    If you want that user can choose between different lengths of the event you can specify them here. Must include the provided `lengthInMinutes`.
  - **`title`** (string) **required**
  - **`slug`** (string) **required**
  - **`description`** (string) **required**
  - **`locations`** (object | object | object | object[]) **required**
  - **`bookingFields`** (object | object | object | object[]) **required**
  - **`disableGuests`** (boolean) **required**
  - **`slotInterval`** (number) *optional*
  - **`minimumBookingNotice`** (number) *optional*
  - **`beforeEventBuffer`** (number) *optional*
  - **`afterEventBuffer`** (number) *optional*
  - **`recurrence`** (object) **required**
    - **`interval`** (number) **required**
      Repeats every {count} week | month | year
    - **`occurrences`** (number) **required**
      Repeats for a maximum of {count} events
    - **`frequency`** (`"yearly"` | `"monthly"` | `"weekly"`) **required**
      Allowed values: `yearly`, `monthly`, `weekly`

  - **`metadata`** (object) **required**
  - **`price`** (number) **required**
  - **`currency`** (string) **required**
  - **`lockTimeZoneToggleOnBookingPage`** (boolean) **required**
  - **`seatsPerTimeSlot`** (number) *optional*
  - **`forwardParamsSuccessRedirect`** (boolean) **required**
  - **`successRedirectUrl`** (string) **required**
  - **`isInstantEvent`** (boolean) **required**
  - **`seatsShowAvailabilityCount`** (boolean) *optional*
  - **`scheduleId`** (number) **required**
  - **`bookingLimitsCount`** (object | object) *optional*
  - **`bookerActiveBookingsLimit`** (object) *optional*
    - **`maximumActiveBookings`** (number) *optional*
      The maximum number of active bookings a booker can have for this event type.
    - **`offerReschedule`** (boolean) *optional*
      Whether to offer rescheduling the last active booking to the chosen time slot when limit is reached.

  - **`onlyShowFirstAvailableSlot`** (boolean) *optional*
  - **`bookingLimitsDuration`** (object | object) *optional*
  - **`bookingWindow`** (object | object | object[]) *optional*
    Limit how far in the future this event can be booked
  - **`bookerLayouts`** (object) *optional*
    - **`defaultLayout`** (`"month"` | `"week"` | `"column"`) **required**
      Allowed values: `month`, `week`, `column`
    - **`enabledLayouts`** (`"month"` | `"week"` | `"column"`[]) **required**
      Array of valid layouts - month, week or column

  - **`confirmationPolicy`** (object | object) *optional*
  - **`requiresBookerEmailVerification`** (boolean) *optional*
  - **`hideCalendarNotes`** (boolean) *optional*
  - **`color`** (object) *optional*
    - **`lightThemeHex`** (string) **required**
      Color used for event types in light theme
    - **`darkThemeHex`** (string) **required**
      Color used for event types in dark theme

  - **`seats`** (object) *optional*
    - **`seatsPerTimeSlot`** (number) **required**
      Number of seats available per time slot
    - **`showAttendeeInfo`** (boolean) **required**
      Show attendee information to other guests
    - **`showAvailabilityCount`** (boolean) **required**
      Display the count of available seats

  - **`offsetStart`** (number) *optional*
  - **`customName`** (string) *optional*
  - **`destinationCalendar`** (object) *optional*
    - **`integration`** (string) **required**
      The integration type of the destination calendar. Refer to the /api/v2/calendars endpoint to retrieve the integration type of your connected calendars.
    - **`externalId`** (string) **required**
      The external ID of the destination calendar. Refer to the /api/v2/calendars endpoint to retrieve the external IDs of your connected calendars.

  - **`useDestinationCalendarEmail`** (boolean) *optional*
  - **`hideCalendarEventDetails`** (boolean) *optional*
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

  - **`hidden`** (boolean) **required**
  - **`bookingRequiresAuthentication`** (boolean) **required**
    Boolean to require authentication for booking this event type via api. If true, only authenticated users who are the event-type owner or org/team admin/owner can book this event type.
  - **`disableCancelling`** (object) *optional*
    - **`disabled`** (boolean) *optional*
      If true, cancelling is always disabled for this event type.

  - **`disableRescheduling`** (object) *optional*
    - **`disabled`** (boolean) *optional*
      If true, rescheduling is always disabled for this event type.
    - **`minutesBefore`** (number) *optional*
      Rescheduling is disabled when less than the specified number of minutes before the meeting.

  - **`interfaceLanguage`** (string) *optional*
    Set preferred language for the booking interface.
  - **`allowReschedulingPastBookings`** (boolean) *optional*
    Enabling this option allows for past events to be rescheduled.
  - **`allowReschedulingCancelledBookings`** (boolean) *optional*
    When enabled, users will be able to create a new booking when trying to reschedule a cancelled booking.
  - **`showOptimizedSlots`** (boolean) *optional*
    Arrange time slots to optimize availability.
  - **`teamId`** (number) **required**
  - **`ownerId`** (number) *optional*
  - **`parentEventTypeId`** (number) *optional*
    For managed event types, parent event type is the event type that this event type is based on
  - **`hosts`** (object[]) **required**
    Items:
    - **`userId`** (number) **required**
      Which user is the host of this event
    - **`mandatory`** (boolean) *optional*
      Only relevant for round robin event types. If true then the user must attend round robin event always.
    - **`priority`** (`"lowest"` | `"low"` | `"medium"` | `"high"` | `"highest"`) *optional*
      Allowed values: `lowest`, `low`, `medium`, `high`, `highest`
    - **`name`** (string) **required**
    - **`username`** (string) **required**
    - **`avatarUrl`** (string) *optional*

  - **`assignAllTeamMembers`** (boolean) *optional*
  - **`schedulingType`** (`"roundRobin"` | `"collective"` | `"managed"`) **required**
    Allowed values: `roundRobin`, `collective`, `managed`
  - **`team`** (object) **required**
    - **`id`** (number) **required**
    - **`slug`** (string) **required**
    - **`bannerUrl`** (string) **required**
    - **`name`** (string) **required**
    - **`logoUrl`** (string) **required**
    - **`weekStart`** (string) **required**
    - **`brandColor`** (string) **required**
    - **`darkBrandColor`** (string) **required**
    - **`theme`** (string) **required**

  - **`emailSettings`** (object) *optional*
    - **`disableEmailsToAttendees`** (boolean) *optional*
      Disables all email communication to attendees for this event type, including booking confirmations, reminders, and cancellations. This DOES NOT include emails sent by custom email workflows.
    - **`disableEmailsToHosts`** (boolean) *optional*
      Disables all email communication to hosts for this event type, including booking confirmations, reminders, and cancellations. This DOES NOT include emails sent by custom email workflows.

  - **`rescheduleWithSameRoundRobinHost`** (boolean) *optional*
    Rescheduled events will be assigned to the same host as initially scheduled.

**Example Response:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "lengthInMinutes": 60,
      "lengthInMinutesOptions": [
        15,
        30,
        60
      ],
      "title": "Learn the secrets of masterchief!",
      "slug": "learn-the-secrets-of-masterchief",
      "description": "Discover the culinary wonders of Argentina by making the best flan ever!",
      "locations": [],
      "bookingFields": [],
      "disableGuests": true,
      "slotInterval": 60,
      "minimumBookingNotice": 0,
      "beforeEventBuffer": 0,
      "afterEventBuffer": 0,
      "price": 0,
      "currency": "string",
      "lockTimeZoneToggleOnBookingPage": true,
      "seatsPerTimeSlot": 0,
      "forwardParamsSuccessRedirect": true,
      "successRedirectUrl": "string",
      "isInstantEvent": true,
      "seatsShowAvailabilityCount": true,
      "scheduleId": 0,
      "onlyShowFirstAvailableSlot": true,
      "bookingWindow": [],
      "requiresBookerEmailVerification": true,
      "hideCalendarNotes": true,
      "offsetStart": 0,
      "customName": "string",
      "useDestinationCalendarEmail": true,
      "hideCalendarEventDetails": true,
      "hideOrganizerEmail": true,
      "hidden": true,
      "bookingRequiresAuthentication": true,
      "interfaceLanguage": "string",
      "allowReschedulingPastBookings": true,
      "allowReschedulingCancelledBookings": true,
      "showOptimizedSlots": true,
      "teamId": 0,
      "ownerId": 0,
      "parentEventTypeId": 0,
      "hosts": [],
      "assignAllTeamMembers": true,
      "schedulingType": "roundRobin",
      "rescheduleWithSameRoundRobinHost": true
    }
  ]
}
```
