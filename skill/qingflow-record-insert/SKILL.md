---
name: qingflow-record-insert
description: Create Qingflow records with a schema-first insert workflow.
metadata:
  short-description: Schema-first Qingflow record insert

---

# Qingflow Record Insert

> **Skill 版本**：`qingflow-skills-2026.07.01.04`（入口文档版本；如需确认 CLI 包版本，使用 `qingflow --version` 或 `qingflow --json version`）。

## Default Path

`record_insert_schema_get -> record_insert(items) -> optional record_get/readback`

Default to batch-shaped insert. A single new record is `items` with one row.

## Core Tools

- `record_insert_schema_get`
- `record_insert`
- `record_member_candidates`
- `record_department_candidates`
- `file_upload_local`

## Special Field Write Cheatsheet

Always read the insert schema first, then use field titles as `items[].fields` keys. For special fields:

- `member`: write a unique name, email, or resolved member id. If candidates are duplicated or the tool returns `needs_confirmation`, stop and surface candidates.
- `department`: do not invent department names. Use a value inside the schema/candidate scope: unique department name, returned id/key, or returned object shape such as `{"key":"DEPT_ID","label":"部门名"}` / `{"id":"DEPT_ID","value":"部门名"}`.
- `relation`: known target record id is most stable for batch inserts. Natural display text is allowed only when it uniquely resolves through the field's `searchable_fields`; duplicates require confirmation.
- `single_select` / `multi_select`: option label and option id are both acceptable when present in schema/options. Prefer labels for readability; let the tool compile to the path-specific value.
- `attachment`: upload the local file first with `file_upload_local`, then write the returned file value. Do not write only a filename or arbitrary URL.
- System fields are read-only: `数据ID`, `编号`, `申请人`, `申请时间`, `创建人`, `创建时间`, `提交人`, `提交时间`, `更新时间`, `更新人`, `当前流程状态`, `当前处理人`, `当前处理节点`, `流程标题`.

## Failure Repair Contract

When insert returns `blocked`, `partial_success`, or `needs_confirmation`, do not retry the whole batch blindly.

- Read `items[].failed_fields[]` first.
- Each failed field exposes `error_code`, `expected_format`, `example_value`, and `next_action`.
- For `member`, `department`, `relation`, `attachment`, and `select` fields, `next_action` is field-type specific: candidate lookup, upload first, use record/apply id, or use schema option label/id.
- Retry only the failed `row_number` with corrected values. If any row has `write_executed=true` or `created_record_ids` is non-empty, never replay the original batch.

## Candidate Lookup

Do not pre-query member or department ids by default. Use candidate commands only when:

- the user explicitly asks to see candidates
- insert returns `needs_confirmation`
- member / department names are likely duplicated
- a natural value is outside the field's candidate scope

```bash
qingflow --json record member-candidates \
  --app-key APP_KEY \
  --field-id FIELD_ID \
  --keyword "张三"
```

```bash
qingflow --json record department-candidates \
  --app-key APP_KEY \
  --field-id FIELD_ID \
  --keyword "直销部"
```

If the candidate scope must match an existing runtime context, pass the current record or pending fields:

```bash
qingflow --json record member-candidates \
  --app-key APP_KEY \
  --field-id FIELD_ID \
  --record-id RECORD_ID \
  --workflow-node-id WORKFLOW_NODE_ID \
  --fields-file pending_fields.json \
  --keyword "张三"
```

Without `record_id` / `workflow_node_id` / `fields-file`, the result is a static applicant-node preview. It is useful for explicit browsing, but not proof that every candidate is valid in a later workflow-specific write.

## Working Rules

