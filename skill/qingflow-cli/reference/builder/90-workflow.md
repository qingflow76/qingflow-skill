# Builder Workflow

Read this when the task is about approval/fill/copy/webhook workflow configuration or workflow repair.

## Scope

Responsible for: `builder flow get/schema/apply`, WorkflowSpec, `patch_nodes`, assignees, editable fields, and workflow readback.

Not responsible for: guessing raw backend fields without first reading `builder flow schema` / `builder flow get`.

## Main chain

```text
contract -> app get fields -> builder flow schema -> builder flow get -> member/role lookup -> build WorkflowSpec -> flow apply --spec-file -> builder flow get readback
```

## Demo/reference files

Workflow examples depend on live `builder flow schema`, field ids, role ids, and member ids. Use [workflow/README.md](./workflow/README.md) as the staged guide and [workflow/workflow-schema.json](./workflow/workflow-schema.json) for schema validation; do not copy a static flow spec without replacing live ids from the target app/workspace.

## Recommended write path

- Before applying a workflow, verify the app has an explicit business status select field such as `状态`, `处理状态`, `审批状态`, `工单状态`, `计划状态`, `报工状态`, or `单据状态`. Domain result fields are not enough by themselves: for example, `检验结论` should be paired with `处理状态`.
- For workflow creation or replacement, always use `builder flow get` / `builder flow schema`, then submit a complete WorkflowSpec with `--spec-file`.
- Do not use `--nodes-file` + `--transitions-file` in skill-led workflow builds. Even simple linear workflows should be represented as WorkflowSpec.
- Use `patch_nodes[]` only for targeted maintenance of existing nodes. Node ids come from `builder flow get` readback.
- Do not mix `patch_nodes` and full `spec` in the same call.

## Input modes

All workflow creation and replacement uses WorkflowSpec through `--spec-file`. Existing-node maintenance can use `--patch-nodes-file` after readback. This is the only skill-led workflow write path for linear, branching, Q-Robot, approval, filling, and cc flows.

## Detailed workflow docs

Use [workflow/README.md](./workflow/README.md) for full staged workflow modeling and [workflow/workflow-schema.json](./workflow/workflow-schema.json) for schema validation.
