# Generic Stdio MCP Clients

Use this for any local AI client that supports MCP over stdio.

## Required mapping

- `command`: `<ABSOLUTE_PATH_TO_REPO>/qingflow-support/mcp-server/qingflow-mcp`
- `args`: `[]`
- `env.QINGFLOW_MCP_DEFAULT_BASE_URL`: backend base URL for the active environment

Environment examples:

- `prod` (default): `https://qingflow.com/api`
- `test`: use the explicitly provided non-production backend

Keep separate client entries or separate config snippets for `test` and `prod`.

## Validation sequence

1. Start the client
2. Confirm the `qingflow` MCP server is visible
3. In Wingent Momo runtime, skip auth/workspace preflight and run a read-only tool such as `app_list`
4. In a standalone client without injected credentials, run `auth_use_credential` or `auth_login`
5. Then run `workspace_list`
6. Then run `workspace_select`
7. Run a read-only tool such as `app_list`

## Common failures

- Launch failure: bad `command` path or missing `.venv`
- Auth failure: invalid or expired credential/token
- Business tool failure before setup: workspace not selected
