---
name: pipeline-creation
description: >
  Pipeline creation and editing for OpenObserve. Use when the user asks to
  create, edit, or design data pipelines with input/output streams, transform
  functions, and routing conditions. Covers node layout, node types, edge
  connections, and the pipeline JSON structure.
---

# Pipeline Creation Workflow

Tools named here (for example `createPipeline`, `createFunction`) belong to the OpenObserve MCP server.
Depending on the server version they are exposed directly or are found with
`tool_search` and run with `tools_call`; use whichever form is available. If no
OpenObserve tools are available, run the `setup` skill first.

## Node Layout (Vertical)

Always use top-to-bottom layout:
```
Input (top):     y = 100,  x = 100
Transform 1:     y = 250,  x = 100  (100 + 150 spacing)
Transform 2:     y = 400,  x = 100  (250 + 150 spacing)
Output (bottom): y = 550,  x = 100  (400 + 150 spacing)
```

Rules:
- Vertical spacing: 150px minimum between nodes
- Horizontal spacing: 250px for parallel branches
- Single column: x = 100 for all nodes
- Start: y = 100

## Pipeline Creation Steps

1. Understand data flow (source -> transforms -> destination)
2. Verify prerequisites:
   - List streams: source and destination exist?
   - List functions: transform functions exist?
   - If functions missing: create them first (`createFunction`), after validating the VRL with
     `testFunction` (see the `vrl-scripts` skill)
3. Design nodes (input, processing, output)
4. Create edges (connect nodes)
5. Check the current `createPipeline` input schema (`tool_search("create pipeline")`), then call it
   with `org_id` and the pipeline as `request_body`
6. Tell the user what was created: pipeline name, source and destination streams, and functions used

## Node Types

| Node Type | io_type | data.node_type | Purpose |
|-----------|---------|----------------|---------|
| Stream (source) | "input" | "stream" | Data source |
| Function | "default" | "function" | Transform/parse |
| Condition | "default" | "condition" | Filter/route (set `"version": 2` in the node data) |
| Stream (dest) | "output" | "stream" | Data destination |

Edge ids use the form `e<source_id>-<target_id>`.

A pipeline changes how data is ingested. Before creating or editing one, state the source stream,
the destination stream and the transforms you are about to apply, and make sure the destination is
not an existing stream the user did not name.

See `references/pipeline-example.md` for the complete pipeline JSON structure.
