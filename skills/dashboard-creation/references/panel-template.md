# Dashboard Panel Template

## Standard Panel (line/bar/area — no breakdown)

```json
{
  "id": "panel-0",
  "type": "line",
  "title": "Panel Title",
  "description": "What this panel shows",
  "queryType": "sql",
  "queries": [{
    "query": "SELECT histogram(_timestamp) as x_axis_1, COUNT(*) as y_axis_1 FROM \"stream\" GROUP BY x_axis_1 ORDER BY x_axis_1",
    "vrlFunctionQuery": "",
    "customQuery": true,
    "fields": {
      "stream": "stream_name",
      "stream_type": "logs",
      "x": [{"label": "Time", "alias": "x_axis_1", "column": "x_axis_1"}],
      "y": [{"label": "Count", "alias": "y_axis_1", "column": "y_axis_1"}],
      "z": [],
      "breakdown": [],
      "filter": {"filterType": "group", "logicalOperator": "AND", "conditions": []}
    },
    "config": {"promql_legend": ""}
  }],
  "layout": {"x": 0, "y": 0, "w": 192, "h": 15, "i": 0},
  "config": {"show_legends": true}
}
```

## Panel with Breakdown (multi-series by category)

```json
{
  "id": "panel-1",
  "type": "bar",
  "title": "Errors by Service Over Time",
  "description": "Error count broken down by service",
  "queryType": "sql",
  "queries": [{
    "query": "SELECT histogram(_timestamp) as x_axis_1, service_name as breakdown_1, COUNT(*) as y_axis_1 FROM \"logs\" WHERE level='error' GROUP BY x_axis_1, breakdown_1 ORDER BY x_axis_1",
    "vrlFunctionQuery": "",
    "customQuery": true,
    "fields": {
      "stream": "logs",
      "stream_type": "logs",
      "x": [{"label": "Time", "alias": "x_axis_1", "column": "x_axis_1"}],
      "y": [{"label": "Errors", "alias": "y_axis_1", "column": "y_axis_1"}],
      "z": [],
      "breakdown": [{"label": "Service", "alias": "breakdown_1", "column": "breakdown_1"}],
      "filter": {"filterType": "group", "logicalOperator": "AND", "conditions": []}
    },
    "config": {"promql_legend": ""}
  }],
  "layout": {"x": 0, "y": 0, "w": 192, "h": 15, "i": 1},
  "config": {"show_legends": true, "legends_position": "right"}
}
```

## Table Panel (raw records)

CRITICAL: Table panels with `customQuery: true` MUST set `"table_dynamic_columns": true` in config.

```json
{
  "id": "panel-2",
  "type": "table",
  "title": "Recent Error Logs",
  "queryType": "sql",
  "queries": [{
    "query": "SELECT _timestamp, service_name, level, message FROM \"logs\" WHERE level='error' ORDER BY _timestamp DESC LIMIT 50",
    "vrlFunctionQuery": "",
    "customQuery": true,
    "fields": {
      "stream": "logs",
      "stream_type": "logs",
      "x": [],
      "y": [],
      "z": [],
      "filter": {"filterType": "group", "logicalOperator": "AND", "conditions": []}
    },
    "config": {"promql_legend": ""}
  }],
  "layout": {"x": 0, "y": 15, "w": 192, "h": 15, "i": 2},
  "config": {"show_legends": false, "table_dynamic_columns": true}
}
```

## Metric Panel (single KPI value)

```json
{
  "id": "panel-3",
  "type": "metric",
  "title": "Total Error Count",
  "queryType": "sql",
  "queries": [{
    "query": "SELECT COUNT(*) as y_axis_1 FROM \"logs\" WHERE level='error'",
    "vrlFunctionQuery": "",
    "customQuery": true,
    "fields": {
      "stream": "logs",
      "stream_type": "logs",
      "x": [],
      "y": [{"label": "Errors", "alias": "y_axis_1", "column": "y_axis_1"}],
      "z": [],
      "filter": {"filterType": "group", "logicalOperator": "AND", "conditions": []}
    },
    "config": {"promql_legend": ""}
  }],
  "layout": {"x": 0, "y": 0, "w": 48, "h": 15, "i": 3},
  "config": {}
}
```

## PromQL Panel (metrics)

```json
{
  "id": "panel-4",
  "type": "line",
  "title": "HTTP Request Rate",
  "description": "Rate of HTTP requests per second",
  "queryType": "promql",
  "queries": [{
    "query": "rate(http_requests_total{job=\"api\"}[5m])",
    "vrlFunctionQuery": "",
    "customQuery": true,
    "fields": {
      "stream": "http_requests_total",
      "stream_type": "metrics",
      "x": [],
      "y": [],
      "z": [],
      "filter": {"filterType": "group", "logicalOperator": "AND", "conditions": []}
    },
    "config": {"promql_legend": "{instance}"}
  }],
  "layout": {"x": 0, "y": 0, "w": 96, "h": 15, "i": 4},
  "config": {"show_legends": true}
}
```

See SKILL.md "Metrics Dashboard (PromQL)" section for query rules.

## Field Reference

### AxisItem structure
```json
{"label": "Display Name", "alias": "sql_column_alias", "column": "sql_column_alias"}
```

CRITICAL: The `alias` value must match the SQL `AS` clause exactly.

### Required for all panels
- `x`: X-axis fields — array of AxisItem
- `y`: Y-axis fields — array of AxisItem
- `z`: Z-axis fields (heatmap only) — array of AxisItem, `[]` for non-heatmap
- `filter`: MUST be object: `{"filterType": "group", "logicalOperator": "AND", "conditions": []}`

### Optional
- `breakdown`: Series grouping — array of AxisItem. For bar/stacked/line/area/scatter

## Supported types

Chart types: `line`, `area`, `area-stacked`, `bar`, `h-bar`, `stacked`, `h-stacked`, `scatter`, `pie`, `donut`, `metric`, `gauge`, `heatmap`, `table`, `geomap`, `sankey`

Query types: `sql`, `promql`

Stream types: `logs`, `metrics`, `traces`
