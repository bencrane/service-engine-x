<!-- Source: https://cal.com/docs/api-reference/v2/teams-verified-resources/request-email-verification-code -->

# Request email verification code

`POST /v2/teams/{teamId}/verified-resources/emails/verification-code/request`

Sends a verification code to the Email

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

## Request Body

- **`email`** **required** (`string`): Email to verify.
  - Example: `acme@example.com`

### Example Request Body

```json
{
  "email": "acme@example.com"
}
```

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`

## Example Request

```bash
curl -X POST \
  "https://api.cal.com/v2/teams/<teamId>/verified-resources/emails/verification-code/request" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '<request_body>'
```
