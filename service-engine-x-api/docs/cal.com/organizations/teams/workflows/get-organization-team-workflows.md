<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-workflows/get-organization-team-workflows -->

# Get organization team workflows - Cal.com Docs

Workflows
# Get organization team workflows
Copy page

Required membership role: `team admin`. PBAC permission: `workflow.read`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageGET/v2/organizations/{orgId}/teams/{teamId}/workflows/routing-formTry itGet organization team workflows

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/workflows/routing-form`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "id": 101,
      "name": "Platform Test Workflow",
      "type": "routing-form",
      "activation": {
        "isActiveOnAllRoutingForms": false,
        "activeOnRoutingFormIds": [
          "5cacdec7-1234-6e1b-78d9-7bcda8a1b332"
        ]
      },
      "trigger": {
        "type": "formSubmitted",
        "offset": {
          "value": 24,
          "unit": "hour"
        }
      },
      "steps": [
        {
          "id": 67244,
          "stepNumber": 1,
          "recipient": "const",
          "template": "reminder",
          "sender": "Cal.com Notifications",
          "message": {
            "subject": "Reminder: Your Meeting {EVENT_NAME} - {EVENT_DATE_ddd, MMM D, YYYY h:mma} with Cal.com",
            "html": "<p>Reminder for {EVENT_NAME}.</p>",
            "text": "Reminder for {EVENT_NAME}."
          },
          "action": "email_host",
          "email": "[email protected]",
          "phone": "<string>",
          "phoneRequired": true,
          "includeCalendarEvent": true,
          "autoTranslateEnabled": false,
          "sourceLocale": "en"
        }
      ],
      "userId": 2313,
      "teamId": 4214321,
      "createdAt": "2024-05-12T10:00:00.000Z",
      "updatedAt": "2024-05-12T11:30:00.000Z"
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
​orgIdnumberrequired​teamIdnumberrequired
#### Query Parameters
​takenumberdefault:250

Maximum number of items to returnRequired range: `1 <= x <= 250`Example:

`25`​skipnumberdefault:0

Number of items to skipRequired range: `x >= 0`Example:

`0`
#### Response
200 - application/json​statusenum<string>required

Indicates the status of the responseAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

List of workflows

Show child attributes
