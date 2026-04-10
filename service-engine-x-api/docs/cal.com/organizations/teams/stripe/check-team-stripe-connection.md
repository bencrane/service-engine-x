<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-stripe/check-team-stripe-connection -->

# Check team Stripe connection

Required membership role: `team admin`. PBAC permission: `organization.manageBilling`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/stripe/check`

**Tags:** Orgs / Teams / Stripe

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `orgId` **required**

**Type:** `number`

## Example Request

```bash
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/stripe/check" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`status`** (`"success"` | `"error"`) **required**
  Allowed values: `success`, `error`

**Example Response:**

```json
{
  "status": "success"
}
```
