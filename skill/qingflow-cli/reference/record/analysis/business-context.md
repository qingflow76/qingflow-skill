# Business Context

Use this when analysis depends on organization, aliases, ownership, stage semantics, or user-provided business definitions.

## When To Check Context

Check for business context when the request mentions:

- department / team / group / region
- owner / assignee / sales rep / partner
- stage / status / funnel / conversion
- product line / business line
- same-period comparison
- "北斗部门", "SMB", "伙伴", or any named internal scope

## Mapping Rules

Use explicit mappings in this order:

1. the user's message in the current thread
2. attached or local business context files
3. schema-visible fields and sample records
4. short clarification to the user

Do not infer hidden org hierarchy from memory. If the mapping changes the denominator or grouping, state it in the final answer.

Example:

```python
dept_map = {
    "烈焰组": "北斗部门",
    "飓风组": "北斗部门",
}
df["部门口径"] = df["field_40"].replace(dept_map)
```

Final wording:

```text
部门口径：将「烈焰组」「飓风组」合并计入「北斗部门」。
```

## Ratio Definitions

Before computing rates, define:

- numerator
- denominator
- time range
- grouping dimension
- exclusions

If any part is ambiguous, ask. Do not rename a count as a rate.

## Time Scope

Normalize relative dates to exact dates before calling `record_access`.

Examples:

- `今年5月` -> `2026-05-01` to `2026-05-31` when current year is 2026
- `去年同期` -> same month range in the previous year
- `最近一个完整自然月` -> previous calendar month, not the last 30 days

## Cross-App Reconciliation

If the analysis needs multiple apps:

1. run the standard sequence per app
2. keep each dataset's scope and completeness separately
3. join in Python only on explicit ids or trusted business keys
4. disclose join keys and unmatched records

If no reliable key exists, report the gap instead of forcing a join.
