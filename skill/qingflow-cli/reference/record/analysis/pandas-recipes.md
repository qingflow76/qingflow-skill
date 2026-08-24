# Pandas Recipes

Use Python to read returned CSV shards. Never paste raw CSV into the model context.

## Load All Shards

```python
import pandas as pd

files = [
    "/absolute/path/records-0001.csv",
    # include every record_access.files[].local_path
]

frames = [pd.read_csv(path, dtype=str, keep_default_na=False) for path in files]
df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# Columns are readable and field-id anchored, e.g. 项目状态__field_343283094.
fields = []  # optionally paste record_access.fields here if you need field-id metadata
field_by_id = {int(item["field_id"]): item for item in fields if "field_id" in item}
title_by_col = {item["column_name"]: item["title"] for item in fields if item.get("column_name")}
```

## Field Quality Profile

Run this before choosing final grouping dimensions.

```python
def field_quality(frame: pd.DataFrame, *, date_col: str | None = None) -> pd.DataFrame:
    rows = []
    for col in frame.columns:
        blank = frame[col].astype(str).eq("")
        item = {
            "column": col,
            "row_count": len(frame),
            "blank_count": int(blank.sum()),
            "blank_rate": float(blank.mean()) if len(frame) else 0.0,
            "distinct_count": int(frame[col].replace("", pd.NA).nunique(dropna=True)),
        }
        rows.append(item)
    quality = pd.DataFrame(rows).sort_values(["blank_rate", "distinct_count"], ascending=[False, False])
    if date_col and date_col in frame.columns:
        tmp = frame.copy()
        tmp["_period"] = pd.to_datetime(tmp[date_col], errors="coerce").dt.to_period("M").astype(str)
        period_quality = []
        for col in frame.columns:
            if col == date_col:
                continue
            by_period = tmp.groupby("_period")[col].apply(lambda s: float(s.astype(str).eq("").mean()))
            period_quality.append({"column": col, "max_period_blank_rate": float(by_period.max()) if len(by_period) else 0.0})
        quality = quality.merge(pd.DataFrame(period_quality), on="column", how="left")
    return quality
```

Quality gates:

- `blank_rate > 0.4`: do not use as the primary conclusion dimension.
- `max_period_blank_rate > 0.8`: do not use for period comparison.
- Very high `distinct_count` fields are usually identifiers or descriptions, not grouping dimensions.
- High-missing dimensions may still be reported as `已填写样本观察`.

## Column Selection

Prefer exact readable CSV columns. Use suffix matching only when you need to address a field id programmatically.

```python
def col_by_field_id(frame, field_id: int) -> str:
    suffix = f"__field_{field_id}"
    matches = [col for col in frame.columns if col.endswith(suffix)]
    if not matches:
        raise KeyError(f"field_id not in CSV: {field_id}")
    return matches[0]
```

## Count Distribution

```python
col = "项目状态__field_18"
quality = field_quality(df)
blank_rate = quality.loc[quality["column"].eq(col), "blank_rate"].iloc[0]
if blank_rate > 0.4:
    print(f"Use only as filled-sample observation: {col} blank_rate={blank_rate:.1%}")
dist = (
    df[col]
    .replace("", pd.NA)
    .fillna("未填写")
    .value_counts(dropna=False)
    .rename_axis("group")
    .reset_index(name="count")
)
dist["share"] = dist["count"] / dist["count"].sum()
```

## Numeric Aggregation

```python
group_col = "项目状态__field_18"
amount_col = "金额__field_25"
tmp = df.copy()
tmp[amount_col] = (
    tmp[amount_col]
    .str.replace(",", "", regex=False)
    .str.replace("￥", "", regex=False)
    .pipe(pd.to_numeric, errors="coerce")
)
summary = (
    tmp.groupby(group_col, dropna=False)[amount_col]
    .agg(count="count", total="sum", avg="mean")
    .reset_index()
    .sort_values("total", ascending=False)
)
```

## Date Trend

```python
date_col = "申请时间__field_2"
tmp = df.copy()
tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
tmp = tmp.dropna(subset=[date_col])
tmp["month"] = tmp[date_col].dt.to_period("M").astype(str)
trend = tmp.groupby("month").size().reset_index(name="count")
```

## Year-Over-Year Month Comparison

```python
date_col = "申请时间__field_2"
tmp = df.copy()
tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
tmp = tmp.dropna(subset=[date_col])
tmp["year"] = tmp[date_col].dt.year
tmp["month"] = tmp[date_col].dt.month
monthly = tmp.groupby(["year", "month"]).size().reset_index(name="count")
```

## Ratio

```python
numerator = len(df[df["项目状态__field_18"].eq("已成交")])
denominator = len(df)
ratio = numerator / denominator if denominator else None
```

Always report numerator and denominator.

## Multi-Select Cells

If values are serialized with delimiters, inspect samples first. For simple comma-separated values:

```python
col = "标签__field_30"
exploded = (
    df.assign(_value=df[col].str.split(","))
    .explode("_value")
)
exploded["_value"] = exploded["_value"].str.strip()
multi_dist = exploded["_value"].value_counts().reset_index(name="count")
```

## Business Mapping

```python
mapping = {
    "烈焰组": "北斗部门",
    "飓风组": "北斗部门",
}
department_col = "部门__field_40"
df["department_normalized"] = df[department_col].replace(mapping)
```

State the mapping in the final answer.
