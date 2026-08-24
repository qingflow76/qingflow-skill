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

- if the user starts from inbox, todo, workload, cc, or bottleneck language, use the public task tools first
- use `task_list` for headline counts and flat browsing; group locally by app or workflow node when buckets matter
- use `task_get`, `task_workflow_log_get`, and `task_associated_report_detail_get` only after locating the exact task
- treat task counts as task-center counts, not record counts
- switch to `record_get` only after locating the exact business record behind a task
- identify the exact target first
- for approve or reject, identify the exact target first; prefer `task_id` from task-center results, then use `task_action_execute` with action `approve` or `reject`
- avoid usage-side workflow actions on ambiguous records
- summarize the final action and target task ids or record ids
