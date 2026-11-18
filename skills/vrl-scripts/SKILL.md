---
name: vrl-scripts
description: >
  VRL (Vector Remap Language) script generation for OpenObserve. Use when the
  user asks to write, debug, or optimize VRL scripts for log parsing, field
  extraction, enrichment, or data transformation. Covers error handling patterns,
  validation process, common functions, and response formatting rules.
---

# VRL Script Generation [+ VALIDATION]

## Validation (mandatory)

Validate every script before returning it or saving it as a function. Use the `testFunction` tool
of the OpenObserve MCP server (find it with `tool_search("test function")` if it is not exposed
directly) with:

- `org_id`
- `request_body.function`: the VRL source
- `request_body.events`: one or more sample events, ideally real records from the target stream

Read the result: fix any compile error and test again, and check that the transformed output has
the fields you intended. Stop after three failed attempts and show the user the error.

If no OpenObserve tools are available, say that the script is unvalidated, or run the `setup`
skill first.

## CRITICAL: Fallible Function Rule (E103 Prevention)

In VRL, event fields like `.log`, `.message`, `.field` have type `any` — NOT `string`.
Functions expecting `string` args (replace, split, parse_regex, parse_grok, etc.) become FALLIBLE when passed `any`-typed fields.

**DEFAULT RULE: ALWAYS use `!` (abort-on-error) suffix on functions that take event fields as arguments.**

```
WRONG:  .log = replace(.log, r'pattern', "replacement")
RIGHT:  .log = replace!(.log, r'pattern', "replacement")

WRONG:  .tokens = split(.field, ".")
RIGHT:  .tokens = split!(.field, ".")

WRONG:  parsed = parse_regex(.message, pattern)
RIGHT:  parsed, err = parse_regex(.message, pattern)
        OR: parsed = parse_regex!(.message, pattern)
```

This applies to ALL functions that receive event fields: `replace`, `split`, `join`, `parse_regex`,
`to_string`, `to_int`, `to_float`, `to_bool`, `to_timestamp`, `contains`, `starts_with`,
`ends_with`, `slice`, `truncate`, `upcase`, `downcase`, `strip_whitespace`, `parse_json`, etc.

Two valid patterns:
1. `result, err = fn(args)` — handle error explicitly (**PREFERRED** — makes debugging easier)
2. `result = fn!(args)` — abort on error (only for simple one-liners where failure is unrecoverable)

**PREFER pattern 1 (tuple return + err check) over pattern 2 (`!`).** When a VRL script fails silently
or drops events, `err` values make it possible to diagnose what went wrong. The `!` suffix aborts
the entire script on error with no context.

```
GOOD (debuggable):
  .log, err = replace(.log, r'pattern', "replacement")
  if err != null {
    .vrl_error = err
  }

OK (simple cases only):
  .log = replace!(.log, r'pattern', "replacement")
```

## Additional Error Handling

| Error Type | Wrong | Correct |
|------------|-------|---------|
| Null Access | `.status = .parsed.status` | `if exists(.parsed.status) { .status = .parsed.status }` |
| Regex Pattern | `pattern = "\\d+"` | `pattern = r'\d+'` |

Rules:
- Regex patterns: Use raw strings `r'pattern'`
- Always check `exists()` before accessing nested fields

Common validation errors:

| Code | Description | Fix |
|------|-------------|-----|
| E103 | Unhandled fallible assignment | Add error handling: `result, err = fn()` or `fn!()` |
| E103 | Type mismatch (`any` vs `string`) | Check `exists()` before using the field, or convert it explicitly |
| E103 | Null field access | Add a null check with `exists()` |

## Common VRL Functions (always handle errors with event fields)

- `parsed, err = parse_grok()` - Parse with Grok patterns (preferred for structured log formats like syslog, apache, custom bracketed formats)
- `parsed, err = parse_regex()` - Extract with regex (use when Grok patterns don't fit)
- `.field, err = replace()` - String replacement (most common source of E103)
- `.tokens, err = split()` / `join()` - String ops
- `.val, err = to_string()` / `to_int()` / `to_float()` - Type conversions
- `.result, err = contains()` / `starts_with()` / `ends_with()` - String checks
- `.data, err = parse_json()` - JSON parsing
- `exists()` - Check if field exists (infallible, no error handling needed)
- `del()` - Remove fields (infallible, no error handling needed)
- `.flat, err = flatten()` - Handle nested structures

## Response format

- Put the script in a single ```vrl code block.
- Explain the script with `#` comments inside the code, not with headings or bold labels above it.
- Add a brief explanation after the code block only if it is needed.

See `references/vrl-example.md` for a complete VRL parsing example.
