```toml
name = 'Search v2'
description = '{{domain}}/api/users/search'
method = 'POST'
url = '{{domain}}/api/users/search'
sortWeight = 3000000
id = 'e0d874ac-e0a8-4aec-972a-a430764c8399'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'

[body]
type = 'PLAIN'
raw = '{"query": "james"}'
```
