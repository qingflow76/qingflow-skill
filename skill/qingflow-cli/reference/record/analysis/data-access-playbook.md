# Data Access Playbook

This file is the operational state machine for `record_access`.

## Required Sequence

1. `app_get`
2. choose `view_id` from `accessible_views`
3. `record_browse_schema_get(app_key, view_id)`
4. build `record_access.columns / where / order_by` from field ids
5. run `record_access`
6. read every CSV shard with Python

Do not call `record_access` with field titles, guessed ids, page controls, row limits, or profile.
CSV columns are readable and field-id anchored, for example `项目状态__field_343283094`; do not look for extra `schema.json` or README files.

## Finding `record_access`

`record_access` can be available as an MCP tool or as a CLI subcommand. If the MCP surface does not show a top-level `record_access` tool, look under the Qingflow CLI record group before choosing any other path:

```bash
qingflow record --help
qingflow record access --help
```

The CLI call is:

```bash
qingflow record access \
  --app-key APP_KEY \
  --view-id VIEW_ID \
  --columns-file columns.json \
  --where-file where.json \
  --order-by-file order_by.json \
  --json
```

This is the same analysis path: it writes CSV shards and metadata for Python. Do not replace it with list browsing, export, QingBI, or aggregate helpers just because the MCP tool is not visible.

## Request Patterns

### Count or distribution

Fetch the grouping field and any time/business filter field.

```json
{
  "app_key": "APP_KEY",
  "view_id": "system:all",
  "columns": [{ "field_id": 18 }],
  "where": [{ "field_id": 2, "op": "between", "value": ["2026-05-01", "2026-05-31"] }],
  "order_by": []
}
```

### Trend

Fetch the date/time field plus metric fields.

```json
{
  "app_key": "APP_KEY",
  "view_id": "system:all",
  "columns": [{ "field_id": 2 }, { "field_id": 18 }],
  "where": [{ "field_id": 2, "op": "between", "value": ["2026-01-01", "2026-12-31"] }],
  "order_by": [{ "field_id": 2, "direction": "asc" }]
}
```

### Ratio

If numerator and denominator use different filters, run separate `record_access` calls. Only compute the ratio after both source datasets are complete and compatible.

## Status Decisions

| Status | Meaning | Agent action |
|---|---|---|
| `success` + `safe_for_final_conclusion=true` | Full retrieved scope is reliable | Give final conclusion |
| `needs_scope` | Tool refused large unbounded scan, no CSV | Ask for scope or retry with explicit period/business filter |
| `partial` | Some CSV files written, but not full data | Give only subset observation |
| `complete=false` | Not all requested data is available | Do not present full-population conclusion |
| `truncated=true` | Tool had to stop before full scope | Disclose and narrow scope |

## `needs_scope` Recovery

Use the returned `scope` object:

- `reported_total`: explain why scope is needed
- `suggested_time_fields`: choose likely date fields
- `recommended_where_examples`: reuse if they match the user request

If the user already provided a concrete month/quarter/year, retry with that period. If no business boundary is available, ask one short clarification.

## `partial` Recovery

You may read the files, but must label output as partial:

- say which files/rows were analyzed
- do not use `全部`, `所有`, `整体`, or `全量`
- suggest narrowing time or business scope before final conclusion

## View Scope

For custom views, the result is scoped to that saved view. If `verification.view_filter_verified=false`, disclose that the saved-filter scope could not be fully verified.

For board/gantt views, switch to a table-style view or `system:all` plus explicit filters.
