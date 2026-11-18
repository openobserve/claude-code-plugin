---
name: alert-creation
description: >
  Alert creation and editing for OpenObserve. Use when the user asks to create,
  edit, or configure alerts, alert destinations, or notification rules. Covers
  naming rules, choosing a destination, default thresholds, and alert query
  types (SQL, PromQL, custom).
---

# Alert Creation Workflow

Tools named here (for example `CreateAlert`, `CreateDestination`) belong to the
OpenObserve MCP server. Depending on the server version they are exposed
directly or are found with `tool_search` and run with `tools_call`; use
whichever form is available. If no OpenObserve tools are available, run the
`setup` skill first.

## Workflow

User: "Alert me when error rate exceeds 5%"

1. **Choose the stream.** Use the stream the user named. If they named none,
   list streams and pick the one that clearly matches; ask only if several do.
2. **Check the schema** of that stream and build the query with real field
   names (see the `sql-query` skill).
3. **Choose a destination** (see below). This is the one thing to ask about
   when it is not obvious.
4. **Apply defaults** for anything the user did not specify (see the table).
5. **Create the alert:** check the current `CreateAlert` input schema with
   `tool_search("create alert")`, then call it with `org_id` and the alert as
   `request_body`.
6. **Verify** the response, then report what was created, including the
   defaults you chose: "Created alert `high_error_rate` on `app_logs`: error
   rate > 5% over 5 minutes, notifying `team_slack`, silenced for 10 minutes
   after firing."

Keep questions to a minimum: state the defaults you applied instead of asking
about each one. The user can ask for changes afterwards.

## Alert naming rules

Names must be snake_case with no special characters.

Correct: `high_error_rate`, `cpu_usage_critical`, `api_latency_p95`
Wrong: `High-Error-Rate`, `CPU:Usage:Critical`, `API Latency (p95)`

Forbidden characters: `:`, `#`, `?`, `&`, `%`, `/`, quotes, spaces

## Destinations

An alert needs at least one destination; the `destinations` array cannot be
empty.

1. List the existing alert destinations (`tool_search("list destinations")`).
2. If the user named one, use it. If exactly one exists, use it and say so.
   If several exist and none was named, ask which to use.
3. If none exist, ask the user where notifications should go (a webhook URL
   such as a Slack or PagerDuty endpoint, or email addresses). Do not invent a
   URL and do not create a placeholder destination: an alert that notifies
   nowhere looks healthy while nobody is told.
4. Create the destination with `CreateDestination`. An alert destination must
   include a `template`; use `"Default"` for the built-in one. Without a
   template it becomes a pipeline destination and cannot be used by alerts.

   ```json
   {
     "name": "team_webhook",
     "type": "http",
     "url": "https://example.com/webhook",
     "method": "post",
     "template": "Default",
     "headers": {"Content-Type": "application/json"}
   }
   ```

   Email destinations use `"type": "email"` with an `emails` array and need
   SMTP configured on the OpenObserve instance.

Reuse existing destinations where possible instead of creating one per alert.

## Defaults

| Parameter | Default | Meaning |
|-----------|---------|---------|
| period | 5 (minutes) | Evaluate the last 5 minutes of data |
| frequency | 1 | Trigger on first occurrence |
| silence | 10 (minutes) | Stay quiet for 10 minutes after firing |
| operator | `>` | Greater than |
| enabled | true | Active as soon as it is created |

## Alert query types

| Type | Use case | Example |
|------|----------|---------|
| SQL | Log-based alerts with complex conditions | Error rate, log pattern matching |
| PromQL | Metrics-based alerts | Latency percentiles, rate calculations |
| Custom | Pattern matching on specific fields | "OutOfMemory" in the message field |

See `references/alert-examples.md` for complete alert query examples.

## Editing and deleting

Fetch the alert first, change only what the user asked for, and send the
complete alert back. Before deleting an alert or a destination, name it and
confirm with the user; check that a destination is not used by other alerts.
