---
name: dashboard-creation
description: >
  Dashboard creation, updating, and editing for OpenObserve. Use when the user asks to
  create, update, modify, or design dashboards with panels, charts, and visualizations.
  Covers layout grid (192-column), chart types, query aliases, breakdown fields, complex
  multi-panel builds, UpdateDashboard, AddPanel, UpdatePanel, and the required dashboard JSON structure.
---

# Dashboard Creation Workflow

Tools named here (for example `CreateDashboard`, `AddPanel`) belong to the OpenObserve MCP server.
Depending on the server version they are exposed directly or are found with
`tool_search` and run with `tools_call`; use whichever form is available. If no
OpenObserve tools are available, run the `setup` skill first.

## Autonomous Dashboard Creation

**Design the complete dashboard first, with no panel-count ceiling.** Infer every metric, breakdown, and view the request actually calls for — a narrow request needs few panels, a "full monitoring dashboard" request needs many. Decide this purely from what the user asked for. Only after the full panel list is settled does the next section's rule apply, and it governs tool-call mechanics only — it must never influence how many panels you design.

### New Dashboard: Bundle vs Iterate the Tool Calls [CRITICAL]

This governs HOW to call `CreateDashboard`/`AddPanel` for a **brand-new** dashboard, after the panel design is already finalized — it is a tool-efficiency detail, not a design input, and must never cause you to add or drop a panel. Editing an EXISTING dashboard always uses `AddPanel`/`UpdatePanel` one at a time regardless of panel count (see the table further below — that's a concurrent-edit-safety rule, unrelated to this one).

`CreateDashboard` can take MULTIPLE panels in a single call — its `panels` field is an array. `AddPanel`, by contrast, only ever accepts ONE panel per call — never pass an array or multiple panels to `AddPanel`; it has no way to accept more than one.

- **Small panel list** (roughly 5 or fewer — a boundary for this tool-call decision only, not a target to design toward): put every panel straight into the `panels` array of the one `CreateDashboard` call. Nothing exists yet to hash-conflict against, so this is a single round-trip covering all of them at once.
- **Large panel list**: `CreateDashboard` with an empty `panels` array, then `AddPanel` once per panel (one panel per call, as above), chaining each response's `hash` into the next call. This avoids one big payload having a subtle error (wrong axis field, bad layout math) undo the whole build — the small-list path above trades that safety net for fewer round-trips.

Loop until every designed panel has been added — never stop early because iterating takes multiple calls.

## tools_call Args for CreateDashboard [CRITICAL]

Once your full panel design is settled, its size decides the shape of this call (see "New Dashboard: Bundle vs Iterate the Tool Calls" above) — a mechanical detail, not a design constraint:
- **Large panel list**: create with an EMPTY `panels` array, then add panels iteratively with AddPanel.
- **Small panel list**: create with the FULL `panels` array already populated (skip the AddPanel loop entirely for the initial build).

The `args` object MUST contain both `org_id` and `request_body`:

```json
tools_call(tool="CreateDashboard", args={
  "org_id": "default",
  "request_body": {
    "title": "Error Analysis",
    "description": "Dashboard for error monitoring",
    "tabs": [{
      "tabId": "tab-1",
      "name": "Overview",
      "panels": []
    }]
  }
})
```

After creating, add variables and filters with UpdateDashboard (use hash from CreateDashboard response):

```json
tools_call(tool="UpdateDashboard", args={
  "org_id": "default",
  "dashboard_id": "<dashboard_id>",
  "hash": "<hash_from_create>",
  "request_body": {
    "title": "Error Analysis",
    "description": "Dashboard for error monitoring",
    "variables": {"showDynamicFilters": false, "list": []},
    "tabs": [{
      "tabId": "tab-1",
      "name": "Overview",
      "panels": []
    }]
  }
})
```


If the dashboard was created with an empty `panels` array (>5 panels), add them one by one with AddPanel (see Panel-Level CRUD APIs below). If `panels` was already populated at creation (≤5 panels), there's nothing left to add.

NEVER call `tools_call(tool="CreateDashboard")` without `args` — this will fail with "missing field `args"`.

## Layout Grid System

192-column grid (min width=12, min height=8):

- Full: 192 (100%)
- Half: 96 (50%)
- Third: 64 (33%)
- Quarter: 48 (25%)

Default panel height: **15** for all panels.
Use **tabs** to group related panels logically (e.g., by subsystem, signal type).
Vertical stacking: y = previous_y + previous_height

Example:

```
Panel 0: {x: 0, y: 0, w: 192, h: 15}   <- Full width
Panel 1: {x: 0, y: 15, w: 96, h: 15}   <- Half left
Panel 2: {x: 96, y: 15, w: 96, h: 15}  <- Half right
Panel 3: {x: 0, y: 30, w: 192, h: 15}  <- Full width
```

## Chart Type Selection

| Chart Type | Best For | Notes |
|------------|----------|-------|
| `line` | Trends over time | Needs 2+ data points |
| `area` / `area-stacked` | Volume/composition over time | `area-stacked` requires breakdown |
| `bar` / `h-bar` | Category comparison | Works with any data count |
| `stacked` / `h-stacked` | Category composition | Requires breakdown field |
| `scatter` | Correlation | Needs 2+ data points |
| `pie` / `donut` | Proportions | x=slices, y=size |
| `metric` | Single KPI number | Best for single values |
| `gauge` | Value in range | Set min/max in config |
| `heatmap` | 2D density | Requires z-axis |
| `table` | Raw/aggregated data | Most flexible |

**Rule: If a query might return few data points, prefer `bar` over `line`/`area`.**

## Breakdown Field (SQL only) [CRITICAL]

Breakdown creates multiple series by splitting data on a categorical field. Applies to SQL panels only — PromQL handles series splitting via label selectors.

Use when: "errors **by service** over time", "activity **per account**"

SQL pattern:
```sql
SELECT histogram(_timestamp) as x_axis_1, service_name as breakdown_1, COUNT(*) as y_axis_1
FROM "logs" GROUP BY x_axis_1, breakdown_1 ORDER BY x_axis_1
```

Works with: `bar`, `stacked`, `h-bar`, `h-stacked`, `line`, `area`, `area-stacked`, `scatter`
Does NOT work with: `pie`, `donut`, `metric`, `gauge`, `heatmap`, `table`

`stacked`, `h-stacked`, `area-stacked` REQUIRE a breakdown field.

## SQL Query Column Aliases [CRITICAL PITFALL]

For SQL panels, field `alias` values must match SQL column aliases exactly.

| Query Type | SQL | Field aliases |
|------------|-----|---------------|
| Time series | `SELECT histogram(_timestamp) as x_axis_1, COUNT(*) as y_axis_1 FROM "stream" GROUP BY x_axis_1 ORDER BY x_axis_1` | x: `x_axis_1`, y: `y_axis_1` |
| Category | `SELECT service as x_axis_1, COUNT(*) as y_axis_1 FROM "stream" GROUP BY x_axis_1 ORDER BY y_axis_1 DESC` | x: `x_axis_1`, y: `y_axis_1` |
| With breakdown | `SELECT histogram(_timestamp) as x_axis_1, level as breakdown_1, COUNT(*) as y_axis_1 FROM "stream" GROUP BY x_axis_1, breakdown_1 ORDER BY x_axis_1` | x: `x_axis_1`, y: `y_axis_1`, breakdown: `breakdown_1` |
| Table | `SELECT _timestamp, message, level FROM "stream" ORDER BY _timestamp DESC LIMIT 50` | No special aliases |

Wrong alias = empty chart! `alias` in fields config MUST match the `AS` clause in SQL.

**Does NOT apply to PromQL** — PromQL panels must have empty `fields.x` and `fields.y` arrays (see Metrics Dashboard section).

### Table Panels

Table panels with `customQuery: true` and empty x/y fields MUST set `"table_dynamic_columns": true` in panel config.

## Metrics Dashboard (PromQL) [CRITICAL]

When creating dashboards from metric streams:

### Query Rules
- `queryType` MUST be `"promql"` (not `""` or `"sql"`)
- Counter metrics → use `rate()`, NOT `sum()` directly
- Gauge metrics → use as-is (e.g., `avg`, `min`, `max`)
- When dividing two PromQL queries, labels must match exactly for division to work (e.g., both sides need the same `instance` label)

### Fields Structure for PromQL
When `customQuery: true` is used for PromQL, `fields.x` and `fields.y` MUST be empty arrays `[]`. The UI rejects PromQL queries that have X/Y axis fields defined.

```json
{
  "queryType": "promql",
  "queries": [{
    "query": "rate(http_requests_total{job=\"api\"}[5m])",
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
  }]
}
```

### Variables and Legends
- Use single curly braces: `{variable_name}` — NOT double `{{variable_name}}`
- Verify legends use appropriate label names from the metric schema

## Complex Dashboards (20+ Panels)

Use tabs to organize panels by category. Plan layout grouping and chart types before building.

**Large dashboard JSON handling:** tools expect inline JSON in their arguments. The server cannot
read file paths, so never pass a path to a local file in place of the JSON. For a large dashboard,
create it with an empty `panels` array and add panels one at a time with `AddPanel`.

## Panel-Level CRUD APIs [PREFERRED for creation & editing]

Use these APIs to iteratively build panels or edit individual panels without sending the entire dashboard.
The server handles fetch-modify-save internally with optimistic locking via hash.

### AddPanel — Add a panel to an existing dashboard

```
tool_search("add panel") -> tools_call(tool="AddPanel", args={
  "org_id": "default",
  "dashboard_id": "<dashboard_id>",
  "hash": "<current_hash>",
  "request_body": {
    "panel": { ... panel object ... },
    "tabId": "tab-1"  // optional, defaults to first tab
  }
})
```

- Layout is **auto-computed** by the server if you omit x/y (or set both to 0). You can set w/h for size hints.
- Panel ID is **auto-generated** if empty. The response includes the assigned ID.
- Response returns `{ panel, hash, tabId }` — use the new `hash` for subsequent calls.
- **One panel per call, always** — `request_body.panel` is a single object, not an array. To add N panels, call `AddPanel` N times, chaining the hash each time (see "New Dashboard: Bundle vs Iterate the Tool Calls" above). `CreateDashboard` is the one that accepts multiple panels at once, via its `panels` array — `AddPanel` never does.

### UpdatePanel — Update a single panel by ID

```
tool_search("update panel") -> tools_call(tool="UpdatePanel", args={
  "org_id": "default",
  "dashboard_id": "<dashboard_id>",
  "panel_id": "<panel_id>",
  "hash": "<current_hash>",
  "request_body": {
    "panel": { ... updated panel object ... },
    "tabId": "tab-1"  // optional
  }
})
```

- **Layout is preserved** if you send layout as all zeros `{x:0,y:0,w:0,h:0,i:0}` — so you can update queries/config without worrying about layout.
- The `panel_id` in the URL is authoritative (overrides `panel.id` in body).
- Response returns `{ panel, hash, tabId }`.

### DeletePanel — Remove a panel by ID

```
tool_search("delete panel") -> tools_call(tool="DeletePanel", args={
  "org_id": "default",
  "dashboard_id": "<dashboard_id>",
  "panel_id": "<panel_id>",
  "hash": "<current_hash>",
  "tabId": "tab-1"  // optional, searches all tabs if omitted
})
```

- Response returns `{ hash, panelId }`.

### Hash Chaining for Sequential Operations

Each panel operation returns a new `hash`. Use it for the next call:

```
1. GetDashboard → hash_0
2. AddPanel(hash=hash_0) → hash_1, panel_id_1
3. AddPanel(hash=hash_1) → hash_2, panel_id_2
4. UpdatePanel(hash=hash_2, panel_id=panel_id_1) → hash_3
```

### When to Use Panel APIs vs Full UpdateDashboard [CRITICAL]

**NEVER use UpdateDashboard to delete or update a single panel** — it is slow and error-prone. Use the atomic panel APIs instead.

| Task | Correct Tool | NOT |
|------|-------------|-----|
| Create new dashboard from scratch, ≤5 panels | **CreateDashboard** (full `panels` array in one call) + **UpdateDashboard** (variables) | ~~AddPanel loop for a brand-new small dashboard~~ (extra round-trips for no benefit — nothing exists yet to hash-conflict against) |
| Create new dashboard from scratch, >5 panels | **CreateDashboard** (empty panels) + **UpdateDashboard** (variables) + **AddPanel** (one per panel, chain hashes) | ~~CreateDashboard with all panels~~ (large payload, harder for the model to get every panel right in one shot) |
| Add 1-5 panels to an EXISTING dashboard | **AddPanel** (one per panel, chain hashes) | ~~UpdateDashboard~~ |
| Update a panel's query/title/config | **UpdatePanel** | ~~UpdateDashboard~~ |
| Remove a panel | **DeletePanel** | ~~UpdateDashboard~~ |
| Reorder/restructure all panels | **UpdateDashboard** (full PUT) | |
| Change dashboard title/variables/tabs | **UpdateDashboard** (full PUT) | |
| Add variables/filters after creation | **UpdateDashboard** (full PUT) | |

## UpdateDashboard Workflow (Full PUT)

```
1. GetDashboard to retrieve current JSON + hash
2. Modify the JSON (add/remove/edit panels)
3. Send FULL modified dashboard body to UpdateDashboard
4. Pass the hash from step 1 for conflict detection
```

UpdateDashboard is a full PUT — send the complete body, not just changes.
When updating, preserve existing alias conventions — don't force x_axis_1/y_axis_1 on existing panels.

The same 192-column layout grid applies (Full: 192, Half: 96, Third: 64, Quarter: 48, height: 15).
When modifying a fetched dashboard, preserve the existing panel layout values unless explicitly restructuring the layout.

Example:

```
tool_search("update dashboard") -> tools_call(tool="UpdateDashboard", args={
  "org_id": "default",
  "dashboard_id": "<dashboard_id>",
  "hash": "<hash_from_GetDashboard>",
  "request_body": {
    "title": "Updated Error Analysis",
    "description": "Error monitoring dashboard",
    "variables": {"showDynamicFilters": false, "list": []},
    "tabs": [{
      "tabId": "tab-1",
      "name": "Overview",
      "panels": [
        {
          "id": "Panel_0",
          "type": "line",
          "title": "Error Count Over Time",
          "queryType": "sql",
          "queries": [{ ... }],
          "layout": {"x": 0, "y": 0, "w": 192, "h": 15, "i": 0},
          "config": {"show_legends": true}
        },
        {
          "id": "Panel_1",
          "type": "bar",
          "title": "Errors by Service",
          "queryType": "sql",
          "queries": [{ ... }],
          "layout": {"x": 0, "y": 15, "w": 96, "h": 15, "i": 1},
          "config": {"show_legends": true}
        },
        {
          "id": "Panel_2",
          "type": "table",
          "title": "Recent Errors",
          "queryType": "sql",
          "queries": [{ ... }],
          "layout": {"x": 96, "y": 15, "w": 96, "h": 15, "i": 2},
          "config": {"show_legends": false, "table_dynamic_columns": true}
        }
      ]
    }]
  }
})
```

## Finishing

After every panel has been added, tell the user the dashboard title and ID and give them a link:
`<base_url>/web/dashboards/view?org_identifier=<org_id>&dashboard=<dashboard_id>&folder=<folder_id>`,
where `<base_url>` is the host of the OpenObserve MCP server URL (leave out `folder` for the default
folder). Do this once, at the end, not between
panels.

Load `references/panel-template.md` resource for the complete panel JSON structure.
