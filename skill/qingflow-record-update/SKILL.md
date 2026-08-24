---
name: qingflow-record-update
description: Update Qingflow records through the current record detail context using the Wingent Momo runtime MCP session; recover auth/workspace only after a tool error.
metadata:
  short-description: Detail-first Qingflow record update
---

# Qingflow Record Update

> **Skill 版本**：`qingflow-skills-2026.07.01.04`（入口文档版本；如需确认 CLI 包版本，使用 `qingflow --version` 或 `qingflow --json version`）。

## Default Path

`record_get -> record_update`

## Core Tools

- `record_update_schema_get`
- `record_update`
- `record_get`
- `record_list`

## Working Rules

1. Start with `record_get(app_key, record_id, view_id when known)` to read the current detail-page context; if the frontend/custom view is known, keep that same `view_id` through the update
2. Use `record_get.fields[]` for field titles, `field_id`, `kind`, and current values
3. Build `fields` as a field-title keyed map containing only the user-requested changes
4. Run `record_update` directly with that key/value map; pass the same `view_id` when it is known so the tool tries that frontend view first, then let the tool fall back to other executable routes if needed
5. Keep `verify_write=true` for production updates
6. If the write returns `status="needs_confirmation"`, stop and surface the candidates
7. On success, read only the final status, `update_route`, `write_executed`, and verification result; do not surface intermediate route failures as the outcome
8. On failure, surface the failed reason and field/path diagnostics returned by `record_update`
9. Use `record_update_schema_get` only after an update failure, field ambiguity, or explicit request to diagnose writable fields/routes
10. Treat app-level `viewList` or applicant/insert schema 40002 as auxiliary-context loss, not as final record permission denial, when `record_get` or `record_update` succeeds through the selected `custom:*` view or `system:all`/type=8 route
11. If single-record readback matters, prefer `record_get` after the write and read top-level `fields[]`, `media_assets.items[].local_path`, `file_assets.items[].local_path`, `file_assets.items[].extraction.text_path`, and `semantic_context`; `record_get` follows the frontend storage cookie redirect path for Qingflow attachments, so prefer local paths over remote URLs; use `record_list(..., output_profile="normalized")` only for batch row-shaped normalized readback
12. For batch updates, read top-level `mode`, `dry_run`, `total`, `succeeded`, `failed`, `needs_confirmation`, `updated_record_ids`, `write_executed`, `safe_to_retry`, `verification_status`, and `items[].row_number/status/record_id`
13. If `write_executed=true`, do not blindly retry the whole batch; use `items[]` and `updated_record_ids` to decide whether only failed rows need repair
14. If you use `record_list` to locate candidates, parse `data.items[]` as flat row objects such as `row["客户名称"]` + `row["record_id"]`; do not expect a nested `fields[]` array in list rows

## Special Field Values

Use the field `kind` from `record_get.fields[]` when shaping values:

- `member`: start with a natural-language name such as `"周颖"`. If `record_update` returns `status="needs_confirmation"`, no write happened; retry with one candidate object, for example `{"uid":1048599,"name":"沈嘉慧Seth","email":"shenjiahui@exiao.tech"}`.
- `department`: start with a department name such as `"客户成功部"`. The record tool resolves names through the member-visible directory path first; do not pre-query ContactAuth-only contact management APIs for ids. On `needs_confirmation`, retry with the explicit candidate object/id returned by the tool.
- `relation`: prefer a unique human-readable target value or `{"apply_id":"..."}`. On multiple matches, stop and retry only after choosing one `confirmation_requests[].candidates[]` item.
- `select`: single select uses one option string; multi select uses an array of option strings.
- `attachment`: use a supported uploaded/file object from the returned format hints; do not invent remote URLs when the tool asks for upload.
- Reference, formula, auto-fill, readonly, and system fields are not independent writable kinds. Do not force-write the filled target field; update the upstream driving field instead, or surface the blocker.

`needs_confirmation` means `write_executed=false`: the tool found candidates but did not have enough certainty to write. Do not report it as success or failure. Surface the candidate list if user choice is needed; if the intended candidate is obvious from the user request or prior context, retry with the explicit object and then verify the final value.

For member or department ambiguity, use the record candidate tools (`record_member_candidates` / `record_department_candidates`, or CLI `qingflow record member-candidates` / `department-candidates`). These follow the same field-scope candidate route as the frontend selector; do not replace them with contact-directory management queries.

## Do Not

- Do not pass legacy `view_key` / `view_name` selectors; use `view_id` only when the frontend/detail view is known
- Do not call `record_update_schema_get` as the normal pre-step for every update
- Do not use applicant/insert schema to decide record update fields
- Do not update fields that were absent from `record_get.fields[]` unless the user explicitly provided a raw field id and you can justify it
- Do not resolve lookup fields against a guessed record context
- Do not treat a denied intermediate route as final failure when `record_update` later succeeds through another route
