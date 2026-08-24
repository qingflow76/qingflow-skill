---
name: qingflow-mcp-setup
description: Install, connect, authenticate, and troubleshoot the Qingflow MCP server in local AI clients such as Claude Desktop or any stdio-compatible MCP client. Use when the user wants to configure the MCP, verify local startup, log in with token/password, select a workspace, or fix connection/authentication issues.
metadata:
  short-description: Install and connect the Qingflow MCP locally
---

# Qingflow MCP Setup

> **Skill 版本**：`qingflow-skills-2026.07.01.04`（入口文档版本；如需确认 CLI 包版本，使用 `qingflow --version` 或 `qingflow --json version`）。

## Overview

This skill sets up the local Qingflow MCP server, connects it to a local AI client, and verifies authentication and workspace selection. Use it for installation, client configuration, token login, and connection troubleshooting.

## Workflow

Follow these steps in order.

`feedback_submit` is also available as a cross-cutting helper when setup or MCP capability gaps still block the user after reasonable troubleshooting. It does not require Qingflow login or workspace selection, and should be called only after explicit user confirmation.

Before configuration or live calls, identify the target environment explicitly as `test` or `prod`, then read [references/environments.md](references/environments.md). If the user did not specify one, default to `prod`.

### Step 1: Verify the local project path

Resolve the repository root first. In this repo, the MCP server should live at:

- `<repo_root>/qingflow-support/mcp-server`

Key entrypoint:

- `<repo_root>/qingflow-support/mcp-server/qingflow-mcp`

If the path differs, stop and update all client config snippets before proceeding.
If the Skill is installed outside the source checkout, set `QINGFLOW_MCP_ROOT=<repo_root>/qingflow-support/mcp-server` before running `scripts/check_local_server.sh`.

### Step 2: Install local dependencies

Run:

```bash
cd <repo_root>/qingflow-support/mcp-server
python3 -m venv .venv
./.venv/bin/pip install -e '.[dev]'
```

Use `scripts/check_local_server.sh` to verify the entrypoint and virtualenv. The script first tries `QINGFLOW_MCP_ROOT`, then the current git repository, then the installed Skill's `qingflow-support/mcp-server` ancestor.

### Step 3: Configure the local AI client

For any stdio-compatible MCP client, map these values:

- `command`: `<repo_root>/qingflow-support/mcp-server/qingflow-mcp`
- `args`: `[]`
- `env.QINGFLOW_MCP_DEFAULT_BASE_URL`: the target backend URL for the active environment
- `env.QINGFLOW_MCP_DEFAULT_QF_VERSION`: set this when the environment must route to a specific version such as `canary`

Client-specific snippets:

- Claude Desktop: read [references/claude-desktop.md](references/claude-desktop.md)
- Generic stdio MCP clients: read [references/generic-stdio.md](references/generic-stdio.md)

When both test and production are in play, keep separate config snippets or clearly labeled `env` blocks so the user can switch without ambiguity.

### Step 4: Validate startup

The server is a stdio MCP process. A direct terminal launch may print nothing and wait for a client. That is normal.

Manual startup command:

```bash
cd <repo_root>/qingflow-support/mcp-server
./qingflow-mcp
```

Prefer validating through the client after config is added.

### Step 5: Use injected session first; authenticate only for setup or recovery

For Wingent Momo runtime conversations, the session normally already carries the credential-derived token, workspace, and route context. Do not run `auth_use_credential`, `auth_login`, `workspace_list`, or `workspace_select` before ordinary business tools. Start with the smallest read-only business call that fits the task; if it succeeds, continue.

For a standalone local MCP client that has no injected session, use this setup order:

1. `auth_use_credential` or `auth_login`
2. `workspace_list`
3. `workspace_select`
4. Run a small read-only business tool

`auth_use_credential` gets the selected workspace from the credential context. If the user needs a different workspace after authentication, use `workspace_list` and then `workspace_select`.
After auth, prefer one read-only tool call that returns `request_route` so you can confirm the live `base_url` and `qf_version` before proceeding.
`auth_use_credential` is a tool call, not a custom HTTP header. It exchanges the createClaw credential for a Qingflow token, `wsId`, and when needed `Cookie: qfVersion=...` after the session is established.
Do not run `workspace_select` on production paths unless the user explicitly asks to switch workspace or a business tool clearly reports that no workspace is selected. If `/user` does not return a version lane, the session now falls back to the workspace `systemVersion`.

### Step 6: Troubleshoot in the right layer

- If the client cannot launch the server, check path, execute permission, and `.venv`
- If tools return `auth required`, re-run `auth_use_credential` or `auth_login`
- If tools return `workspace not selected`, call `workspace_list` and `workspace_select`
- If calls fail after a working session, assume token expiry and re-authenticate
- If the browser shows data but MCP does not, compare `request_route` against the browser environment and check whether `qf_version` should be `canary`

## Guardrails

- Never write tokens into the skill files
- In Wingent Momo runtime, trust injected workspace context until a business tool proves otherwise; for standalone clients, confirm workspace with `auth_whoami`, `workspace_select`, or a successful read-only business call.
- When debugging, distinguish server startup issues from Qingflow auth issues
- When the user mentions production, restate the exact `base_url`, `qf_version`, and workspace before any live validation
- If setup is complete but the current MCP capability is still unsupported or the user's need still cannot be satisfied, summarize the gap, ask whether to submit feedback, and call `feedback_submit` only after explicit user confirmation

## Resources

- Environment switching: [references/environments.md](references/environments.md)
- Claude Desktop config: [references/claude-desktop.md](references/claude-desktop.md)
- Generic stdio config: [references/generic-stdio.md](references/generic-stdio.md)
- Local checks: [scripts/check_local_server.sh](scripts/check_local_server.sh)
