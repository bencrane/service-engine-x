<!-- Source: https://cal.com/docs/api-reference/v2/teams-verified-resources/verify-an-email-for-a-team -->

# Verify an email for a team

`POST /v2/teams/{teamId}/verified-resources/emails/verification-code/verify`

Use code to verify an email

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
  - Example: `example@acme.com`
- **`code`** **required** (`string`): verification code sent to the email to verify
  - Example: `1ABG2C`

### Example Request Body

```json
{
  "email": "example@acme.com",
  "code": "1ABG2C"
}
```

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object`)
  - **`id`** **required** (`number`): The unique identifier for the verified email.
    - Example: `789`
  - **`email`** **required** (`string (email)`): The verified email address.
    - Example: `user@example.com`
  - **`teamId`** **required** (`number`): The ID of the associated team, if applicable.
    - Example: `89`
  - **`userId`** (`number`): The ID of the associated user, if applicable.
    - Example: `45`

## Example Request

```bash
curl -X POST \
  "https://api.cal.com/v2/teams/<teamId>/verified-resources/emails/verification-code/verify" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '<request_body>'
```
