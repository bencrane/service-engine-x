<!-- Source: https://cal.com/docs/api-reference/v2/orgs-routing-forms/get-organization-routing-forms -->

# Get organization routing forms - Cal.com Docs

Routing Forms
# Get organization routing forms
Copy page

Required membership role: `org admin`. PBAC permission: `routingForm.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/routing-formsTry itGet organization routing forms

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/routing-forms \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "name": "My Form",
      "description": "This is the description.",
      "position": 0,
      "createdAt": "2024-03-28T10:00:00.000Z",
      "updatedAt": "2024-03-28T10:00:00.000Z",
      "userId": 2313,
      "teamId": 4214321,
      "disabled": false,
      "id": "<string>",
      "routes": {},
      "fields": {},
      "settings": {}
    }
  ]
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_
#### Path Parameters
​orgIdnumberrequired
#### Query Parameters
​skipnumber

Number of responses to skip​takenumber

Number of responses to take​sortCreatedAtenum<string>

Sort by creation timeAvailable options: `asc`, `desc` ​sortUpdatedAtenum<string>

Sort by update timeAvailable options: `asc`, `desc` ​afterCreatedAtstring<date-time>

Filter by responses created after this date​beforeCreatedAtstring<date-time>

Filter by responses created before this date​afterUpdatedAtstring<date-time>

Filter by responses created after this date​beforeUpdatedAtstring<date-time>

Filter by responses updated before this date​routedToBookingUidstring

Filter by responses routed to a specific booking​teamIdsnumber[]

Filter by teamIds. Team ids must be separated by a comma.Example:

`"?teamIds=100,200"`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Show child attributes
