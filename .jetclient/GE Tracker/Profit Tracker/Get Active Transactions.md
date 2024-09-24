```toml
name = 'Get Active Transactions'
description = '{{domain}}/api/profit-tracker/active-transactions'
method = 'GET'
url = '{{domain}}/api/profit-tracker/active-transactions'
sortWeight = 12000000
id = '0c417286-ddaa-4297-81dc-536a6efeae8d'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```

### Example

```toml
name = 'Get Active Transactions'
id = '5faff9d5-9dc5-47ae-9f53-2e4664d6d97f'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```
