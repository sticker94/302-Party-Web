```toml
name = 'Get Bought Transactions'
description = '{{domain}}/api/profit-tracker/bought'
method = 'GET'
url = '{{domain}}/api/profit-tracker/bought'
sortWeight = 8000000
id = '6eabc8e5-433f-48b9-9bcd-910fde0b9207'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```

### Example

```toml
name = 'Get Bought Transactions'
id = '81cea36f-fb9d-4956-86c2-0ae9868c0a8d'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```
