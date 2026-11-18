# Alert Query Examples

## SQL-based (error rate)
```json
{
  "type": "sql",
  "sql": "SELECT COUNT(_timestamp) * 100.0 / (SELECT COUNT(_timestamp) FROM \"logs\") as error_rate FROM \"logs\" WHERE level='ERROR'",
  "aggregation": {
    "group_by": [],
    "function": "avg",
    "having": {
      "operator": ">",
      "value": 5
    }
  }
}
```

## PromQL-based (latency)
```json
{
  "type": "promql",
  "promql": "histogram_quantile(0.95, api_request_duration_seconds)",
  "promql_condition": {
    "operator": ">",
    "value": 1.0
  }
}
```

## Custom (pattern matching)
```json
{
  "type": "custom",
  "conditions": {
    "column": "message",
    "operator": "Contains",
    "value": "OutOfMemory"
  },
  "search_event_type": "DerivedStream"
}
```
