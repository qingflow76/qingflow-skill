---
name: qingflow-task-ops
description: Use Qingflow todo discovery, workflow task context, associated approval context, workflow logs, and unified task actions with the current Wingent Momo runtime MCP session. Do not use this skill for record CRUD or final statistical analysis.
metadata:
  short-description: Qingflow task workflow context and actions
---

# Qingflow Task Ops

> **Skill 版本**：`qingflow-skills-2026.07.01.04`（入口文档版本；如需确认 CLI 包版本，使用 `qingflow --version` 或 `qingflow --json version`）。

## Overview

This skill is for task workflow operations only.
In Wingent Momo runtime, trust injected MCP credentials, workspace, and route context until a business tool explicitly reports otherwise.
Before executing, skim the shared maintenance baseline: [public-surface-sync.md](../qingflow-operations/references/public-surface-sync.md).

## Default Paths

Use exactly one of these default paths:

1. Find target todos
   `task_list`

2. Read one task context
   `task_list -> exact target -> task_get`

3. Read associated approval context when material to a high-impact recommendation
   `task_get -> task_workflow_log_get` and/or material `task_associated_report_detail_get`

4. Execute workflow action
   `task_list -> exact target -> task_get -> task_action_execute`

5. Execute a user-specified action on an already-clear target
   `task_list -> exact target -> (optional task_get) -> task_action_execute`

## Core Tools

- `task_list`
- `task_get`
- `task_action_execute`
- `task_associated_report_detail_get`
- `task_workflow_log_get`

## Supporting Tools

- `app_list`

## Standard Operating Order

Use one of these two modes:

1. Recommendation mode
   1. Trust the current MCP/session when the runtime has already injected credentials; recover auth/workspace only after an actual tool error
   2. Discover the exact target with `task_list`
   3. Read node context with `task_get`
   4. Before giving a high-impact approve/reject/rollback/transfer recommendation, read `task_workflow_log_get`
   5. If `task_get` returns visible `associated_reports`, read the reports that are material to the decision; if a report cannot be read, disclose the gap instead of blocking indefinitely
   6. Give a recommendation only after reviewing the available node context, workflow log when visible, and material associated reports
   7. Wait for explicit user confirmation before `task_action_execute`

2. User-directed execution mode
   1. Trust the current MCP/session when the runtime has already injected credentials; recover auth/workspace only after an actual tool error
   2. Discover the exact target with `task_list`
   3. If the target or action requirements are ambiguous, read `task_get`; otherwise go straight to `task_action_execute`
   4. Execute through `task_action_execute`
   5. After actions, report whether it succeeded, the `task_id`, the executed action, the final route/status, and any warnings

## Task-Center Rules

- Use `task_list` for flat browsing
- `task_box` must be one of:
  - `todo`
  - `initiated`
  - `cc`
  - `done`
- `flow_status` must be one of:
  - `all`
  - `in_progress`
  - `approved`
  - `rejected`
  - `pending_fix`
  - `urged`
  - `overdue`
  - `due_soon`
  - `unread`
  - `ended`
- `task_list` is the only public task discovery path in this MCP surface
- `task_list --query` uses backend `searchKey` first; only when backend returns zero rows does MCP apply a local fallback match on normalized `app_name / workflow_node_name / app_key / record_id`
- `task_id` must be copied from `task_list.data.items[].task_id`; it is not a row number, list index, record id, or workflow node id
- Use `task_id` directly with `task_get`, `task_workflow_log_get`, `task_associated_report_detail_get`, and `task_action_execute`; do not reconstruct actions from `app_key + record_id + workflow_node_id` unless the user explicitly provided that full locator for troubleshooting
- Default box usage:
  - `todo`: `task_list -> task_get -> task_workflow_log_get / task_associated_report_detail_get -> recommendation -> explicit user confirmation -> task_action_execute`
  - `initiated`: `task_list -> record_get`
  - `done`: `task_list -> record_get`
  - `cc`: `task_list -> record_get`
