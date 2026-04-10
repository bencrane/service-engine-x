<!-- Source: https://cal.com/docs/api-reference/v2/orgs-users/get-all-users -->

# Get all users - Cal.com Docs

Users
# Get all users
Copy page

Required membership role: `org admin`. PBAC permission: `organization.listMembers`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/usersTry itGet all users

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/users`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "id": 1,
      "email": "[email protected]",
      "timeZone": "America/New_York",
      "weekStart": "Monday",
      "hideBranding": false,
      "createdDate": "2022-01-01T00:00:00Z",
      "profile": {
        "id": 1,
        "organizationId": 1,
        "userId": 1,
        "username": "john_doe"
      },
      "username": "john_doe",
      "name": "John Doe",
      "emailVerified": "2022-01-01T00:00:00Z",
      "bio": "I am a software developer",
      "avatarUrl": "https://example.com/avatar.jpg",
      "appTheme": "light",
      "theme": "default",
      "defaultScheduleId": 1,
      "locale": "en-US",
      "timeFormat": 12,
      "brandColor": "#ffffff",
      "darkBrandColor": "#000000",
      "allowDynamicBooking": true,
      "verified": true,
      "invitedTo": 1,
      "metadata": {
        "key": "value"
      }
    }
  ]
}`
```

#### Headers
​Authorizationstring

For non-platform customers - value must be `Bearer <token>` where `<token>` is api key prefixed with cal_​x-cal-secret-keystring

For platform customers - OAuth client secret key​x-cal-client-idstring

For platform customers - OAuth client ID
#### Path Parameters
​orgIdnumberrequired
#### Query Parameters
​takenumber

The number of items to returnRequired range: `1 <= x <= 1000`Example:

`10`​skipnumber

The number of items to skipRequired range: `x >= 0`Example:

`0`​emailsstring[]

The email address or an array of email addresses to filter byExample:
```
`["[email protected]", "[email protected]"]`
```
​assignedOptionIdsstring[]

Filter by assigned attribute option ids. ids must be separated by a comma.Example:

`"?assignedOptionIds=aaaaaaaa-bbbb-cccc-dddd-eeeeee1eee,aaaaaaaa-bbbb-cccc-dddd-eeeeee2eee"`​attributeQueryOperatorenum<string>default:AND

Query operator used to filter assigned options, AND by default.Available options: `OR`, `AND`, `NONE` Example:

`"NONE"`​teamIdsnumber[]

Filter by teamIds. Team ids must be separated by a comma.Example:

`"?teamIds=100,200"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Show child attributes
