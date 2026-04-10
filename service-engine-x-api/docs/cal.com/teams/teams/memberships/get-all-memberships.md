<!-- Source: https://cal.com/docs/api-reference/v2/teams-memberships/get-all-memberships -->

# Get all memberships

`GET /v2/teams/{teamId}/memberships`

Retrieve team memberships with optional filtering by email addresses. Supports pagination.

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

## Query Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `take` | `number` | No | Maximum number of items to return Default: `250` |
| `skip` | `number` | No | Number of items to skip Default: `0` |
| `emails` | `string[]` | No | Filter team memberships by email addresses. If you want to filter by multiple emails, separate them with a comma (max 20 emails for performance). |

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
curl -X GET \
  "https://api.cal.com/v2/teams/<teamId>/memberships" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
