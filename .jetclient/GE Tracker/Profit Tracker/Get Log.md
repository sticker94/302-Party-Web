```toml
name = 'Get Log'
description = '{{domain}}/api/profit-tracker'
method = 'GET'
url = '{{domain}}/api/profit-tracker'
sortWeight = 5000000
id = 'a43c620c-c4d1-4427-a4e0-5992a1263dbb'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```

### Example

```toml
name = 'Get Log'
id = '867a76a1-01db-4edb-b6a8-514b804ff585'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```
