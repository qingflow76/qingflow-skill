---
name: qingflow-record-delete
description: Delete Qingflow records safely using the current Wingent Momo runtime MCP session; recover auth/workspace only after a tool error.
metadata:
  short-description: Qingflow record delete
---

# Qingflow Record Delete

> **Skill 版本**：`qingflow-skills-2026.07.01.04`（入口文档版本；如需确认 CLI 包版本，使用 `qingflow --version` 或 `qingflow --json version`）。

## Default Path

`record_list / record_get -> record_delete`

## Core Tools

- `record_list`
- `record_get`
- `record_delete`

## Working Rules

1. Resolve the exact target `record_id` first
2. Prefer reading the current state before delete when the request is high risk
3. Choose an accessible system `view_id` from `app_get.accessible_views`; custom views can locate records but cannot be used as the delete route
4. Call `record_delete` with `record_id` or `record_ids` and the system `view_id` so the backend uses the matching listType delete route

## Do Not

- Do not pass `custom:*` view selectors to `record_delete`; custom views can locate records, but delete currently supports only system listType routes
- Do not omit `view_id`; a delete without frontend list context is ambiguous and should return `RECORD_DELETE_VIEW_REQUIRED`
- Do not infer the target record id from a vague title if `record_list` can disambiguate it
