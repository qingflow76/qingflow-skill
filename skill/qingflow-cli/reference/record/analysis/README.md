# Qingflow CLI Record Analysis

Use this section for final statistical conclusions: counts, distributions, ratios, averages, rankings, trends, comparisons, and analysis reports.

Default path, every time:

```text
app get -> record schema browse(view_id=...) -> record access -> Python/pandas -> final answer
```

Use the CLI entry:

```bash
qingflow record --help
qingflow record access --help
qingflow record access --app-key APP_KEY --view-id VIEW_ID --columns-file columns.json --where-file where.json --order-by-file order_by.json --json
```

The CLI command is under the `record` command group, so the discovery path is: first inspect `qingflow record --help`, then inspect `qingflow record access --help`.

## Hard Rules

- Never start analysis from `record_list`, export, QingBI, or guessed field ids.
- Never conclude `record_access` is unavailable just because it is not visible as a top-level MCP tool; check the CLI path `qingflow record access`.
- Never call `record access` before `record schema browse`.
- Use only field ids returned by `record schema browse`.
- If `app_get.accessible_views[].analysis_supported=false`, do not use that view for `record_access`.
- Prefer an explicit time range or business filter. If the user gives none and the table may be large, ask for scope or use a clearly provided month/quarter/year.
- Read every CSV shard in `record_access.files[].local_path` with Python. Do not print raw CSV or load raw rows into model context.
- Before final analysis, run a field-quality profile in pandas: row count, null rate, distinct count, and period coverage for candidate grouping fields.
- Do not use a high-missing field as the main conclusion dimension. If a candidate dimension is sparse, downgrade it to an `已填写样本观察` and choose a cleaner semantic fallback when available.
- Full final conclusions require `record_access.complete=true` and `record_access.safe_for_final_conclusion=true`.
- `record_list` is only for sample inspection after the aggregate result is understood.
- `record_get` is only for single-record detail verification, logs, references, images, or readable attachments. Read images from `media_assets.items[].local_path`; read documents/tables from `file_assets.items[].local_path` and `extraction.text_path`.
- `record_export_direct` is only for explicit export/download/Excel requests.
- `chart_get` / QingBI is only for user-provided report URLs or chart ids.

## Tool Selection

| Need | Tool |
|---|---|
| Batch analysis, statistics, comparison, report | `record access -> Python` |
| Browse a few example rows | `record_list` |
| Inspect one record, logs, references, images, attachments | `record_get` |
| User asks to export/download/Excel | `record_export_direct` |
| User gives report URL or chart id | `chart_get` |
| Todo/workflow task actions | `reference/task/QINGFLOW_CLI_TASK_CONTEXT_WORKFLOW.md` |

## Standard Procedure

1. Run `app get` and choose a table-style `view_id` from `accessible_views`.
2. Run `record schema browse --app-key APP_KEY --view-id VIEW_ID`.
3. Decide metric intent before fetching data: `count`, `sum`, `avg`, `distinct_count`, ratio, ranking, trend, or comparison.
4. Choose minimal `record_access.columns`, plus `where` and `order_by`.
5. Run `qingflow record access`.
6. Read all returned CSV files in Python; use `fields[]` only when field-id metadata is needed.
7. Run field-quality checks for all candidate dimensions.
8. Compute results in pandas.
9. Report numbers with scope, field choices, field-quality caveats, completeness, and business assumptions.

Use field-id DSLs only:

```json
{
  "app_key": "APP_KEY",
  "view_id": "system:all",
  "columns": [{ "field_id": 2 }, { "field_id": 18 }],
  "where": [{ "field_id": 2, "op": "between", "value": ["2026-05-01", "2026-05-31"] }],
  "order_by": [{ "field_id": 2, "direction": "asc" }]
}
```

Never pass `page`, `page_size`, `limit`, `max_rows`, `timeout`, or `profile` to `record_access`.

CSV columns are already readable and field-id anchored, for example `项目状态__field_343283094`. Do not expect separate `schema.json` or `README.md` files.

For CLI use, write JSON argument files instead of embedding large JSON in shell text:

```bash
qingflow record access \
  --app-key APP_KEY \
  --view-id system:all \
  --columns-file columns.json \
  --where-file where.json \
  --order-by-file order_by.json \
  --json
```

## Status Handling

Read `record_access.status` before reading files or writing conclusions.

- `status=success`, `complete=true`, `safe_for_final_conclusion=true`: full-scope answer is allowed.
- `status=needs_scope`: no CSV was written. Ask for a time/business range or retry with a user-provided period using `scope.suggested_time_fields`.
- `status=partial`: read returned files only as a subset. Do not give a full-population conclusion.
- `complete=false`, `truncated=true`, or `safe_for_final_conclusion=false`: answer as `初步观察` or ask for a narrower scope.

## Business Context

If the question mentions department, team, region, owner group, stage, product line, or a named business scope, check whether aliases or child scopes matter before concluding. Use explicit mappings provided by the user or local context; otherwise ask a short clarification.

Example: if `烈焰组` and `飓风组` are sub-departments of `北斗部门`, apply that mapping in Python and state it in the answer.

## Output Shape

Default to:

1. `结论`
2. `关键数据`
3. `口径与范围`
4. `可信度 / 限制`

Concrete numbers are mandatory. Ratios require both numerator and denominator. Trends require a time field and explicit date range. Rankings must come from a sorted pandas result.
If a requested dimension has poor quality, say so explicitly and provide the nearest reliable fallback dimension, for example platform or product instead of a mostly empty module field.

## References

Load only what is needed:

- Data access status machine: [references/data-access-playbook.md](./data-access-playbook.md)
- Python/pandas templates: [references/pandas-recipes.md](./pandas-recipes.md)
- Analysis patterns: [references/analysis-patterns.md](./analysis-patterns.md)
- Business mappings and scope: [references/business-context.md](./business-context.md)
- Confidence and final wording: [references/confidence-reporting.md](./confidence-reporting.md)
- Common mistakes: [references/analysis-gotchas.md](./analysis-gotchas.md)
- Report templates: [references/report-format.md](./report-format.md)

## Feedback Escalation

If the desired analysis cannot be completed because of missing capability, unsupported data shape, or an awkward workflow after reasonable attempts, summarize the exact gap and ask whether to submit product feedback. Only after explicit user confirmation, call `feedback_submit`.
