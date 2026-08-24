---
name: qingflow-operations
description: Route Qingflow operational requests to the right specialized record or task skill using the current unified Qingflow MCP session. Use when the task is operational but it is not yet clear whether it is record CRUD or final analysis.
metadata:
  short-description: Router for Qingflow operational skills
---

# Qingflow Operations

> **Skill 版本**：`qingflow-skills-2026.07.01.04`（入口文档版本；如需确认 CLI 包版本，使用 `qingflow --version` 或 `qingflow --json version`）。

For shared record/task concepts and CLI versus MCP selection, read [$qingflow-common](../qingflow-common/SKILL.md). This Skill routes operational work inside the unified Qingflow MCP package.

## Overview

This skill is a lightweight router for operational Qingflow work. It is a task router inside the unified MCP, not a separate MCP service.
In Wingent Momo runtime, trust injected MCP credentials, workspace, and route context until a business tool explicitly reports otherwise.
Before routing, skim the shared maintenance baseline: [public-surface-sync.md](references/public-surface-sync.md).

## Default Paths

Route to exactly one of these specialized paths:

1. Record insert
   Switch to [$qingflow-record-insert](../qingflow-record-insert/SKILL.md)

2. Record update
   Switch to [$qingflow-record-update](../qingflow-record-update/SKILL.md)

3. Record delete
   Switch to [$qingflow-record-delete](../qingflow-record-delete/SKILL.md)

4. Record import
   Switch to [$qingflow-record-import](../qingflow-record-import/SKILL.md)

5. Task workflow operations
   Switch to [$qingflow-task-ops](../qingflow-task-ops/SKILL.md)

6. Analysis
   Switch to [$qingflow-record-analysis](../qingflow-record-analysis/SKILL.md)

7. Standalone MCP setup or explicit auth/workspace recovery
   Switch to [$qingflow-mcp-setup](../qingflow-mcp-setup/SKILL.md)

8. App / view / workflow / chart / portal / package configuration
   Switch to the `qingflow-system-build` Skill in the same MCP package.

## Routing Rules

- If the user does not know the target `app_key`, discover apps first with `app_list` / `app list --query` over current-user visible apps, then route to the specialized skill; do not use the legacy app search path for ordinary members
- If the app is known but the available data range is unclear, call `app_get` first and inspect `accessible_views`
- If the task is about creating or new record entry, switch to `$qingflow-record-insert`
- If the task is about editing an existing record directly, switch to `$qingflow-record-update`
- If the task is about deleting records directly, switch to `$qingflow-record-delete`
- If the task is about import templates, import capability discovery, import-file verification, authorized local file repair, import execution, or import status, switch to `$qingflow-record-import`
- If the task is about todo discovery, task context, approval actions, rollback or transfer, associated report review, or workflow log review, switch to `$qingflow-task-ops`
- If the task is about package, app, field, layout, workflow, view, chart, portal, visibility, icon, or app base configuration, switch to `qingflow-system-build` within the same MCP package.
- If the task involves member, department, or relation fields and the user only has natural names/titles, keep the same route; direct write now supports backend-native auto resolution and may return `needs_confirmation` with candidates instead of failing blind
- For member/department field ambiguity, keep the record insert/update route and use `record_member_candidates` / `record_department_candidates`; do not switch to `directory_*`, builder member search, external-contact lookup, or contact-directory management queries. The record workflow exposes `directory_search` for member-visible keyword search, not directory tree/list management.
- If the task involves linked visibility, upstream/downstream field dependencies, reference-driven auto fill, or formula-driven defaulting, keep the same insert/update route and read field-level `linkage` from the schema before composing payloads
- If the task is about subtable writes, still route to the matching insert/update skill, but shape the payload as parent subtable field -> row array; do not route users toward top-level leaf selectors
- If the task is insert-focused and readback/detail context matters, keep the same route and prefer the single-record detail readback after the write; use normalized list readback only when batch row shape is needed
- If the user sounds like an ordinary workflow assignee rather than a system operator, prefer `$qingflow-task-ops` over direct record mutation whenever both paths could fit
- If the task is about task discovery by natural language query, still route to `$qingflow-task-ops`; `task_list --query` now uses backend search first and only falls back to local matching when backend returns zero rows
- If the task is about grouped distributions, ratios, rankings, trends, insights, or any final statistical conclusion, switch to `$qingflow-record-analysis`
- In Wingent Momo runtime, do not route to `$qingflow-mcp-setup` as a preflight. Switch there only when a business tool explicitly reports missing auth, invalid session, or wrong/missing workspace, or when the user asks to configure a standalone MCP client.

## Shared Preconditions

- prefer canonical app ids, record ids, task ids, and workflow node ids over guessed names
- if a field or target is still ambiguous after schema/task lookup, ask the user to confirm from a short candidate list instead of guessing
- if schema fields include `linkage.sources` or `linkage.affects_fields`, treat those as the preferred high-level explanation of field dependencies instead of trying to infer hidden front-end logic
- if the task can stay read-only, do not write or act
- if the task involves a user-uploaded import file, do not modify the file unless the user explicitly authorizes repair or normalization
- if the task involves record import, call `app_get` first and inspect `data.import_capability` before template download, file repair, or import start
- if a record detail includes images or attachments, prefer the single-record detail tool's local paths: images from `media_assets.items[].local_path`, documents/tables from `file_assets.items[].local_path` and `extraction.text_path`; remote Qingflow file URLs are not stable direct-read targets
- if the current MCP capability is unsupported, the workflow is awkward, or the user's need still cannot be satisfied after reasonable use, summarize the gap, ask whether to submit feedback, and call `feedback_submit` only after explicit user confirmation

## Shared Helper

- `feedback_submit` is a cross-cutting helper for product feedback submission
- It does not require Qingflow login or workspace selection
- Use it only after the user explicitly confirms they want to submit feedback

## Resources

- Shared public-surface baseline: [public-surface-sync.md](references/public-surface-sync.md)
- Record insert: [$qingflow-record-insert](../qingflow-record-insert/SKILL.md)
- Record update: [$qingflow-record-update](../qingflow-record-update/SKILL.md)
- Record delete: [$qingflow-record-delete](../qingflow-record-delete/SKILL.md)
- Record import: [$qingflow-record-import](../qingflow-record-import/SKILL.md)
- Task workflow operations: [$qingflow-task-ops](../qingflow-task-ops/SKILL.md)
- Dedicated analysis workflow: [$qingflow-record-analysis](../qingflow-record-analysis/SKILL.md)
- System-building work uses the `qingflow-system-build` Skill in the same unified MCP package.
