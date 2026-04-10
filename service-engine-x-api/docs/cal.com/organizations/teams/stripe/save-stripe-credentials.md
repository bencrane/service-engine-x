<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-stripe/save-stripe-credentials -->

# Save Stripe credentials

Required membership role: `team admin`. PBAC permission: `organization.manageBilling`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-control

## Endpoint

`GET /v2/organizations/{orgId}/teams/{teamId}/stripe/save`

**Tags:** Orgs / Teams / Stripe

## Path Parameters

### `teamId` **required**

**Type:** `number`

### `orgId` **required**

**Type:** `number`

## Query Parameters

### `state` **required**

**Type:** `string`

### `code` **required**

**Type:** `string`

## Example Request

```bash
curl -X GET "https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/stripe/save" \
  -H "Authorization: Bearer <token>" \
  -H "cal-api-version: 2024-08-13"
```

## Responses

### 200

- **`url`** (string) **required**

**Example Response:**

```json
{
  "url": "string"
}
```
