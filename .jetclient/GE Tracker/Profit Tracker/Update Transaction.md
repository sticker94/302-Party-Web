```toml
name = 'Update Transaction'
description = '{{domain}}/api/profit-tracker/f1809a9a-9611-4f16-9463-0b409a636527'
method = 'POST'
url = '{{domain}}/api/profit-tracker/f1809a9a-9611-4f16-9463-0b409a636527'
sortWeight = 2000000
id = '2738679d-37fd-47bc-a5a4-e3a6b0cca6e9'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'

[[headers]]
key = 'Content-Type'
value = 'application/json'

[body]
type = 'PLAIN'
raw = '{"status":"selling", "sell_price":"3.5m"}'
```

### Example

```toml
name = 'Update Transaction'
id = '8ca531fe-3854-43a0-99bc-29a20e844d74'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'

[[headers]]
key = 'Content-Type'
value = 'application/json'

[body]
type = 'PLAIN'
raw = '{"status":"selling", "sell_price":"3.5m"}'
```
