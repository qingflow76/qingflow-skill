# Environment Switching

Use this reference before any data creation, update, delete, or workflow usage action.

## Step 1: Resolve the active environment

Decide explicitly whether the task targets:

- `test`: demo, mock data, smoke usage validation, training scenarios
- `prod`: real operational data and live workflow actions

If the user did not specify an environment, default to `prod`.

## Test Environment

Use test for:

- mock or smoke data entry
- business flow walkthroughs
- user acceptance demos
- data correction rehearsals

Test behavior:

- creating demo data is acceptable
- default to at least `5` records for mock or smoke datasets unless the user asks for fewer
- destructive cleanup is acceptable only when the record scope is explicit

Known current test backend:

- use an explicitly provided non-production backend

## Production Environment

Use production for:

- live data entry
- live business record updates
- comments and workflow actions on real records
- controlled data correction or deletion

Production behavior:

- prefer search or get before any write
- restate the exact app and record scope before update or delete
- do not create mock, smoke, or demo data unless the user explicitly asks for it
- for bulk changes, summarize the target count before execution and the affected ids after execution
- destructive actions need explicit confirmation in the conversation context

Production guardrails:

- never assume a record id, app id, or workspace id
- treat `record_delete` as high risk
- if the task can be answered read-only, do not write

## Reporting Rule

For app-user operations, always report:

- active environment
- target app
- operation type: read, create, update, delete, or workflow action
- affected record count or ids
