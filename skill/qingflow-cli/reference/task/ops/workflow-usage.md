# Workflow and Task Usage Actions

Use these when the user is operating inside an existing process, not redesigning it.

Examples:

- add a comment to a record
- approve or reject a workflow task
- transfer a task
- roll back a task
- list todo, initiated, done, or cc tasks
- inspect workload by worksheet or workflow node
- urge a pending task

Rules:

- if the user starts from inbox, todo, workload, cc, or bottleneck language, use `task_*` first
- use `task_summary` for headline counts
- use `task_list` for flat browsing
- use `task_facets` when worksheet or workflow-node buckets matter
- treat task counts as task-center counts, not record counts
- switch to `record_get` only after locating the exact business record behind a task
- identify the exact target first through `task_list`
- for approve, reject, rollback, transfer, urge, or save-only, use only `task_list.data.items[].task_id` as the public action locator
- read `task_get` before action when the allowed action or required payload is not already explicit; `task_get.data.available_actions` is the source of truth
- avoid usage-side workflow actions on ambiguous records
- do not reconstruct an action target from `app_key + record_id + workflow_node_id`; those fields are readback/debug context, not the default action input
- execute actions through `task action --task-id ... --action ...`
- summarize the final action and exact `task_id`; include record ids only as returned context
