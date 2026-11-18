# Error catalog

## SQL errors

| Error | Typical message | Fix |
|-------|-----------------|-----|
| Field not found | `column "X" does not exist` | Check the schema and use the actual field name (case-sensitive) |
| Table not found | `table "X" not found` | Check the stream list, use the exact name in double quotes, and pass the right `type` (`logs`, `metrics`, `traces`) |
| Syntax error | `syntax error at or near "X"` | Check SQL syntax and clause ordering |

## Auth errors

| Code | Message | Fix |
|------|---------|-----|
| 401 / 403 | `401 Unauthorized` or `403 Forbidden` | Stop retrying. Tell the user they do not have permission for this action in the organization, or need to sign in again via `/mcp`. |

## Best-practice warnings

| Warning | Fix |
|---------|-----|
| Time filter in SQL | Remove `WHERE _timestamp ...` conditions; pass the range as `start_time` / `end_time` |
| `SELECT *` | Replace with an explicit field list, which is faster and gives dashboards stable aliases |

## Tool errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Missing required fields" | Arguments omitted | Read the tool's input schema and supply every required argument |
| `SearchSQL` returns nothing or wrong results | Guessed or missing arguments | Look up the current `SearchSQL` schema before calling it |
| Tool not found | The tool is not exposed directly by this server version | Find it with `tool_search` and run it with `tools_call` |
