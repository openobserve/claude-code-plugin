# OpenObserve plugin for Claude Code

Use [OpenObserve](https://openobserve.ai) from Claude Code: query logs, metrics and traces, and work with streams, dashboards and alerts through conversation.

## What's included

| Skill | What it does |
|---|---|
| `setup` | Connects Claude Code to the MCP server built into your OpenObserve instance. Asks for your cloud region or self-hosted URL and your organization, checks the endpoint, and registers it. |
| `sql-query` | Schema-first workflow for writing and validating SQL and PromQL against your streams. |
| `dashboard-creation` | Builds and edits dashboards: layout grid, chart types, panel JSON, and the panel-level tools. |
| `alert-creation` | Creates and edits alerts and alert destinations, with sensible defaults. |
| `pipeline-creation` | Designs data pipelines: source and destination streams, functions and conditions. |
| `vrl-scripts` | Writes and validates VRL functions for parsing and transforming data. |
| `spl-conversion` | Converts Splunk SPL searches to OpenObserve SQL. |
| `openobserve-instrument` | Instruments an LLM or AI-agent app to send OpenTelemetry traces to OpenObserve. |

The skills are adapted from the [`@openobserve/skills`](https://www.npmjs.com/package/@openobserve/skills) package (version 1.2.1) for use in Claude Code.

## Install

```
/plugin marketplace add openobserve/claude-code-plugin
/plugin install openobserve@openobserve
```

## Connect your instance

In Claude Code, run:

```
/openobserve:setup
```

or just ask "connect OpenObserve". You will be asked for:

| Value | Example | Notes |
|---|---|---|
| OpenObserve URL | `https://cloud.openobserve.ai` | Cloud: `cloud` (US), `eu1`, `ap1`. Self-hosted: your own host. |
| Organization ID | `default` | The `org_identifier` shown in the OpenObserve UI address bar. |

Then run `/mcp`, pick `openobserve`, and sign in. Sign-in uses OAuth in your browser; the plugin stores no credentials.

To do the same by hand:

```
claude mcp add --transport http --scope user openobserve https://<host>/api/<org_id>/mcp
```

## What the skills can run

- `setup` runs `claude mcp list`, one unauthenticated `curl` probe of the endpoint you name, and `claude mcp add`.
- `openobserve-instrument` edits your project, installs OpenTelemetry packages, and runs `scripts/preflight.py` (Python standard library only), which sends an empty trace batch to your OpenObserve instance to check the credentials in your `.env`. For supported Python SDKs it downloads the OpenObserve installer from a pinned commit of [`openobserve/o2-datasource`](https://github.com/openobserve/o2-datasource) and runs it only if its SHA-256 matches the value in the skill.
- The other skills only call OpenObserve MCP tools.

## Why the server is not bundled

Every OpenObserve organization has its own MCP address (`<host>/api/<org_id>/mcp`), and self-hosted instances live on their own hosts, so there is no single URL a plugin could ship. The setup skill registers your endpoint as an ordinary user-level MCP server, which you can inspect or remove with `claude mcp list` and `claude mcp remove openobserve`.

## Permissions

The MCP server acts with the permissions of the signed-in user. It is **not read-only**: besides search, it exposes tools that create, update and delete dashboards, alerts and other resources. Claude Code asks before each tool call unless you allow it; use a role with read-only access if you want to rule out changes.

## Local development

```
claude plugin validate .
claude --plugin-dir .
```

## Privacy

The plugin talks only to the OpenObserve instance you configure. See the [OpenObserve privacy policy](https://openobserve.ai/legal/privacy-policy/).

## License

Apache-2.0
