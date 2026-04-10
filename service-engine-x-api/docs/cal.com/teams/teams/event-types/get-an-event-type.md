<!-- Source: https://cal.com/docs/api-reference/v2/teams-event-types/get-an-event-type -->

# Get an event type

`GET /v2/teams/{teamId}/event-types/{eventTypeId}`

Get an event type

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

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object`)
  - **`id`** **required** (`number`)
    - Example: `1`
  - **`lengthInMinutes`** **required** (`number`)
    - Example: `60`
  - **`lengthInMinutesOptions`** (`number[]`): If you want that user can choose between different lengths of the event you can specify them here. Must include the provided `lengthInMinutes`.
  - **`title`** **required** (`string`)
    - Example: `Learn the secrets of masterchief!`
  - **`slug`** **required** (`string`)
    - Example: `learn-the-secrets-of-masterchief`
  - **`description`** **required** (`string`)
    - Example: `Discover the culinary wonders of Argentina by making the best flan ever!`
  - **`locations`** **required** (`object | object | object[]`)
  - **`bookingFields`** **required** (`object | object | object[]`)
  - **`disableGuests`** **required** (`boolean`)
  - **`slotInterval`** (`number`)
    - Example: `60`
  - **`minimumBookingNotice`** (`number`)
    - Example: `0`
  - **`beforeEventBuffer`** (`number`)
    - Example: `0`
  - **`afterEventBuffer`** (`number`)
    - Example: `0`
  - **`recurrence`** **required** (`object`)
  - **`metadata`** **required** (`object`)
  - **`price`** **required** (`number`)
  - **`currency`** **required** (`string`)
  - **`lockTimeZoneToggleOnBookingPage`** **required** (`boolean`)
  - **`seatsPerTimeSlot`** (`number`)
  - **`forwardParamsSuccessRedirect`** **required** (`boolean`)
  - **`successRedirectUrl`** **required** (`string`)
  - **`isInstantEvent`** **required** (`boolean`)
  - **`seatsShowAvailabilityCount`** (`boolean`)
  - **`scheduleId`** **required** (`number`)
  - **`bookingLimitsCount`** (`object | object`)
  - **`bookerActiveBookingsLimit`** (`object`)
    - **`maximumActiveBookings`** (`number`): The maximum number of active bookings a booker can have for this event type.
      - Example: `3`
    - **`offerReschedule`** (`boolean`): Whether to offer rescheduling the last active booking to the chosen time slot when limit is reached.
  - **`onlyShowFirstAvailableSlot`** (`boolean`)
  - **`bookingLimitsDuration`** (`object | object`)
  - **`bookingWindow`** (`object | object | object[]`): Limit how far in the future this event can be booked
  - **`bookerLayouts`** (`object`)
    - **`defaultLayout`** **required** (`enum`)
      - Enum values: `month`, `week`, `column`
    - **`enabledLayouts`** **required** (`enum[]`): Array of valid layouts - month, week or column
  - **`confirmationPolicy`** (`object | object`)
  - **`requiresBookerEmailVerification`** (`boolean`)
  - **`hideCalendarNotes`** (`boolean`)
  - **`color`** (`object`)
    - **`lightThemeHex`** **required** (`string`): Color used for event types in light theme
      - Example: `#292929`
    - **`darkThemeHex`** **required** (`string`): Color used for event types in dark theme
      - Example: `#fafafa`
  - **`seats`** (`object`)
    - **`seatsPerTimeSlot`** **required** (`number`): Number of seats available per time slot
      - Example: `4`
    - **`showAttendeeInfo`** **required** (`boolean`): Show attendee information to other guests
      - Example: `True`
    - **`showAvailabilityCount`** **required** (`boolean`): Display the count of available seats
      - Example: `True`
  - **`offsetStart`** (`number`)
  - **`customName`** (`string`)
  - **`destinationCalendar`** (`object`)
    - **`integration`** **required** (`string`): The integration type of the destination calendar. Refer to the /api/v2/calendars endpoint to retrieve the integration type of your connected calendars.
    - **`externalId`** **required** (`string`): The external ID of the destination calendar. Refer to the /api/v2/calendars endpoint to retrieve the external IDs of your connected calendars.
  - **`useDestinationCalendarEmail`** (`boolean`)
  - **`hideCalendarEventDetails`** (`boolean`)
  - **`hideOrganizerEmail`** (`boolean`): Boolean to Hide organizer's email address from the booking screen, email notifications, and calendar events
  - **`calVideoSettings`** (`object`): Cal video settings for the event type
  - **`hidden`** **required** (`boolean`)
  - **`bookingRequiresAuthentication`** **required** (`boolean`): Boolean to require authentication for booking this event type via api. If true, only authenticated users who are the event-type owner or org/team admin/owner can book this event type.
  - **`disableCancelling`** (`object`): Settings for disabling cancelling of this event type.
  - **`disableRescheduling`** (`object`): Settings for disabling rescheduling of this event type. Can be always disabled or disabled when less than X minutes before the meeting.
  - **`interfaceLanguage`** (`string`): Set preferred language for the booking interface.
  - **`allowReschedulingPastBookings`** (`boolean`): Enabling this option allows for past events to be rescheduled.
  - **`allowReschedulingCancelledBookings`** (`boolean`): When enabled, users will be able to create a new booking when trying to reschedule a cancelled booking.
  - **`showOptimizedSlots`** (`boolean`): Arrange time slots to optimize availability.
  - **`teamId`** **required** (`number`)
  - **`ownerId`** (`number`)
  - **`parentEventTypeId`** (`number`): For managed event types, parent event type is the event type that this event type is based on
  - **`hosts`** **required** (`object[]`)
    Array items:
    - **`userId`** **required** (`number`): Which user is the host of this event
    - **`mandatory`** (`boolean`): Only relevant for round robin event types. If true then the user must attend round robin event always.
    - **`priority`** (`enum`)
      - Enum values: `lowest`, `low`, `medium`, `high`, `highest`
    - **`name`** **required** (`string`)
      - Example: `John Doe`
    - **`username`** **required** (`string`)
      - Example: `john-doe`
    - **`avatarUrl`** (`string`)
      - Example: `https://cal.com/api/avatar/d95949bc-ccb1-400f-acf6-045c51a16856.png`
  - **`assignAllTeamMembers`** (`boolean`)
  - **`schedulingType`** **required** (`enum`)
    - Enum values: `roundRobin`, `collective`, `managed`
  - **`team`** **required** (`object`)
    - **`id`** **required** (`number`)
    - **`slug`** **required** (`string`)
    - **`bannerUrl`** **required** (`string`)
    - **`name`** **required** (`string`)
    - **`logoUrl`** **required** (`string`)
    - **`weekStart`** **required** (`string`)
    - **`brandColor`** **required** (`string`)
    - **`darkBrandColor`** **required** (`string`)
    - **`theme`** **required** (`string`)
  - **`emailSettings`** (`object`): Email settings for this event type. Only available for organization team event types.
  - **`rescheduleWithSameRoundRobinHost`** (`boolean`): Rescheduled events will be assigned to the same host as initially scheduled.

## Example Request

```bash
curl -X GET \
  "https://api.cal.com/v2/teams/<teamId>/event-types/<eventTypeId>" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
