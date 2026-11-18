# Pipeline Node Example

```json
{
  "name": "nginx_log_parser",
  "source": {"source_type": "realtime"},
  "nodes": [
    {
      "id": "node-input-001",
      "io_type": "input",
      "position": {"x": 100, "y": 100},
      "data": {
        "node_type": "stream",
        "org_id": "default",
        "stream_name": "nginx_raw_logs",
        "stream_type": "logs"
      }
    },
    {
      "id": "node-function-001",
      "io_type": "default",
      "position": {"x": 100, "y": 250},
      "data": {
        "node_type": "function",
        "name": "parse_nginx",
        "after_flatten": true
      }
    },
    {
      "id": "node-output-001",
      "io_type": "output",
      "position": {"x": 100, "y": 400},
      "data": {
        "node_type": "stream",
        "org_id": "default",
        "stream_name": "nginx_parsed_logs",
        "stream_type": "logs"
      }
    }
  ],
  "edges": [
    {
      "id": "enode-input-001-node-function-001",
      "source": "node-input-001",
      "target": "node-function-001"
    },
    {
      "id": "enode-function-001-node-output-001",
      "source": "node-function-001",
      "target": "node-output-001"
    }
  ]
}
```
