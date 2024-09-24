```toml
name = 'FSW Transfer'
description = '{{domain}}/api/fsw-transfer'
method = 'GET'
url = '{{domain}}/api/fsw-transfer'
sortWeight = 2000000
id = 'eb42574b-b6cc-4164-b4e2-7e07dee4db1d'

[[queryParams]]
key = 'filters'
value = 'false'
disabled = true

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```
