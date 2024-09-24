```toml
name = 'Get Multiple Items'
description = '{{domain}}/api/items/multi'
method = 'GET'
url = '{{domain}}/api/items/multi/?itemIds=3105,13576'
sortWeight = 3000000
id = '04f5572d-14c8-435e-a219-b0f3a7bb88df'

[[queryParams]]
key = 'itemIds'
value = '3105,13576'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```
