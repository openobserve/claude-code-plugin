# SPL to SQL Conversion Example

SPL:
```
index=production source=app.log error
| stats count by host, status
| sort -count
```

SQL (converted + validated):
```sql
SELECT host as x_axis_1, status, COUNT(_timestamp) as count
FROM "production"
WHERE source = 'app.log' AND match_all('error')
GROUP BY host, status
ORDER BY count DESC
```

Notes:
- Removed index (stream is "production")
- `search` -> `WHERE` clause
- `stats count by` -> `SELECT ... GROUP BY`
- `sort -count` -> `ORDER BY count DESC`
- No time filters in the SQL (earliest/latest become `start_time` / `end_time`)
