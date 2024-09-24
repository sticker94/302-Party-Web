```toml
name = 'Get Selling Transactions'
description = '{{domain}}/api/profit-tracker/selling'
method = 'GET'
url = '{{domain}}/api/profit-tracker/selling'
sortWeight = 9000000
id = '1d5fb894-11e1-4dfd-b3bc-57c22b0b8eb5'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```

### Example

```toml
name = 'Get Selling Transactions'
id = 'b5727055-b329-4d98-b2be-e07c1fb8c125'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```
