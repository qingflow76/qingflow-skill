# Analysis Patterns

## Canonical Sequence

1. `app_get`
2. `record_browse_schema_get`
3. decide metric intent
4. choose `record_access.columns / where / order_by`
5. `record_access`
6. Python over every returned CSV shard
7. optional `record_list` or `record_get` only for sample/detail verification

Metric intent must be one of:

- `count`
- `sum`
- `avg`
- `distinct_count`
- ratio with numerator and denominator
- sorted ranking
- time trend
- period comparison

## Distribution

1. Fetch grouping field and filter fields.
2. Run the field-quality profile for the grouping field.
3. If the field passes quality gates, group by the readable field-id anchored column such as `项目状态__field_343283094`.
4. Count rows and calculate share from the sum of counts.
5. Report top groups plus total row count.

If the grouping field is ambiguous, ask the user to choose from a short candidate list.

## Dimension Selection

When the user asks for a semantic bucket such as `板块`, `模块`, `业务线`, or `来源`, inspect candidate fields and choose the most reliable one:

1. Match schema titles to the user's wording.
2. Fetch candidate fields together if they are cheap.
3. Profile `blank_rate`, period coverage, and distinct count.
4. Prefer the candidate with clear semantics and usable coverage.
5. If the literal field is sparse, downgrade it to `已填写样本观察` and use the nearest reliable fallback for the main conclusion.

Example: if `缺陷所属模块` is mostly empty but `缺陷所属平台` and `所属产品` are complete, use platform/product for the main conclusion and state that module-level analysis is limited.

Quality gates:

- Overall `blank_rate > 0.4`: not a primary conclusion dimension.
- Any compared period `blank_rate > 0.8`: not valid for period comparison.
- High-cardinality description/id fields are not dimensions unless the user explicitly asks for record-level ranking.

## Ratio / Conversion / Penetration

1. Define numerator and denominator in plain language.
2. Fetch both populations with compatible scope.
3. Compute ratio in Python.
4. Report `numerator / denominator = percentage`.

If denominator is missing or scope differs, do not call the result a rate.

## Average / Sum

1. Fetch grouping field and numeric metric field.
2. Convert the metric column with `pd.to_numeric(errors="coerce")`.
3. Report count, sum, and average together when useful.
4. State how blanks/non-numeric values were handled if material.

## Ranking

1. Build the metric in Python.
2. Sort explicitly.
3. Report Top N with metric values.
4. Do not infer ranking from unsorted sample rows.

## Trend

1. Choose a date/time field from `suggested_time_fields`.
2. Convert relative phrases into exact date ranges.
3. Fetch the date field and metrics.
4. Bucket in pandas by day/week/month/quarter/year.
5. Report both absolute values and changes.

## Same-Period Comparison

For `今年5月 vs 去年5月`:

1. Use the same date field for both periods.
2. Fetch the full combined date range or two separate compatible ranges.
3. Apply identical business filters.
4. Compute absolute delta and percentage delta.
5. State both periods explicitly.

## Sample Inspection

Use `record_list` only after the aggregate result is complete, and only for:

- representative examples
- checking surprising categories
- manually inspecting records behind a bucket

Never use `record_list` alone for final averages, shares, rankings, trends, or distributions.

## Ambiguous Field Recovery

If the exact field is unclear:

1. inspect `record_browse_schema_get.fields`
2. use titles and suggested fields
3. if one candidate is clearly dominant, proceed
4. otherwise ask the user to confirm

Do not retry tools with guessed field names.
