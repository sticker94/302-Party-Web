```toml
name = 'Get Sold Transactions'
description = '{{domain}}/api/profit-tracker/sold'
method = 'GET'
url = '{{domain}}/api/profit-tracker/sold?orderBy=soldDate&order=asc&showAll='
sortWeight = 10000000
id = 'cf7df5dd-14f9-4b6d-8782-0399d74bb7ec'

[[queryParams]]
key = 'orderBy'
value = 'soldDate'

[[queryParams]]
key = 'order'
value = 'asc'

[[queryParams]]
key = 'showAll'
value = ''

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```

### Example

```toml
name = 'Get Sold Transactions'
id = '69c6adde-be74-47ea-87d9-78b70e132469'

[[queryParams]]
key = 'orderBy'
value = 'soldDate'

[[queryParams]]
key = 'order'
value = 'asc'

[[queryParams]]
key = 'showAll'
value = ''

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```
