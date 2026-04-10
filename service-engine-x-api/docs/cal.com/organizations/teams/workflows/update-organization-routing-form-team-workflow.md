<!-- Source: https://cal.com/docs/api-reference/v2/orgs-teams-workflows/update-organization-routing-form-team-workflow -->

# Update organization routing form team workflow - Cal.com Docs

Workflows
# Update organization routing form team workflow
Copy page

Required membership role: `team admin`. PBAC permission: `workflow.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePATCH/v2/organizations/{orgId}/teams/{teamId}/workflows/{workflowId}/routing-formTry itUpdate organization routing form team workflow

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/organizations/{orgId}/teams/{teamId}/workflows/{workflowId}/routing-form \
  --header 'Content-Type: application/json' \
  --data '
{
  "name": "Rounting-form Test Workflow",
  "trigger": {
    "type": "formSubmitted"
  },
  "steps": [
    {
      "action": "email_address",
      "stepNumber": 1,
      "recipient": "attendee",
      "template": "reminder",
      "sender": "<string>",
      "verifiedEmailId": 31214,
      "includeCalendarEvent": true,
      "message": {
        "subject": "Reminder: Your Meeting {EVENT_NAME} - {EVENT_DATE_ddd, MMM D, YYYY h:mma} with Cal.com",
        "html": "<p>This is a reminder from {ORGANIZER} of {EVENT_NAME} to {ATTENDEE} starting here  {LOCATION} {MEETING_URL} at {START_TIME_h:mma} {TIMEZONE}.</p>"
      },
      "autoTranslateEnabled": false,
      "sourceLocale": "en",
      "id": 67244
    }
  ]
}
'`
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
​teamIdnumberrequired​workflowIdnumberrequired​orgIdnumberrequired
#### Body
application/json​namestring

Name of the workflowExample:

`"Rounting-form Test Workflow"`​triggerobject

Trigger configuration for the routing-form workflow, allowed triggers are formSubmitted,formSubmittedNoEvent
- Option 1
- Option 2

Show child attributes​stepsobject[]

Steps to execute as part of the routing-form workflow, allowed steps are email_attendee,email_address,sms_attendee,sms_number
- Option 1
- Option 2
- Option 3
- Option 4

Show child attributes​activationobject

Show child attributes
#### Response
200 - application/json​statusenum<string>required

Indicates the status of the responseAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

workflow

Show child attributes
