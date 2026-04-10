<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-workflows/create-organization-team-workflow-for-event-types -->

# Create organization team workflow for event-types

Required membership role: `team admin`. PBAC permission: `workflow.create`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`POST /v2/organizations/{orgId}/teams/{teamId}/workflows`

**Tags:** Orgs / Teams / Workflows

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

- **`name`** (string) **required**
  Name of the workflow
- **`activation`** (object) **required**
  - **`isActiveOnAllEventTypes`** (boolean) **required**
    Whether the workflow is active for all the event-types
    Default: `False`
  - **`activeOnEventTypeIds`** (number[]) *optional*
    List of event-types IDs the workflow applies to, required if isActiveOnAllEventTypes is false
    Default: `[]`

- **`trigger`** (object | object | object | object) **required**
  Trigger configuration for the event-type workflow, allowed triggers are beforeEvent,eventCancelled,newEvent,afterEvent,rescheduleEvent,afterHostsCalVideoNoShow,afterGuestsCalVideoNoShow,bookingRejected,bookingRequested,bookingPaymentInitiated,bookingPaid,bookingNoShowUpdated
- **`steps`** (object | object | object | object[]) **required**
  Steps to execute as part of the event-type workflow, allowed steps are email_host,email_attendee,email_address,sms_attendee,sms_number,whatsapp_attendee,whatsapp_number,cal_ai_phone_call

### Example Request Body

```json
{
  "name": "Platform Test Workflow",
  "activation": {
    "isActiveOnAllEventTypes": false,
    "activeOnEventTypeIds": [
      698191
    ]
  },
  "steps": []
}
```

## Example Request

```bash
curl -X POST "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/workflows" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '{"name": "Platform Test Workflow", "activation": {"isActiveOnAllEventTypes": false, "activeOnEventTypeIds": [698191]}, "steps": []}'
```

## Responses

### 201

- **`status`** (`"success"` | `"error"`) **required**
  Indicates the status of the response
  Allowed values: `success`, `error`
- **`data`** (object[]) **required**
  workflow
  Items:
  - **`id`** (number) **required**
    Unique identifier of the workflow
  - **`name`** (string) **required**
    Name of the workflow
  - **`userId`** (number) *optional*
    ID of the user who owns the workflow (if not team-owned)
  - **`teamId`** (number) *optional*
    ID of the team owning the workflow
  - **`createdAt`** (string) *optional*
    Timestamp of creation
  - **`updatedAt`** (string) *optional*
    Timestamp of last update
  - **`type`** (`"event-type"`) **required**
    type of the workflow
    Default: `event-type`
    Allowed values: `event-type`
  - **`activation`** (object) **required**
    - **`isActiveOnAllEventTypes`** (boolean) *optional*
      Whether the workflow is active for all event types associated with the team/user
      Default: `False`
    - **`activeOnEventTypeIds`** (number[]) *optional*
      List of Event Type IDs the workflow is specifically active on (if not active on all)

  - **`trigger`** (object) **required**
    - **`type`** (string (enum)) **required**
      Trigger type for the workflow
    - **`offset`** (object) *optional*

  - **`steps`** (object[]) **required**
    Steps comprising the workflow
    Items:
    - **`id`** (number) **required**
      Unique identifier of the step
    - **`stepNumber`** (number) **required**
      Step number in the workflow sequence
    - **`recipient`** (`"const"` | `"attendee"` | `"email"` | `"phone_number"`) **required**
      Intended recipient type
      Allowed values: `const`, `attendee`, `email`, `phone_number`
    - **`email`** (string) *optional*
      Verified email address if action is EMAIL_ADDRESS
    - **`phone`** (string) *optional*
      Verified Phone if action is SMS_NUMBER or WHATSAPP_NUMBER
    - **`phoneRequired`** (boolean) *optional*
      whether or not the attendees are required to provide their phone numbers when booking
      Default: `False`
    - **`template`** (`"reminder"` | `"custom"` | `"rescheduled"` | `"completed"` | `"rating"` | `"cancelled"`) **required**
      Template type used
      Allowed values: `reminder`, `custom`, `rescheduled`, `completed`, `rating`, `cancelled`
    - **`includeCalendarEvent`** (boolean) *optional*
      Whether a calendar event (.ics) was included (for email actions)
      Default: `False`
    - **`sender`** (string) **required**
      Displayed sender name used for this step
    - **`message`** (object) **required**
    - **`autoTranslateEnabled`** (boolean) *optional*
      Whether auto-translation of the workflow step content for attendees is enabled. Only available for organizations.
      Default: `False`
    - **`sourceLocale`** (string (enum)) *optional*
      The source locale of the workflow step content used for auto-translation (e.g. 'en').
    - **`action`** (string (enum)) **required**
      Action to perform
      Allowed values: `email_host`, `email_attendee`, `email_address`, `sms_attendee`, `sms_number`, `whatsapp_attendee`, `whatsapp_number`, `cal_ai_phone_call`

**Example Response:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 101,
      "name": "Platform Test Workflow",
      "userId": 2313,
      "teamId": 4214321,
      "createdAt": "2024-05-12T10:00:00.000Z",
      "updatedAt": "2024-05-12T11:30:00.000Z",
      "type": "event-type",
      "steps": []
    }
  ]
}
```
