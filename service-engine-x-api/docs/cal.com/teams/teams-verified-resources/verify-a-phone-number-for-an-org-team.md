<!-- Source: https://cal.com/docs/api-reference/v2/teams-verified-resources/verify-a-phone-number-for-an-org-team -->

# Verify a phone number for an org team

`POST /v2/teams/{teamId}/verified-resources/phones/verification-code/verify`

Use code to verify a phone number

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

- **`phone`** **required** (`string`): phone number to verify.
  - Example: `+37255556666`
- **`code`** **required** (`string`): verification code sent to the phone number to verify
  - Example: `1ABG2C`

### Example Request Body

```json
{
  "phone": "+37255556666",
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
  - **`phoneNumber`** **required** (`string (phone)`): The verified phone number.
    - Example: `+37255556666`
  - **`userId`** (`number`): The ID of the associated user, if applicable.
    - Example: `45`
  - **`teamId`** **required** (`number`): The ID of the associated team, if applicable.
    - Example: `89`

## Example Request

```bash
curl -X POST \
  "https://api.cal.com/v2/teams/<teamId>/verified-resources/phones/verification-code/verify" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '<request_body>'
```
