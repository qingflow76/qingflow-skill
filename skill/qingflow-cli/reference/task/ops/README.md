# Qingflow CLI Task Ops

## Overview

This section is for task workflow operations only. Do not use it for record CRUD or final statistical analysis.

## Default Paths

Use exactly one of these default paths:

1. Find target todos
   `qingflow task list`

2. Read one task context
   `task list -> exact target -> task get`

3. Read associated approval context
   `task get -> task report` or `task log`

4. Execute workflow action
   `task list -> exact target -> task get -> task action`

5. Execute a user-specified action on an already-clear target
   `task list -> exact target -> (optional task get) -> task action`

## Core Tools

- `qingflow task list`
- `qingflow task get`
- `qingflow task action`
- `qingflow task report`
- `qingflow task log`

## Supporting Tools

- `app_list`
- `app_search`

## Standard Operating Order

Before any task action, comment, transfer, urge, approve, reject, or rollback, resolve the target environment with [environments.md](./environments.md). If the user does not specify one, default to `prod`.

Use one of these two modes:

1. Recommendation mode
   1. Discover the exact target with `task list`
   2. Read node context with `task get`
   3. Before giving any approval recommendation, read `task log`
   4. If `task get` returns any `associated_reports`, read every visible report through `task report`
   5. Give a recommendation only after reviewing node context, workflow log, and associated reports
   6. Wait for explicit user confirmation before `task action`

2. User-directed execution mode
   1. Discover the exact target with `task list`
   2. If the target or action requirements are ambiguous, read `task get`; otherwise go straight to `task action`
   3. Execute through `task action --task-id ...`
   4. After actions, report the exact `task_id`, executed action, and any returned `app_key / record_id` plus warnings

## Task-Center Rules

- Use `task list` for flat browsing
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
- `task list` is the only public task discovery path
- `task list --query` uses backend `searchKey` first; only when backend returns zero rows does CLI apply a local fallback match on normalized `app_name / workflow_node_name / app_key / record_id`
- Treat `task_id` from `task list.data.items[]` as the public action locator. Do not reconstruct action identity from `app_key + record_id + workflow_node_id`.
- Default box usage:
  - `todo`: `task list -> task get -> task log / task report -> recommendation -> explicit user confirmation -> task action`
  - `initiated`: `task list -> record get`
  - `done`: `task list -> record get`
  - `cc`: `task list -> record get`
- Treat `initiated`, `done`, and `cc` primarily as list-plus-record-detail flows, not task action flows

## Workflow Usage Actions

- `task get.capabilities.available_actions` is the source of truth for executable actions
- Current public actions are:
  - `approve`
  - `reject`
  - `rollback`
  - `transfer`
  - `urge`
  - `save_only`
- Before any approve/reject/rollback/transfer recommendation, always review `task log` when `task get.visibility.audit_record_visible=true`
- If `task get` returns visible `associated_reports`, review each one with `task report`; do not rely on report summary alone
- Do not give an approval recommendation based only on `task get`
- Do not execute `task action` until the user explicitly confirms the chosen action
- Exception: if the user has already explicitly authorized a concrete action on exact targets, you may execute directly after exact target resolution
- Avoid actions on ambiguous tasks or records
- Summarize the final action and the exact `task_id`
- `reject` requires `payload.audit_feedback`
- `save_only` requires non-empty `fields` and is only available when the backend exposes editable fields for the current node
- `task action` distinguishes action execution from workflow continuation. Read `verification.runtime_continuation_verified` before claiming the workflow actually moved on.
- If `task action` returns `partial_success` with `WORKFLOW_CONTINUATION_UNVERIFIED`, report the action as sent but the downstream continuation as unverified.
- If `task action` returns `TASK_CONTEXT_VISIBILITY_UNVERIFIED` after a `46001`-style context loss, do not claim the task was already processed unless the workflow log or record state proves it.
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

- Environment switching: [environments.md](./environments.md)
- Workflow and task usage actions: [workflow-usage.md](./workflow-usage.md)
