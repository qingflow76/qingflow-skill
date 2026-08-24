# Environment Switching

Use this reference before any workflow usage action, comment, or task-center operation that might affect live work.

## Step 1: Resolve the active environment

Decide explicitly whether the task targets:

- `test`: demo, mock data, smoke usage validation, training scenarios
- `prod`: real operational tasks, comments, and workflow actions

If the user did not specify an environment, default to `prod`.

## Test Environment

Use test for:

- workflow walkthroughs
- user acceptance demos
- comment or transfer rehearsals

## Production Environment

Use production for:

- live task-center operations
- live comments on real business records
- approve / reject / rollback / transfer / urge on real work

Production guardrails:

- never assume a task id, record id, or workflow node id
- find the exact target first
- if the task can be answered read-only, do not act

## Reporting Rule

For task ops, always report:

- active environment
- target app or task box
- operation type: read, comment, approve, reject, rollback, transfer, urge, or mark_read
- affected task ids or record ids
