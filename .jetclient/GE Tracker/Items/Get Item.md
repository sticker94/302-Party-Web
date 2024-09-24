```toml
name = 'Get Item'
description = '{{domain}}/api/items/13576'
method = 'GET'
url = '{{domain}}/api/items/13576'
sortWeight = 1000000
id = '9c9315a1-056c-4f78-b4b8-d8b7cc9303cd'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```

### Example

```toml
name = 'Get Item'
id = '3e7f6541-a5bf-40b8-b7b9-d5906064949d'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```
