<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-stripe/get-stripe-connect-url-for-a-team -->

# Get Stripe connect URL for a team

Required membership role: `team admin`. PBAC permission: `organization.manageBilling`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/stripe/connect`

**Tags:** Orgs / Teams / Stripe

## Path Parameters

### `teamId` **required**

**Type:** `string`

### `orgId` **required**

**Type:** `number`

## Query Parameters

### `returnTo` **required**

**Type:** `string`

### `onErrorReturnTo` **required**

**Type:** `string`

## Header Parameters

### `Authorization` **required**

**Type:** `string`

## Example Request

```bash
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/stripe/connect" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`
- **`data`** (object) **required**
  - **`authUrl`** (string) **required**

**Example Response:**

```json
{
  "status": "success",
  "data": {
    "authUrl": "string"
  }
}
```
