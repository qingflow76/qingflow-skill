---
name: qingflow-common
description: Route Qingflow work through the shared public concepts and choose the matching CLI or MCP package. Use when comparing Qingflow CLI and MCP capabilities, selecting an execution surface, or handing work between record, task, form, workflow, and builder skills.
---

# Qingflow Common Concepts

Treat CLI and MCP as two invocation surfaces for the same Qingflow public contract. Choose the surface that is installed in the current runtime, then keep the same business workflow and declaration shape unless that operation is explicitly surface-specific.

## Choose A Surface

| Available runtime | Use | Best fit |
| --- | --- | --- |
| Terminal, script, CI, or a local file workflow | Qingflow CLI | Repeatable commands and JSON files |
| Agent has `qingflow-mcp` tools | Qingflow MCP | Records, tasks, packages, forms, views, workflows, portals, and builder configuration |

Do not require both surfaces. If only one is installed, complete the workflow on that surface. Do not expose a CLI-only command as an MCP tool, or vice versa.

## Shared Concepts

- **AppForm** is the versioned declarative definition for an application form: app metadata, fields, sections, layout, settings, and field configuration. The same JSON declaration is used by CLI and Qingflow MCP.
- **Record** is runtime data written to an existing app. Use the record schema before an insert, update, import, or analysis workflow.
- **Task** is a workflow work item. Prefer task operations for approval, transfer, rollback, and assignee actions.
- **Builder resource** is package, app, view, chart, portal, navigation, or workflow configuration. It is separate from record data.
- **Schema version** is part of the public contract. Pin it for one AppForm or workflow operation and do not combine values from different versions.

## Invocation Mapping

| Business operation | CLI | MCP |
| --- | --- | --- |
| Form schema/read/apply/delete | `qingflow --json builder app-form ...` / `builder app delete` | `app_form_schema`, `app_form_get`, `app_form_apply`, `app_delete` |
| AppForm static validation | `qingflow --json builder app-form validate --file ...` | Performed inside `app_form_apply`; no separate tool |
| Record and task work | `qingflow --json record ...` / `task ...` | Qingflow MCP record and task tools |
| Package, view, portal, chart, workflow | `qingflow --json builder ...` | Qingflow MCP configuration tools |

The operation names and payload schemas are defined by the public surface. Use the current Schema or tool input schema as the source of truth, not a legacy command name or backend payload.

## Package Boundaries

- `@qingflow-tech/qingflow-cli` packages CLI execution guidance and CLI-supported workflows.
- `@qingflow-tech/qingflow-mcp` packages every MCP Skill and exposes one unified MCP service. Record operations and system configuration are task routes in this service, not package or server choices.

Each package includes this common Skill. The CLI package installs its CLI guidance; the MCP package installs every MCP domain Skill. The source of every packaged Skill is `qingflow-support/mcp-server/skills/`.

## Route Next

Use the installed package's relevant domain Skill. In the unified MCP package, select the Skill by the requested work, not by an assumed user or builder server role. Do not link to or invoke a domain Skill that the current package did not install.
