# Confidence Reporting

## Full Conclusion Gate

Use `全量可信结论` only when:

- `record_browse_schema_get` was used
- data came from `record_access`
- all returned CSV shards were read in Python
- `record_access.complete=true`
- `record_access.truncated=false`
- `record_access.safe_for_final_conclusion=true`
- metric definitions are complete
- denominator exists for every ratio
- time fields and date ranges are explicit
- primary grouping dimensions pass field-quality gates

## Initial Observation Gate

Use `初步观察` when:

- `record_access.status=needs_scope`
- `record_access.status=partial`
- `record_access.complete=false`
- `record_access.truncated=true`
- `record_access.safe_for_final_conclusion=false`
- evidence came from `record_list`
- scope or saved view filter is unverified

## Anti-Mixing Rule

Do not combine full CSV-derived totals and sample-only rows in one sentence.

Correct split:

- full totals/distributions: `全量可信结论`
- illustrative examples: `样本观察`

## Semantic Gate

Even with `safe_for_final_conclusion=true`, downgrade if:

- metric definition is incomplete
- denominator was not queried
- conclusion mentions trend but no time field was used
- conclusion mentions volume but no count was computed
- grouping depends on unconfirmed business aliases
- custom view scope is not verified
- primary grouping field has high missingness or poor period coverage

## Partial Disclosure

If only part of the user request is complete:

- say which parts are complete
- say which parts are unresolved
- do not collapse into one all-clear conclusion

## Compact Disclosure Template

```text
可信度：全量可信 / 初步观察
数据完整性：complete=..., truncated=..., safe_for_final_conclusion=...
字段质量：primary dimension blank_rate=..., period coverage=...
取数字段：...
时间范围：...
业务口径：...
限制：...
```
