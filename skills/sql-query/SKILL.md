---
name: sql-query
description: >
  SQL and PromQL query generation for OpenObserve. Use when the user asks to
  write, debug, or optimize SQL or PromQL queries against logs, metrics, or
  traces streams. Covers schema-first workflow, time-range rules, best
  practices, and PromQL label verification.
---

# SQL & PromQL queries for OpenObserve

Queries run through the OpenObserve MCP server. If no OpenObserve tools are
available in this session, run the `setup` skill first. Depending on the server
version, tools such as `StreamList`, `StreamSchema`, `SearchSQL` and
`PrometheusRangeQuery` are exposed directly, or are found with `tool_search`
and run with `tools_call`. Use whichever form the server offers.

## Schema first

Most failed queries come from guessed field names. Never write SQL or PromQL
against a stream whose schema you have not seen in this conversation.

1. **Find the stream.** If the user did not name one, list streams
   (`StreamList`) for the right type: `logs`, `metrics` or `traces`.
2. **Fetch the schema.** Call `StreamSchema` with `org_id`, `stream_name` and
   `type`. Skip this only when the schema is already in the conversation.
3. **Choose fields.**
   - If the stream has a User-Defined Schema (UDS), use only UDS fields. It is
     the source of truth and overrides auto-detected fields.
   - Otherwise use the auto-detected fields.
   - Field names are case-sensitive. Note data types and which fields are
     indexed.
4. **Write the query** using only field names from step 3.
5. **Validate.** Check the current `SearchSQL` input schema, then call it with
   `validate: true` and every required argument (at minimum `sql`,
   `start_time`, `end_time`, `org_id`, `stream_name`). Do not guess or omit
   arguments: missing ones cause silent failures or wrong results.
6. **Fix or stop.** If validation fails, read the error, fix the query and
   validate again. Stop after three attempts, or as soon as the same error
   appears twice, and show the user the error and the last query.
7. **Return** the validated query with a short explanation.

Example of UDS priority:

```
StreamSchema response:
- UDS:           {log_level: string, service: string, msg: string}
- Auto-detected: {level: string, service_name: string, message: string}

Use only log_level, service, msg. Ignore level, service_name, message.
```

## Time range

Do not put the time range in the SQL. It is supplied outside the query: as
`start_time` / `end_time` on `SearchSQL`, or by the time picker when the query
is pasted into the OpenObserve UI or a dashboard panel. A time predicate in the
SQL filters the data twice.

Avoid:

```sql
WHERE _timestamp >= NOW() - INTERVAL '3 months'
WHERE _timestamp BETWEEN ... AND ...
```

Using `_timestamp` for bucketing or aggregation is fine:

```sql
SELECT histogram(_timestamp, '5 minutes') AS x_axis_1, ...
SELECT DATE_TRUNC('hour', _timestamp) AS x_axis_1, ...
SELECT MIN(_timestamp), MAX(_timestamp) ...
```

## SQL best practices

| Rule | Avoid | Prefer | Why |
|------|-------|--------|-----|
| No `SELECT *` | `SELECT * FROM logs` | `SELECT _timestamp, level, message FROM logs` | Performance and clarity |
| Counting rows | `COUNT(*)` | `COUNT(_timestamp)` | Optimized in OpenObserve |
| Field names | Guessed names | Names from the schema (UDS first) | Prevents "column not found" |
| Time range | `WHERE _timestamp >= ...` | `start_time` / `end_time` | Avoids double filtering |
| Stream names | Bare names with special characters | `"stream-name"` in double quotes | Prevents "table not found" |

See `references/sql-functions.md` for OpenObserve-specific functions (full-text
search, arrays, histogram, regex extraction) and `references/error-catalog.md`
for common errors and fixes.

## Traces

Trace spans live in trace streams and are queried with `SearchSQL`. Pass
`type: "traces"` in the arguments; without it the query targets log streams and
the trace stream is not found.

## PromQL

PromQL follows the same schema-first rule. Metrics have labels rather than
fields.

1. Identify the metrics stream (`type: "metrics"`).
2. Fetch its schema with `StreamSchema`.
3. Build the query using only metric names and labels from the schema, for
   selectors as well as `by` / `without`.
4. Run it with `PrometheusRangeQuery` over a short range to confirm it returns
   series. There is no validate-only mode for PromQL, so checking labels
   against the schema matters.
