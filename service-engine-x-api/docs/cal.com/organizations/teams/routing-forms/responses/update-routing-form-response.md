<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-routing-forms-responses/update-routing-form-response -->

# Update routing form response

Required membership role: `team admin`. PBAC permission: `routingForm.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`PATCH /v2/organizations/{orgId}/teams/{teamId}/routing-forms/{routingFormId}/responses/{responseId}`

**Tags:** Orgs / Teams / Routing forms / Responses

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `routingFormId` **required**

**Type:** `string`

### `responseId` **required**

**Type:** `number`

### `orgId` **required**

**Type:** `number`

## Header Parameters

### `Authorization` **required**

**Type:** `string`

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_

## Request Body

**Required:** Yes

**Content-Type:** `application/json`

- **`response`** (object) *optional*
  The updated response data

## Example Request

```bash
curl -X PATCH "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/routing-forms/{routingFormId}/responses/{responseId}" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object) **required**
  - **`id`** (number) **required**
  - **`formId`** (string) **required**
  - **`formFillerId`** (string) **required**
  - **`routedToBookingUid`** (string) **required**
  - **`response`** (object) **required**
  - **`createdAt`** (string) **required**

**Example Response:**

```json
{
  "status": "success",
  "data": {
    "id": 0,
    "formId": "string",
    "formFillerId": "string",
    "routedToBookingUid": "string",
    "response": {
      "f00b26df-f54b-4985-8d98-17c5482c6a24": {
        "label": "participant",
        "value": "mamut"
      }
    },
    "createdAt": "string"
  }
}
```