- Treat `initiated`, `done`, and `cc` primarily as list-plus-record-detail flows, not task action flows

## Workflow Usage Actions

- `task_get.capabilities.available_actions` is the source of truth for v1 executable actions
- Current public actions are:
  - `approve`
  - `reject`
  - `rollback`
  - `transfer`
  - `urge`
  - `save_only`
- Before high-impact approve/reject/rollback/transfer recommendations, review `task_workflow_log_get` when `task_get.visibility.audit_record_visible=true`
- If `task_get` returns visible `associated_reports`, review material reports with `task_associated_report_detail_get`; for unreadable or irrelevant reports, disclose the limitation instead of blocking the whole task
- QingBI associated report detail follows the frontend/qflow visible chart-data route first; a middle `CHART_SEE` / `40002` from legacy BI data reads is not by itself proof that the task-associated report is invisible.
- Do not give a high-impact approval recommendation based only on `task_get` unless workflow log/report visibility is unavailable and you explicitly state that limitation
- Do not execute `task_action_execute` until the user explicitly confirms the chosen action
- Exception: if the user has already explicitly authorized a concrete action on exact targets, you may execute directly after exact target resolution
- Avoid actions on ambiguous tasks or records
- Summarize the final action by `task_id`; include `app_key`, `record_id`, or `workflow_node_id` only as read-only context when the tool returns them, not as the action locator
- `reject` requires `payload.audit_feedback`
- For approve/reject, trust the current task detail or an explicit frontend-provided `formId`; app baseInfo is only a fallback. A baseInfo `40002` is not final task-action denial when `formId` is already known.
- `save_only` requires non-empty `fields` and is only available when the backend exposes editable fields for the current node
- For `save_only`, trust `task_get.editable_fields` / `editableQueIds` from the current task node. An app applicant-schema `40002` is not final task denial when the task detail already exposes the editable field.
- `task_action_execute` now distinguishes action execution from workflow continuation. Read `verification.runtime_continuation_verified` before claiming the workflow actually moved on.
- If `task_action_execute` returns `partial_success` with `WORKFLOW_CONTINUATION_UNVERIFIED`, report the action as sent but the downstream continuation as unverified.
- If `task_action_execute` returns `TASK_CONTEXT_VISIBILITY_UNVERIFIED` after a `46001`-style context loss, do not claim the task was already processed unless the workflow log or record state proves it.
- If `task_action_execute` returns `TASK_RUNTIME_CONSUMED_AFTER_ACTION`, treat that as a normal post-success state: the current node runtime was consumed, the workflow likely continued, and `46001` does not by itself mean the action failed

## Feedback Escalation

- If task capabilities, associated report detail, workflow log visibility, or action support still cannot satisfy the user's goal after reasonable use of this skill, summarize the exact gap in plain language.
- Ask whether the user wants you to submit product feedback.
- Only after explicit user confirmation, call `feedback_submit`.

## Response Interpretation

- `task_list` returns normalized todo rows and is the only default discovery path
- `task_list` may return `TASK_LIST_QUERY_FALLBACK_APPLIED`; this means backend search missed the query and MCP recovered the result through local exact-field fallback
- `task_get` returns node context summary, not full historical report data
- `task_associated_report_detail_get` may return either:
  - `result_type=view_list`
  - `result_type=chart_data`
- `task_workflow_log_get` returns workflow log detail only when the node grants log visibility
- A successful approve/reject/rollback/transfer may still lose the current-node runtime immediately; treat `record_state_readable=false + backend 46001` as a post-action runtime loss unless continuation verification says otherwise
- Treat `request_route` as the source of truth for live route debugging
- If only part of the requested work is completed, explicitly disclose which parts are done and which are not

## Resources

- Workflow and task usage actions: [references/workflow-usage.md](references/workflow-usage.md)
