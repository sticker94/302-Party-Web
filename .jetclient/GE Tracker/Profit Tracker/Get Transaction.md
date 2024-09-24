```toml
name = 'Get Transaction'
description = '{{domain}}/api/profit-tracker/a1910bff-dba5-4b99-9661-6fd02748da9c'
method = 'GET'
url = '{{domain}}/api/profit-tracker/a1910bff-dba5-4b99-9661-6fd02748da9c'
sortWeight = 4000000
id = '11bc99db-0927-4cb9-b9f9-2e660c13d2fe'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```

### Example

```toml
name = 'Get Transaction'
id = '9fd11d3b-c5cd-4c71-b615-c112ea73104a'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```
