```toml
name = 'Delete Price Alert'
description = '{{domain}}/api/price-alerts/{id}'
method = 'DELETE'
url = '{{domain}}/api/price-alerts/{id}'
sortWeight = 3000000
id = 'e73c9e58-a46f-462d-bfa7-a375019c93d9'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'

[body]
type = 'PLAIN'
```
