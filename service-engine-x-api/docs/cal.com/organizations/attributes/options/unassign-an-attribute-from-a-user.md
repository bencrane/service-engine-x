<!-- Source: https://cal.com/docs/api-reference/v2/orgs-attributes-options/unassign-an-attribute-from-a-user -->

# Unassign an attribute from a user - Cal.com Docs

Options
# Unassign an attribute from a user
Copy page

Required membership role: `org member`. PBAC permission: `organization.attributes.editUsers`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pageDELETE/v2/organizations/{orgId}/attributes/options/{userId}/{attributeOptionId}Try itUnassign an attribute from a user

cURL
```
`curl --request DELETE \
  --url https://api.cal.com/v2/organizations/{orgId}/attributes/options/{userId}/{attributeOptionId} \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": {
    "id": "<string>",
    "memberId": 123,
    "attributeOptionId": "<string>"
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_
#### Path Parameters
​orgIdnumberrequired​userIdnumberrequired​attributeOptionIdstringrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
