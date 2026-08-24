# Analysis Gotchas

## Do Not Skip Schema

Correct path:

1. `app_get`
2. `record_browse_schema_get`
3. `record_access`
4. Python

`record_browse_schema_get` returns readable fields for the selected view. Missing fields are permission or view-scope boundaries, not invitations to guess hidden ids.

## Do Not Use Export For Analysis

Export tools are for user-requested files. Analysis uses `record_access` because it returns structured completeness and compact field metadata.

## Do Not Treat `record_list` As Full Data

`record_list` is sample/browse only. It can be capped and should not justify:

- average
- share
- ranking
- trend
- regional distribution
- "all data" insights

## Do Not Control Paging

`record_access` owns paging internally.

Do not invent:

- `page`
- `page_size`
- `limit`
- `requested_pages`
- `scan_max_pages`
- `max_rows`
- `timeout`

## Do Not Print Raw CSV

Read CSV files with pandas. Summarize computed results, not raw rows.

## Do Not Rename Source Files

CSV columns are directly readable and field-id anchored: `record_id`, `<字段标题>__field_<id>`. Use those columns directly in pandas.

## Do Not Trust Sparse Dimensions

Before final grouping, run a field-quality profile. If the selected field is mostly blank, say so and downgrade the claim.

Rules of thumb:

- Overall blank rate above 40%: not a primary conclusion dimension.
- Any compared period blank rate above 80%: do not use that field for period comparison.
- A sparse field can support only `已填写样本观察`.

If the user asks for a semantic field such as `板块`, test nearby candidates like product, platform, module, stage, source, owner, or department before concluding.

## Do Not Hide Incomplete Access

If `needs_scope`, no CSV exists. Ask for a time/business scope.

If `partial`, use only subset wording and avoid full-population claims.

If field meaning is ambiguous, ask the user to confirm from a short list.

## Do Not Guess Metrics

Before fetching data, decide whether the request needs count, sum, average, distinct count, ratio, ranking, trend, or comparison.

## Do Not Call A Ratio Without Denominator

For penetration, conversion, or share:

1. define numerator
2. define denominator
3. query compatible source data
4. compute in Python
5. report numerator and denominator

## Normalize Relative Dates

Convert relative phrases into exact ranges before `record_access`.

- `今年5月` -> exact May 1 to May 31 in the current year
- `去年同期` -> same date range in previous year
- `最近30天` -> exact rolling start/end dates
