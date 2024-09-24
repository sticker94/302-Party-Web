```toml
name = 'Create Transaction'
description = '{{domain}}/api/profit-tracker'
method = 'POST'
url = '{{domain}}/api/profit-tracker'
sortWeight = 1000000
id = '36b8e20f-cea0-4599-9dbf-69d038089a4e'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'

[[headers]]
key = 'Content-Type'
value = 'application/json'

[body]
type = 'PLAIN'
raw = '{"item_id":13190, "qty":55, "buy_price":"3.4m", "status":"sold", "sell_price":"3.85m"}'
```

### Example

```toml
name = 'Create Transaction'
id = 'd57e965b-a438-4f95-802a-3407db76353d'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'

[[headers]]
key = 'Content-Type'
value = 'application/json'

[body]
type = 'PLAIN'
raw = '{"item_id":13190, "qty":55, "buy_price":"3.4m", "status":"sold", "sell_price":"3.85m"}'
```
