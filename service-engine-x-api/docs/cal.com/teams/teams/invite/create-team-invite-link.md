<!-- Source: https://cal.com/docs/api-reference/v2/teams-invite/create-team-invite-link -->

# Create team invite link

`POST /v2/teams/{teamId}/invite`

Create team invite link

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

## Responses

### 200 - 

- **`status`** **required** (`enum`)
  - Enum values: `success`, `error`
  - Example: `success`
- **`data`** **required** (`object`)
  - **`token`** **required** (`string`): Unique invitation token for this team. Share this token with prospective members to allow them to join the team/organization.
    - Example: `f6a5c8b1d2e34c7f90a1b2c3d4e5f6a5b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2`
  - **`inviteLink`** **required** (`string`): Complete invitation URL that can be shared with prospective members. Opens the signup page with the token and redirects to getting started after signup.
    - Example: `http://app.cal.com/signup?token=f6a5c8b1d2e34c7f90a1b2c3d4e5f6a5b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2&callbackUrl=/getting-started`

## Example Request

```bash
curl -X POST \
  "https://api.cal.com/v2/teams/<teamId>/invite" \
  -H "Authorization: Bearer <your_api_key>" \
  -H "cal-api-version: 2024-08-13"
```
