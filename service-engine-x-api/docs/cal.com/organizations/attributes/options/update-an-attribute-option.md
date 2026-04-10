<!-- Source: https://cal.com/docs/api-reference/v2/orgs-attributes-options/update-an-attribute-option -->

# Update an attribute option - Cal.com Docs

Options
# Update an attribute option
Copy page

Required membership role: `org admin`. PBAC permission: `organization.attributes.update`. Learn more about API access control at https://cal.com/docs/api-reference/v2/access-controlCopy pagePATCH/v2/organizations/{orgId}/attributes/{attributeId}/options/{optionId}Try itUpdate an attribute option

cURL
```
`curl --request PATCH \
  --url https://api.cal.com/v2/organizations/{orgId}/attributes/{attributeId}/options/{optionId} \
  --header 'Authorization: <authorization>' \
  --header 'Content-Type: application/json' \
  --data '
{
  "value": "<string>",
  "slug": "<string>"
}
'`
```
200
```
`{
  "status": "success",
  "data": {
    "id": "attr_option_id",
    "attributeId": "attr_id",
    "value": "option_value",
    "slug": "option-slug"
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_
#### Path Parameters
​orgIdnumberrequired​attributeIdstringrequired​optionIdstringrequired
#### Body
application/json​valuestring​slugstring
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
