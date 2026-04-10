<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-workflows/create-organization-team-workflow-for-routing-forms -->

# Create organization team workflow for routing-forms

Required membership role: `team admin`. PBAC permission: `workflow.create`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`POST /v2/organizations/{orgId}/teams/{teamId}/workflows/routing-form`

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
  - **`isActiveOnAllRoutingForms`** (boolean) **required**
    Whether the workflow is active for all the routing forms
  - **`activeOnRoutingFormIds`** (number[]) *optional*
    List of routing form IDs the workflow applies to

- **`trigger`** (object | object) **required**
  Trigger configuration for the routing-form workflow, allowed triggers are formSubmitted,formSubmittedNoEvent
- **`steps`** (object | object | object | object[]) **required**
  Steps to execute as part of the routing-form workflow, allowed steps are email_attendee,email_address,sms_attendee,sms_number

### Example Request Body

```json
{
  "name": "Platform Test Workflow",
  "activation": {
    "isActiveOnAllRoutingForms": false,
    "activeOnRoutingFormIds": [
      "abd1-123edf-a213d-123dfwf"
    ]
  },
  "steps": []
}
```

## Example Request

```bash
curl -X POST "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/workflows/routing-form" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '{"name": "Platform Test Workflow", "activation": {"isActiveOnAllRoutingForms": false, "activeOnRoutingFormIds": ["abd1-123edf-a213d-123dfwf"]}, "steps": []}'
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
  - **`type`** (`"routing-form"`) **required**
    type of the workflow
    Default: `routing-form`
    Allowed values: `routing-form`
  - **`activation`** (object) **required**
    - **`isActiveOnAllRoutingForms`** (boolean) *optional*
      Whether the workflow is active for all routing forms associated with the team/user
      Default: `False`
    - **`activeOnRoutingFormIds`** (string[]) *optional*
      List of Event Type IDs the workflow is specifically active on (if not active on all)

  - **`trigger`** (object) **required**
    - **`type`** (`"formSubmitted"` | `"formSubmittedNoEvent"`) **required**
      Trigger type for the workflow
      Allowed values: `formSubmitted`, `formSubmittedNoEvent`
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
    - **`action`** (`"email_attendee"` | `"email_address"` | `"sms_attendee"` | `"sms_number"`) **required**
      Action to perform
      Allowed values: `email_attendee`, `email_address`, `sms_attendee`, `sms_number`

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
      "type": "routing-form",
      "steps": []
    }
  ]
}
```
