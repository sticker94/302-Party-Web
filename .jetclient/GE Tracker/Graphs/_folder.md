All graph endpoints will return two keys:

* `source` - will be either `osbuddy` or `getracker`. If OSBuddy is not responding, then we will automatically load the `getracker` source
* `data` - an array of data containing historical item data

You may supply a `source` query string parameter to force a certain data source:

```
GET https://www.ge-tracker.com/api/graph/3105/month?source=getracker
```

Candlestick OHLC data may be returned by altering the URL slightly:

```
GET https://www.ge-tracker.com/api/graph/candlestick/3105/month
```

```toml
name = 'Graphs'
description = '{{domain}}/api/graph/'
sortWeight = 2000000
id = '8f175e52-62aa-49df-86e6-e5c5745605eb'
```
