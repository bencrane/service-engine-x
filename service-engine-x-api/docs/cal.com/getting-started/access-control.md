<!-- Source: https://cal.com/docs/api-reference/v2/access-control -->

# Access Control - Cal.com Docs

Getting Started
# Access Control
Copy page

Roles and permissions for organization and team API endpointsCopy pageOrganization and team API endpoints use two layers of access control: **roles** and **PBAC (Permission-Based Access Control)**. Roles are the default mechanism — every endpoint requires a minimum membership role. PBAC is an opt-in feature that adds fine-grained permissions on top.

## ​Roles

Every organization and team endpoint requires the authenticated user to have a membership with a minimum role. There are three roles, from highest to lowest privilege:
LevelRoles (highest to lowest)Organization`owner` > `admin` > `member`Team`owner` > `admin` > `member`

### ​Role hierarchy

Higher roles can access endpoints that require a lower role. For example, if an endpoint requires `admin`, a user with the `owner` role can also access it.

### ​Organization roles grant team access

Organization-level roles carry over to team endpoints:

- **Org `admin` or `owner`** can access any team endpoint, regardless of team membership or the required team role. Organization level is above team level in terms of permissions.

- **Org `member`** must have a separate team membership. Their team role is then checked against the required team role.

For example, if a team endpoint requires `team admin`:

- A user with `org admin` or `org owner` membership can access it directly — no team membership needed.

- A user with `org member` membership needs a `team admin` (or `team owner`) membership in that specific team.

### ​Managing memberships

Use these endpoints to manage organization and team memberships:
**Organization memberships**
MethodEndpoint`POST`/v2/organizations//memberships`GET`/v2/organizations//memberships`GET`/v2/organizations//memberships/`PATCH`/v2/organizations//memberships/`DELETE`/v2/organizations//memberships/
**Team memberships**
MethodEndpoint`POST`/v2/organizations//teams//memberships`GET`/v2/organizations//teams//memberships`GET`/v2/organizations//teams//memberships/`PATCH`/v2/organizations//teams//memberships/`DELETE`/v2/organizations//teams//memberships/

## ​PBAC (Permission-Based Access Control)

PBAC is an opt-in feature enabled per organization. It lets you define custom roles with specific permissions for organization members. Instead of relying solely on admin/member roles, you can create granular roles like “Booking Manager” or “Team Lead” that have access to only the endpoints they need.

### ​How it works

Each endpoint has both a required membership role and a PBAC permission (e.g. `eventType.update`). Access is determined as follows:

- **PBAC is not enabled** — the system checks if the authenticated user has a membership with the required role (e.g. `org admin`). Users with a higher role (e.g. `org owner`) can also access endpoints that require a lower role.

- **PBAC is enabled and user has the required permission** — access is granted and the membership role check is skipped.

- **PBAC is enabled but user is missing the permission** — falls back to the membership role check in step 1.

### ​Setting up PBAC

- **Create a custom role** with specific permissions using the Roles API

- **Assign the role** to an organization or team membership

- When the member makes API requests, PBAC checks if their role includes the required permission for that endpoint

### ​Managing roles and permissions

Use the following endpoints to create roles, assign permissions, and manage access for your organization members.

#### ​Roles

MethodEndpoint`POST`/v2/organizations//roles`GET`/v2/organizations//roles`GET`/v2/organizations//roles/`PATCH`/v2/organizations//roles/`DELETE`/v2/organizations//roles/

#### ​Role permissions

MethodEndpoint`POST`/v2/organizations//roles//permissions`GET`/v2/organizations//roles//permissions`PUT`/v2/organizations//roles//permissions`DELETE`/v2/organizations//roles//permissions/`DELETE`/v2/organizations//roles//permissions

### ​Endpoint descriptions

Each organization and team endpoint description mentions the minimum membership role and PBAC permission required to access it.
