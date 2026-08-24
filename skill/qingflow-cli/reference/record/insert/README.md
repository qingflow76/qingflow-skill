# Qingflow CLI Record Insert

## Default Path

`record schema insert -> record insert --items-file -> optional record get/readback`

Default to batch-shaped insert. A single new record is `items` with one row.

## Core Tools

- `qingflow record schema insert`
- `qingflow record insert --items-file`
- `qingflow record member-candidates`
- `qingflow record department-candidates`
- file upload command when attachments are required

## Working Rules

1. Start with `record schema insert`
2. Read `required_fields`, `optional_fields`, `runtime_linked_required_fields`, and `payload_template`
3. Inside every field bucket, read field-level `linkage` first when present; it is the canonical static hint for linked visibility, reference-driven auto fill, or formula-driven fields
4. Inside `optional_fields`, pay special attention to any field with `may_become_required=true`; these are writable fields that can become required when linked visibility or option-driven rules activate
5. Build `items` as `[{"fields": {...}}]`, where each `fields` map uses field titles from the insert schema
6. Treat `runtime_linked_required_fields` as required-but-not-directly-writable runtime/upstream dependencies, not as fields to hand-fill blindly
7. For `linkage.kind=logic_visibility`, read `sources` as upstream trigger fields and treat `role=manual_input_after_activation` as "fill this only after the upstream condition is satisfied"
8. For `linkage.kind=reference_fill`, prefer filling the source field first; treat target fields with `role=auto_fill_preferred` or `auto_fill_only` as reference-driven outputs rather than blind manual inputs
9. For `linkage.kind=formula_fill`, treat the field as formula/default-auto-fill driven unless the user explicitly asks to override it and the field is still writable
10. If insert succeeds and single-record detail/readback matters, prefer `record get`; use `record list` only for batch row-shaped normalized readback
11. Keep subtable payloads under the parent field as a row array
12. Member / department / relation fields may accept natural strings directly, such as `"张三"`, `"直销部"`, or `"海军军医大学"`; do not pre-query ids by default
13. If the write returns `status="needs_confirmation"`, stop and surface the candidates
14. Retry failed rows only with explicit ids / objects after the user confirms
15. Keep `verify_write=true` for production inserts
16. If post-write detail context matters, read `record get` fields, `media_assets.items[].local_path`, `file_assets.items[].local_path`, `file_assets.items[].extraction.text_path`, and `semantic_context`; `record get` follows the frontend storage cookie redirect path for Qingflow attachments, so prefer local paths over remote URLs and do not expect legacy `data.normalized_record`
17. Treat nested schema shape as guidance, not a brittle contract; do not hard-code transient implementation details like optional nested `field_id` shape when composing inserts
18. For `partial_success`, read `created_record_ids`, then repair only the failed `items[].row_number` using `failed_fields`; never retry the whole batch after any row has `write_executed=true`
19. For numeric / amount-like fields, follow insert schema `expected_format` and `example_value`, not the builder field name alone. If the schema or error says decimals are not allowed, retry only the failed row with an integer value.

## Field Value Quick Table

Use this table after reading `record schema insert`. Field titles, options, candidates, and requiredness always come from the schema of the target app.

| Field kind | Write value | Notes |
| --- | --- | --- |
| Text / long text | JSON string | Use exact field title as key. Do not write system fields such as `编号` or `创建时间`. |
| Number / amount / score / rate | JSON number | Follow `expected_format`, `example_value`, and `allow_decimal`; if decimals are rejected, retry failed rows only with integers. |
| Date | `YYYY-MM-DD` | Use schema format if it differs. |
| Datetime | `YYYY-MM-DD HH:mm:ss` | Keep timezone/business date consistent with the user's request. |
| Single select | Exact option text or option id | Option text must exist in schema `options`; do not invent synonyms such as `月检` when the option is `每月`. |
| Multi select | Array of exact option texts or ids | Example: `["重点", "续约"]`. |
| Boolean / yes-no | Schema-supported boolean value | Prefer the schema example; some apps use option-like text. |
| Member | Natural name first, candidate object/id only after `needs_confirmation` | Example: `"张三"`. Do not pre-query admin contacts by default. |
| Department | Natural department name first, candidate object/id only after `needs_confirmation` | Example: `"销售部"`. Do not use ContactAuth/admin department tree as fallback. |
| Relation / reference record | Real `record_id/apply_id` for batch-created upstream rows; natural name only when unique | In full systems, insert upstream master data first, then use returned ids for downstream rows. |
| Subtable | Parent field value is an array of row objects | Keep subtable leaf fields inside the parent array; do not flatten subfields to top level. |
| Attachment | Upload first, then write returned attachment value/object | Do not write a local path directly unless the upload command returned that shape. |
| Formula / reference-fill / auto-fill | Fill the source/driver field, not the auto-filled target | Override only if schema says writable and user explicitly asks. |

## Copyable Shape Example

This file shape is the default for both one row and many rows. Replace field titles, option texts, record ids, and attachment values with values from `record schema insert`.

```json
[
  {
    "fields": {
      "客户名称": "上海样例客户",
      "客户状态": "有效",
      "客户标签": ["重点", "续约"],
      "预计金额": 12000,
      "预计签约日期": "2026-07-15",
      "负责人": "张三",
      "所属部门": "销售部",
      "关联客户": "540000000000000001",
      "明细子表": [
        {"明细名称": "首批巡检", "数量": 2, "结果": "正常"}
      ],
      "备注": "由 CLI 样例创建"
    }
  }
]
```

Full shape example: [record_insert_all_field_types.example.json](../../examples/record/record_insert_all_field_types.example.json).

## Field Notes

- `searchable_fields` on relation fields defines the backend-native searchable columns
- `accepts_natural_input=true` means the field may accept a natural string before explicit id fallback
- `may_become_required=true` means the field is writable now, but may turn required after linked visibility or option rules activate
- `linkage.kind=logic_visibility` means the field is statically tied to linked visibility or option-driven rules
- `linkage.kind=reference_fill` means the field participates in reference-based auto fill or default matching logic
- `linkage.kind=formula_fill` means the field usually comes from formula/default auto-fill logic
- `linkage.sources` lists the upstream field titles that influence the current field
- `linkage.affects_fields` lists downstream field titles that may change when this field changes
- `linkage.role=auto_fill_only` means "normally do not hand-fill this unless the product explicitly requires it"
- `requires_upload=true` means upload the file first, then write the returned value
- `failed_fields[].next_action` tells the next repair step for that row
- `allow_decimal=false` or errors like `requires an integer amount` mean the current write path wants an integer even if the business label says hours, rate, or score

## CLI Pattern

Use a JSON array file:

```bash
qingflow record insert --app-key APP_KEY --items-file records.json --json
```

`records.json`:

```json
[
  { "fields": { "客户名称": "测试客户", "负责人": "张三" } }
]
```

## Do Not

- Do not skip `record schema insert`
- Do not invent missing required fields
- Do not flatten subtable leaf fields to the top level
- Do not pre-query or silently guess member / department / relation ids when a natural string is enough
- Do not retry a whole batch after `created_record_ids` is non-empty
- Do not bind logic to a transient nested schema serialization detail when the field title and parent table already identify the legal payload shape
- Do not infer decimal support from the field label or builder type; the insert schema is the write contract
