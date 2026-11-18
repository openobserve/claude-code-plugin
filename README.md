# OpenObserve plugin for Claude Code

Use [OpenObserve](https://openobserve.ai) from Claude Code: query logs, metrics and traces, and work with streams, dashboards and alerts through conversation.

## What's included

- **MCP server** (`openobserve`) — connects to the MCP endpoint built into your OpenObserve instance at `<base_url>/api/<org_id>/mcp`. Sign-in uses OAuth in your browser; no API key is stored by the plugin.
- **Skill** (`sql-query`) — a schema-first workflow for writing and validating SQL and PromQL against your streams.

## Install

```
/plugin marketplace add openobserve/claude-code-plugin
/plugin install openobserve@openobserve
```

You will be asked for two values:

| Option | Example | Notes |
|---|---|---|
| OpenObserve URL | `https://cloud.openobserve.ai` | Cloud: `cloud` (US), `eu1`, `ap1`. Self-hosted: your own host. No trailing slash. |
| Organization ID | `default` | The org identifier shown in the OpenObserve UI. |

Then run `/mcp`, pick `openobserve`, and complete the sign-in.

From a shell, the same install with the values supplied up front:

```
claude plugin marketplace add openobserve/claude-code-plugin
claude plugin install openobserve@openobserve \
  --config base_url=https://cloud.openobserve.ai --config org_id=<your-org-id>
```

Change the values later with `/plugin configure openobserve@openobserve`.

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
