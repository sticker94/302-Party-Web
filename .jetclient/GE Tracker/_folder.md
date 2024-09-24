[GE Tracker](https://www.ge-tracker.com) is an Old School RuneScape Flipping and Money Making tool.

~~Both a Premium account and an~~ [~~API key~~](https://www.ge-tracker.com/my-account/api-keys) ~~are required to access the API externally. We have a collection named~~ ~~`No Authentication`~~ ~~which lists public endpoints that do not require authentication to access.~~

**Update:** Due to abuse, user level API access is disabled until further notice. Please see [https://www.ge-tracker.com/blog/api-keys](https://www.ge-tracker.com/blog/api-keys)

### Authorisation

When submitting a request to the GE Tracker API, the API Key must be sent via Header or Query Parameter. Invalid or expired tokens will return a 401 response.

##### Header

> Authorization: Bearer {API_KEY}

##### Query Parameter

> ?token={API_KEY}

### Versioning

The current API version is `v2.1`, and should be specified by the `Accept` header:

> Accept: application/x.getracker.v2.1+json

```toml
name = 'GE Tracker'
sortWeight = 1000000
id = '9eff6a61-f1bf-4c1f-a4ff-01562e12ed75'

[auth.bearer]
token = '{{apiKey}}'
```
