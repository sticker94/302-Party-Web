```toml
name = 'Create Price Alert'
description = '{{domain}}/api/price-alerts'
method = 'POST'
url = '{{domain}}/api/price-alerts'
sortWeight = 2000000
id = '3195cace-a180-4189-86c1-2f35dae17528'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'

[body]
type = 'PLAIN'
raw = '{"itemId": 13190, "field": "selling", "type": "above", "price": "2m", "methods": {"sms": true, "email": true}}'
```