1. Start with `record_insert_schema_get`
2. Read `required_fields`, `optional_fields`, `runtime_linked_required_fields`, `payload_template`, field-level `expected_format`, `example_value`, and `options`
3. Inside every field bucket, read field-level `linkage` first when present; it is the canonical static hint for linked visibility, reference-driven auto fill, or formula-driven fields
4. Inside `optional_fields`, pay special attention to any field with `may_become_required=true`; these are writable fields that can become required when linked visibility or option-driven rules activate
5. Build `items` as `[{"fields": {...}}]`, where each `fields` map uses field titles from the insert schema
6. Treat `runtime_linked_required_fields` as required-but-not-directly-writable runtime/upstream dependencies, not as fields to hand-fill blindly
7. For `linkage.kind=logic_visibility`, read `sources` as upstream trigger fields and treat `role=manual_input_after_activation` as "fill this only after the upstream condition is satisfied"
8. For `linkage.kind=reference_fill`, prefer filling the source field first; treat target fields with `role=auto_fill_preferred` or `auto_fill_only` as reference-driven outputs rather than blind manual inputs
9. For `linkage.kind=formula_fill`, treat the field as formula/default-auto-fill driven unless the user explicitly asks to override it and the field is still writable
10. If insert succeeds and single-record detail/readback matters, prefer `record_get`; for batch verification, rely on returned `created_record_ids` first, then use `record_get` for selected rows or `record_access -> Python` when a row-shaped bulk check is truly needed
11. Keep subtable payloads under the parent field as a row array
12. Follow the Special Field Write Cheatsheet for member, department, relation, select, and attachment values; do not pre-query ids by default when a natural value is unique enough
13. If the write returns `status="needs_confirmation"`, stop and surface the candidates
14. Retry failed rows only with explicit ids / objects after the user confirms
15. Keep `verify_write=true` for production inserts
16. If post-write detail context matters, read `record_get.fields[]`, `media_assets.items[].local_path`, `file_assets.items[].local_path`, `file_assets.items[].extraction.text_path`, and `semantic_context`; `record_get` follows the frontend storage cookie redirect path for Qingflow attachments, so prefer local paths over remote URLs and do not expect legacy flat record shapes
17. Treat nested schema shape as guidance, not a brittle contract; do not hard-code transient implementation details like optional nested `field_id` shape when composing inserts
18. For `partial_success`, read `created_record_ids`, then repair only the failed `items[].row_number` using `failed_fields`; never retry the whole batch after any row has `write_executed=true`
19. Do not put Qingflow system fields in `fields`: `数据ID`, `编号`, `申请人`, `申请时间`, `创建人`, `创建时间`, `提交人`, `提交时间`, `更新时间`, `更新人`, `当前流程状态`, `当前处理人`, `当前处理节点`, `流程标题`. They are generated by the platform and can be read after creation, not manually inserted.
20. When the user asks to add sample records after system setup, still generate values from schema: required fields first, select values from `options`, scalar/date/amount values from `expected_format` and `example_value`; do not invent values outside the insert schema.
21. For ratio, completion-rate, score, and percentage-like fields, obey the schema's `expected_format/example_value`. If the field was modeled as money/amount or otherwise only accepts integers, do not invent decimal percentages; either use an integer value that matches the schema or report that the field should be modeled as `number` for decimal ratios.

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

## CLI Pattern

CLI fallback for the schema step:

```bash
qingflow --json record schema insert --app-key APP_KEY > tmp/qingflow_insert_schema.json
```

Use a JSON array file:

```bash
qingflow --json record insert --app-key APP_KEY --items-file records.json
```

`records.json`:

```json
[
  { "fields": { "客户名称": "测试客户", "负责人": "张三" } }
]
```

## Do Not

- Do not skip `record_insert_schema_get`
- Do not invent missing required fields
- Do not fill platform system fields such as `数据ID`, `编号`, `申请人`, `创建时间`, or `更新时间`
- Do not flatten subtable leaf fields to the top level
- Do not invent member / department / relation candidates outside schema or candidate scope
- Do not invent select option labels outside schema `options`
- Do not pre-query or silently guess member / department / relation ids when a natural string is enough
- Do not retry a whole batch after `created_record_ids` is non-empty
- Do not bind logic to a transient nested schema serialization detail when the field title and parent table already identify the legal payload shape
