---
name: qingflow-record-import
description: Explain and operate Qingflow file-based bulk import using the current Wingent Momo runtime MCP session; recover auth/workspace only after a tool error.
metadata:
  short-description: Qingflow bulk import workflow and troubleshooting
---

# Qingflow Record Import

> **Skill 版本**：`qingflow-skills-2026.07.01.04`（入口文档版本；如需确认 CLI 包版本，使用 `qingflow --version` 或 `qingflow --json version`）。

## Default Path

`app_get -> record_import_schema_get -> record_import_template_get -> record_import_verify -> (optional authorized repair) -> record_import_start -> record_import_status_get`

## Core Tools

- `app_get`
- `record_import_schema_get`
- `record_import_template_get`
- `record_import_verify`
- `record_import_repair_local`
- `record_import_start`
- `record_import_status_get`

## File Shape And Field Mapping

- Official template headers are the target contract. Do not rename them in the import file.
- CSV can be used as a source format for planning or local transformation, but the current verify/start path expects the official Excel template (`.xlsx` / `.xls`).
- When the user gives CSV-like data, map each source column to the official template header first, then write the mapped rows into a copy of the template after explicit user authorization.
- Relation fields: prefer stable target `record_id` or another unique searchable value already accepted by the import schema. Do not rely on duplicated display names.
- Member / department fields: use values inside the schema/candidate scope; do not invent departments or names that are not resolvable.
- Select fields: use option labels from the schema/template; option ids are acceptable only when the import schema or prior readback proves they are supported.

Example source CSV for planning only:

```csv
客户名称,关联客户,状态,负责人
上海示例客户,CUST_RECORD_ID_001,有效,张三
```

Mapped template row concept:

```json
{
  "客户名称": "上海示例客户",
  "关联客户": "CUST_RECORD_ID_001",
  "状态": "有效",
  "负责人": "张三"
}
```

## Working Rules

1. Inspect `app_get.data.import_capability` first
2. Read `record_import_schema_get` before touching the file when column meaning is unclear
3. Keep official headers unchanged
4. Verify before start
5. Only repair a file after explicit user authorization
6. After success, report the import status and tracking identifiers; read back one imported sample only when the user asks for row-level confirmation or when the import result does not already prove completion

## Template Fallback

`record_import_template_get` may return `status: partial_success` with a locally generated applicant template when the official template endpoint is permission-restricted but applicant fields are readable. If the warning is `IMPORT_TEMPLATE_LOCAL_FALLBACK_AUTH_UNKNOWN` or `verification.import_auth_prechecked` is false, treat the result only as "template file prepared"; actual import permission is still decided by `record_import_verify` and `record_import_start`.
