<!-- Source: https://cal.com/docs/api-reference/v2/verified-resources/get-list-of-verified-emails -->

# Get list of verified emails - Cal.com Docs

Verified Resources
# Get list of verified emails
Copy pageCopy pageGET/v2/verified-resources/emailsTry itGet list of verified emails

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/verified-resources/emails \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "id": 789,
      "email": "[email protected]",
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
