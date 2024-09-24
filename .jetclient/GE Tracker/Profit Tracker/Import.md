```toml
name = 'Import'
description = '{{domain}}/api/profit-tracker/import'
method = 'POST'
url = '{{domain}}/api/profit-tracker/import'
sortWeight = 14000000
id = 'b2d7a75e-4b25-46f1-9a56-1667711ab41d'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'

[body]
type = 'PLAIN'
raw = '''
{
  "transactions": [
    {
      "id": "9301a85f-5640-4f1e-90b2-d65b45719edc",
      "itemId": 28338,
      "qty": 5,
      "buyPrice": 1,
      "sellPrice": 5,
      "status": "sold",
      "buyDate": "2023-10-31 08:17:57",
      "boughtDate": "2023-10-31 08:17:57",
      "sellDate": "2023-10-31 08:17:57",
      "soldDate": "2023-10-31 08:17:57",
      "intendedSellPrice": 5
    },
    {
      "id": "f098c9db-7bfb-4385-8787-301b932b67b5",
      "itemId": 28338,
      "qty": 5,
      "buyPrice": 1,
      "sellPrice": 5,
      "status": "sold",
      "buyDate": "2023-10-31 08:17:57",
      "boughtDate": "2023-10-31 08:17:57",
      "sellDate": "2023-10-31 08:17:57",
      "soldDate": "2023-10-31 08:17:57",
      "intendedSellPrice": 5
    }
  ]
}'''
```

### Example

```toml
name = 'Get Previous Transactions'
id = '539d89f7-05c9-4c88-9b12-5a3096296eab'

[[headers]]
key = 'Accept'
value = 'application/x.getracker.{{apiVersion}}+json'
```
