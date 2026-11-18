---
name: setup
description: >
  Connect Claude Code to an OpenObserve instance by registering its MCP server.
  Use when the user asks to set up, connect or configure OpenObserve, or when a
  request needs OpenObserve data (logs, metrics, traces, streams, dashboards,
  alerts) and no OpenObserve MCP tools are available in this session.
---

# Connect OpenObserve

OpenObserve serves an MCP endpoint per organization at:

```
<base_url>/api/<org_id>/mcp
```

The address differs for every user (cloud region or self-hosted host, plus the
organization), so this plugin does not ship a fixed server. This skill registers
the user's own endpoint with Claude Code under the name `openobserve`.

## 1. Check whether it is already connected

Run `claude mcp list` and look for a server whose URL ends in `/api/<org>/mcp`.

- Connected: tell the user it is already set up and continue with their request.
- Listed but "Needs authentication": skip to step 5.
- Not listed: continue.

## 2. Ask for the instance and organization

Ask the user which OpenObserve instance and organization to connect. Accept any
of these forms:

- A cloud region:

  | Region | Base URL |
  |--------|----------|
  | US | `https://cloud.openobserve.ai` |
  | EU | `https://eu1.openobserve.ai` |
  | Asia Pacific | `https://ap1.openobserve.ai` |

- A self-hosted base URL, for example `https://o2.example.com`.
- Any URL copied from the OpenObserve web UI. Take the scheme and host as the
  base URL and the `org_identifier` query parameter as the organization ID.

The organization ID is the `org_identifier` value shown in the browser address
bar of the OpenObserve UI. Self-hosted single-organization installs usually use
`default`. If the user gave only one of the two values, ask for the other. Do
not guess an organization ID.

Remove any trailing slash from the base URL. Require `https://` unless the user
confirms a plain-HTTP internal host.

## 3. Check the endpoint

Build `<base_url>/api/<org_id>/mcp` and probe it without credentials, printing
the response headers:

```
curl -s -o /dev/null -m 15 -D - -X POST \
  -H 'Content-Type: application/json' -d '{}' '<endpoint>'
```

- `401` with a `www-authenticate: Bearer resource_metadata=...` header: this is
  an OpenObserve MCP endpoint with browser sign-in. Continue.
- `401` without that header: the host answers, but this is either not the MCP
  path or an instance without OAuth sign-in. Re-check the URL; if it is right,
  the instance needs a static credential (see step 4).
- Any other status: the host is probably not an OpenObserve instance, or its
  version or edition does not include the MCP server. Ask the user to check.
- Connection error or timeout: the host is wrong or not reachable from this
  machine (VPN, private network). Report it and stop.

The probe cannot confirm the organization ID: an unknown organization answers
the same way and only fails after sign-in. If tools return permission errors
later, the organization ID is the first thing to re-check.

## 4. Register the server

Show the user the endpoint you are about to add, then run:

```
claude mcp add --transport http --scope user openobserve '<endpoint>'
```

Use `--scope user` so it is available in every project, unless the user asks
for it to be limited to the current project.

If a server named `openobserve` already exists with a different URL, ask before
replacing it, or offer a second name such as `openobserve-eu`.

Sign-in uses OAuth in the browser. Do not ask the user for a password, token or
API key, and never write one into a command you run. If their instance has no
single sign-on and needs a static credential, give them the command to run
themselves, with a placeholder:

```
claude mcp add --transport http --scope user openobserve '<endpoint>' \
  --header "Authorization: Basic <base64 of email:token>"
```

## 5. Tell the user how to finish

Tell the user to:

1. Run `/mcp` in Claude Code and select `openobserve`.
2. Choose the authentication option and sign in in the browser.
3. Restart Claude Code if the server does not appear in `/mcp`.

After that, the OpenObserve tools are available and the `sql-query` skill can be
used to write and validate queries.

## Permissions

The server acts with the signed-in user's permissions and is not read-only: it
includes tools that create, update and delete dashboards, alerts and other
resources. Mention this once when setup completes.
