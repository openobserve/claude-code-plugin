---
name: spl-conversion
description: >
  SPL (Splunk Processing Language) to SQL conversion for OpenObserve. Use when
  the user asks to convert SPL queries to SQL, migrate Splunk searches, or
  translate SPL syntax. Covers key command mappings, time filter handling, and
  the mandatory post-conversion validation checklist.
---

# SPL to SQL Conversion [+ VALIDATION]

## Conversion Rules

CRITICAL: When converting SPL to SQL, you MUST validate the resulting SQL

Key Mappings:

| SPL | SQL/DataFusion | Notes |
|-----|----------------|-------|
| `earliest=-1h latest=now` | (not in the SQL) | Pass the range as `start_time` / `end_time`, never as a `WHERE` clause |
| `search field=value` | `WHERE field = 'value'` | Basic filtering |
| `fields a, b, c` | `SELECT a, b, c` | Field selection |
| `stats count by host` | `SELECT host, COUNT(_timestamp) as count FROM ... GROUP BY host` | Aggregation |
| `sort -count` | `ORDER BY count DESC` | Sorting |
| `eval new = field1 + field2` | `field1 + field2 as new` | Numeric calculated fields |
| `eval new = field1 . field2` | `CONCAT(field1, field2) as new` | String concatenation |
| `rex field=msg "(?<code>\d+)"` | `array_extract(regexp_match(msg, '(\d+)'), 1) as code` | Regex extraction (`regexp_extract` does not exist) |
| `bucket _time span=5m` | `histogram(_timestamp, '5 minutes')` | Time bucketing (not filtering!) |

## Validation Checklist for SPL Conversion

After converting SPL to SQL, verify ALL items:
- [ ] Time range filters removed? (earliest/latest not converted)
- [ ] Field names verified against schema?
- [ ] SQL run with `SearchSQL` over a short time range without error? (see the `sql-query` skill)

If any checkbox is unchecked: STOP and complete that step

See `references/spl-example.md` for a complete conversion example, and the `sql-query` skill for
OpenObserve SQL functions and the schema-first workflow.
