```toml
name = 'Get Summary'
description = '{{domain}}/api/profit-tracker/summary'
method = 'GET'
url = '{{domain}}/api/profit-tracker/summary'
sortWeight = 6000000
id = '4d5027a8-0f51-45f4-9351-2c262bc7ee17'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```

### Example

```toml
name = 'Get Summary'
id = '185ce993-e140-410a-8882-89672816544e'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```
