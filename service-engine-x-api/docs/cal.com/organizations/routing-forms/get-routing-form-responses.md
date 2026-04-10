<!-- Source: https://cal.com/docs/api-reference/v2/orgs-routing-forms/get-routing-form-responses -->

# Get routing form responses - Cal.com Docs

Routing Forms
# Get routing form responses
Copy page

Required membership role: `org admin`. PBAC permission: `routingForm.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/routing-forms/{routingFormId}/responsesTry itGet routing form responses

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/routing-forms/{routingFormId}/responses \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "id": 123,
      "formId": "<string>",
      "formFillerId": "<string>",
      "routedToBookingUid": "<string>",
      "response": {
        "f00b26df-f54b-4985-8d98-17c5482c6a24": {
          "label": "participant",
          "value": "mamut"
        }
      },
      "createdAt": "2023-11-07T05:31:56Z"
    }
  ]
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_
#### Path Parameters
​orgIdnumberrequired​routingFormIdstringrequired
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

Filter by responses routed to a specific booking
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Show child attributes
