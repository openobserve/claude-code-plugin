# VRL Script Example

Parse Apache common log format:

```vrl
# Define regex pattern (use raw string)
pattern = r'^(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<path>[^"]+) HTTP\/(?P<version>[^"]+)" (?P<status>\d+) (?P<bytes>\d+)'

# Parse with error handling (mandatory — use tuple return for debuggability)
parsed, err = parse_regex(.message, pattern)
if err != null {
  .vrl_error = err
}

# Extract fields with null checks
if exists(parsed.ip) {
  .client_ip = parsed.ip
}

if exists(parsed.status) {
  .status_code, err = to_int(parsed.status)
  if err != null {
    .vrl_error = err
  }
}

if exists(parsed.method) {
  .http_method = parsed.method
}

# Enrichment example
if exists(.status_code) {
  if .status_code >= 500 {
    .severity = "error"
  } else if .status_code >= 400 {
    .severity = "warning"
  } else {
    .severity = "info"
  }
}
```

VRL Comment Rules:
- Use `#` for single-line comments (NOT `//`)
- Comments explain what code does, not just repeat code
- Keep comments concise and relevant

Error Handling Rules:
- ALWAYS use tuple return `result, err = fn()` over `fn!()` — makes debugging easier
- Store errors in `.vrl_error` so they appear in the event and can be searched/alerted on
- Only use `fn!()` for trivial one-liners where failure means the event is unusable
