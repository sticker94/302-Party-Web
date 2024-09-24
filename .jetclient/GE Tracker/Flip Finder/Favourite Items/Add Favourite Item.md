```toml
name = 'Add Favourite Item'
description = '{{domain}}/api/favourite-items'
method = 'POST'
url = '{{domain}}/api/favourite-items'
sortWeight = 3000000
id = '848efc6b-b366-4ef9-a132-6449d947f0d3'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'

[body]
type = 'PLAIN'
raw = '{"item_id": 13576}'
```
