<!-- Source: https://cal.com/docs/api-reference/v2/calendars/get-busy-times -->

# Get busy times - Cal.com Docs

Calendars
# Get busy times
Copy page

Get busy times from a calendar. Example request URL is `https://api.cal.com/v2/calendars/busy-times?timeZone=Europe%2FMadrid&dateFrom=2024-12-18&dateTo=2024-12-18&calendarsToLoad[0][credentialId]=135&calendarsToLoad[0][externalId]=skrauciz%40gmail.com`. Note: loggedInUsersTz is deprecated, use timeZone instead.Copy pageGET/v2/calendars/busy-timesTry itGet busy times

cURL
```
`curl --request GET \
  --url https://api.cal.com/v2/calendars/busy-times \
  --header 'Authorization: <authorization>'`
```
200
```
`{
  "status": "success",
  "data": [
    {
      "start": "2023-11-07T05:31:56Z",
      "end": "2023-11-07T05:31:56Z",
      "source": "<string>"
    }
  ]
}`
```

#### Headers
​Authorizationstringrequired

value must be `Bearer <token>` where `<token>` is api key prefixed with cal_, managed user access token, or OAuth access token
#### Query Parameters
​loggedInUsersTzstring

Deprecated: Use timeZone instead. The timezone of the user represented as a stringExample:

`"America/New_York"`​timeZonestring

The timezone for the busy times query represented as a stringExample:

`"America/New_York"`​dateFromstringrequired

The starting date for the busy times queryExample:

`"2023-10-01"`​dateTostringrequired

The ending date for the busy times queryExample:

`"2023-10-31"`​calendarsToLoadobject[]required

An array of Calendar objects representing the calendars to be loaded. Use bracket notation in the URL, e.g.: calendarsToLoad[0][credentialId]=135&calendarsToLoad[0][externalId]=[email protected]

Show child attributes
#### Response
200 - application/json​statusenum<string>requiredAvailable options: `success`, `error` Example:

`"success"`​dataobject[]required

Show child attributes
