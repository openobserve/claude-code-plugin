# OpenObserve SQL Functions

## Full-text search
- `match_all('keyword')` - Searches inverted index fields (case-insensitive)
- `match_all_raw('keyword')` - Searches all fields (case-sensitive)
- `str_match(field, 'keyword')` - Filter keyword in field
- `re_match(field, 'pattern')` - Regex match (use Rust regex syntax)

## Array functions
- `arrcount(field)` - Count array elements
- `arrindex(field, start, end)` - Select range (end inclusive)
- `arrsort(field)` - Sort array ascending
- `arrjoin(field, delimiter)` - Join with delimiter
- `arrzip(field1, field2, delimiter)` - Zip arrays
- `cast_to_arr(field)` - Convert JSON array string to native array
- `spath(json_field, 'path.to.value')` - Extract from JSON

## Aggregation
- `histogram(field, 'interval')` - Time bucketing (interval: second/minute/hour/day/week)
- `histogram(field, num)` - Auto-bucket into num buckets
- Standard: `COUNT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()`, `APPROX_PERCENTILE_CONT()`

## Time operations
- `DATE_TRUNC('unit', timestamp)` - Truncate to unit (hour/day/week/month)
- `EXTRACT(unit FROM timestamp)` - Extract component (hour/minute/day)

## String extraction
- `regexp_match(field, 'pattern')` - Returns array of capture group matches
- `array_extract(regexp_match(...), index)` - Get specific capture group (index starts at 1)
- `re_matches(field, 'pattern')` - Returns list of all matching substrings

**IMPORTANT - Functions that DO NOT exist:**
- `regexp_extract()` — Does NOT exist. Use `array_extract(regexp_match(field, 'pattern'), 1)` instead.
- `regexp_replace()` — Does NOT exist.
- `regexp_like()` — Does NOT exist. Use `re_match(field, 'pattern')` instead.

Example - extract a value from a string field:
```sql
-- Extract the status code from a message like "request finished status=502 in 31ms"
SELECT array_extract(regexp_match(message, 'status=(\d+)'), 1) AS status_code,
       COUNT(_timestamp) AS requests
FROM "app_logs"
GROUP BY status_code
```

Full DataFusion SQL reference: https://datafusion.apache.org/user-guide/sql/index.html
