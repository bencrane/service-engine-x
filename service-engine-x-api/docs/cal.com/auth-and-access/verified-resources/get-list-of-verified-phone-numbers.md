<!-- Source: https://cal.com/docs/api-reference/v2/verified-resources/get-list-of-verified-phone-numbers -->

# Get list of verified phone numbers - Cal.com Docs

Verified Resources
# Get list of verified phone numbers
Copy pageCopy pageGET/v2/verified-resources/phonesTry itGet list of verified phone numbers

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/verified-resources/phones \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "id": 789,
      "phoneNumber": "+37255556666",
      "userId": 45
    }
  ]
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Query Parameters
​takenumberdefault:250

Maximum number of items to returnRequired range: `1 <= x <= 250`Example:

`25`​skipnumberdefault:0

Number of items to skipRequired range: `x >= 0`Example:

`0`
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Show child attributes
