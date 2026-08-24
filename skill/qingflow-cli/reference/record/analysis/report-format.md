# Report Format

Use this for user-facing analysis reports.

## Short Answer

```text
结论：
- ...

关键数据：
- 指标 A：...
- 指标 B：...

口径与范围：
- 应用 / 视图：...
- 时间范围：...
- 字段：...
- 字段质量：...
- 业务映射：...
- 数据完整性：...

限制：
- ...
```

## Detailed Report

```text
1. 分析范围
   - app / view
   - time range
   - filters
   - rows analyzed

2. 核心结论
   - concrete numbers first
   - no vague adjectives without numbers

3. 分项数据
   - distribution / trend / ranking tables
   - percentages with numerator and denominator

4. 解释与建议
   - separate facts from hypotheses

5. 口径与可信度
   - fields used
   - field-quality gates and downgraded dimensions
   - mapping rules
   - completeness
   - partial or unverified scope warnings
```

## Wording Rules

- Use `全量可信结论` only when the accessed scope is complete and safe.
- Use `初步观察` for partial or unverified data.
- Do not say `全部`, `所有`, `整体`, or `完整` when `safe_for_final_conclusion=false`.
- For ratios, always show `numerator / denominator`.
- For comparisons, show both periods' absolute values and the delta.

## Comparison Template

```text
今年5月 vs 去年5月：
- 记录数：今年 X，去年 Y，变化 +Z（+P%）
- 金额：今年 X，去年 Y，变化 +Z（+P%）
- 结构变化：...

口径：
- 时间字段：...
- 部门字段：...
- 部门映射：...
- 数据完整性：...
```
