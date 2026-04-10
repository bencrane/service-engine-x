<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-routing-forms-responses/create-routing-form-response-and-get-available-slots -->

# Create routing form response and get available slots

Required membership role: `team member`. PBAC permission: `routingForm.create`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`POST /v2/organizations/{orgId}/teams/{teamId}/routing-forms/{routingFormId}/responses`

**Tags:** Orgs / Teams / Routing forms / Responses

## Path Parameters

### `orgId` **required**

**Type:** `number`

### `teamId` **required**

**Type:** `number`

### `routingFormId` **required**

**Type:** `string`

## Query Parameters

### `start` **required**

**Type:** `string`

      Time starting from which available slots should be checked.

      Must be in UTC timezone as ISO 8601 datestring.

      You can pass date without hours which defaults to start of day or specify hours:
      2024-08-13 (will have hours 00:00:00 aka at very beginning of the date) or you can specify hours manually like 2024-08-13T09:00:00Z


### `end` **required**

**Type:** `string`

      Time until which available slots should be checked.

      Must be in UTC timezone as ISO 8601 datestring.

      You can pass date without hours which defaults to end of day or specify hours:
      2024-08-20 (will have hours 23:59:59 aka at the very end of the date) or you can specify hours manually like 2024-08-20T18:00:00Z

### `timeZone` *optional*

**Type:** `string`

Time zone in which the available slots should be returned. Defaults to UTC.

### `duration` *optional*

**Type:** `number`

If event type has multiple possible durations then you can specify the desired duration here. Also, if you are fetching slots for a dynamic event then you can specify the duration her which defaults to 30, meaning that returned slots will be each 30 minutes long.

### `format` *optional*

**Type:** ``"range"` | `"time"``

Format of slot times in response. Use 'range' to get start and end times.

**Allowed values:** `range`, `time`

### `bookingUidToReschedule` *optional*

**Type:** `string`

The unique identifier of the booking being rescheduled. When provided will ensure that the original booking time appears within the returned available slots when rescheduling.

### `queueResponse` *optional*

**Type:** `boolean`

Whether to queue the form response.

## Header Parameters

### `Authorization` **required**

**Type:** `string`

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_

## Example Request

```bash
curl -X POST "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/routing-forms/{routingFormId}/responses" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 201

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object) **required**
  - **`eventTypeId`** (number) *optional*
    The ID of the event type that was routed to.
  - **`routing`** (object) *optional*
    - **`queuedResponseId`** (string) *optional*
      The ID of the queued form response. Only present if the form response was queued.
    - **`responseId`** (number) *optional*
      The ID of the routing form response.
    - **`teamMemberIds`** (number[]) **required**
      Array of team member IDs that were routed to handle this booking.
    - **`teamMemberEmail`** (string) *optional*
      The email of the team member assigned to handle this booking.
    - **`skipContactOwner`** (boolean) *optional*
      Whether to skip contact owner assignment from CRM integration.
    - **`crmAppSlug`** (string) *optional*
      The CRM application slug for integration.
    - **`crmOwnerRecordType`** (string) *optional*
      The CRM owner record type for contact assignment.

  - **`routingCustomMessage`** (string) *optional*
    A custom message to be displayed to the user in case of routing to a custom page.
  - **`routingExternalRedirectUrl`** (string) *optional*
    The external redirect URL to be used in case of routing to a non cal.com event type URL.
  - **`slots`** (object | object) *optional*

**Example Response:**

```json
{
  "status": "success",
  "data": {
    "eventTypeId": 123,
    "routing": {
      "queuedResponseId": "123",
      "responseId": 123,
      "teamMemberIds": [
        101,
        102
      ],
      "teamMemberEmail": "john.doe@example.com",
      "skipContactOwner": true,
      "crmAppSlug": "salesforce",
      "crmOwnerRecordType": "Account"
    },
    "routingCustomMessage": "This is a custom message.",
    "routingExternalRedirectUrl": "https://example.com/"
  }
}
```
