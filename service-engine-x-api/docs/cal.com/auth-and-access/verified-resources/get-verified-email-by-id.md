<!-- Source: https://cal.com/docs/api-reference/v2/verified-resources/get-verified-email-by-id -->

# Get verified email by id - Cal.com Docs

Verified Resources
# Get verified email by id
Copy pageCopy pageGET/v2/verified-resources/emails/{id}Try itGet verified email by id

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/verified-resources/emails/{id} \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": {
    "id": 789,
    "email": "[email protected]",
    "userId": 45
  }
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Path Parameters
​idnumberrequired
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobjectrequired

Show child attributes
