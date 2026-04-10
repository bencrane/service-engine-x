<!-- Source: https://cal.com/docs/api-reference/v2/teams-memberships/update-membership -->

# Update membership

`PATCH /v2/teams/{teamId}/memberships/{membershipId}`

Update membership

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
| `membershipId` | `number` | Yes |  |

## Request Body

- **`accepted`** (`boolean`)
- **`role`** (`enum`)
  - Enum values: `MEMBER`, `OWNER`, `ADMIN`
- **`disableImpersonation`** (`boolean`)

### Example Request Body

```json
{
  "accepted": true,
  "role": "MEMBER",
  "disableImpersonation": true
}
```

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object`)
  - **`id`** **required** (`number`)
  - **`userId`** **required** (`number`)
  - **`teamId`** **required** (`number`)
  - **`accepted`** **required** (`boolean`)
  - **`role`** **required** (`enum`)
    - Enum values: `MEMBER`, `OWNER`, `ADMIN`
  - **`disableImpersonation`** (`boolean`)
  - **`user`** **required** (`object`)
    - **`avatarUrl`** (`string`)
    - **`username`** (`string`)
    - **`name`** (`string`)
    - **`email`** **required** (`string`)
    - **`bio`** (`string`)
    - **`metadata`** (`object`)

## Example Request

```bash
curl -X PATCH \
  "https://api.cal.com/v2/teams/<teamId>/memberships/<membershipId>" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13" \
  -H "Content-Type: application/json" \
  -d '<request_body>'
```
