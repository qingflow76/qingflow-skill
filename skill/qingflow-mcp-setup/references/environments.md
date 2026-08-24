# Environment Switching

Use this reference before any setup, authentication, or live validation flow.

## Step 1: Resolve the active environment

Decide explicitly whether the user is targeting:

- `test`: for smoke tests, trial setup, DSL validation, mock data, and integration debugging
- `prod`: for real business usage in the formal environment

If the user did not specify an environment, default to `prod`.

## Test Environment

Default characteristics:

- preferred for first-time setup and local MCP validation
- mock or smoke data is acceptable when the user asks for it
- use read/write verification freely inside the intended test workspace

Known values in the current workspace:

- use an explicitly provided non-production backend
- common test workspace example: `ws_id=2`
- `qf_version`: usually unset unless the user explicitly needs a routed version

Setup behavior:

- prefer this environment for Claude Desktop or local MCP client onboarding
- for Wingent Momo runtime, use the injected session and skip auth/workspace preflight
- for standalone MCP client setup, use `auth_use_credential` or `auth_login`, then `workspace_list`, then `workspace_select`
- if the user asks to verify installation, a real read-only smoke path is acceptable

## Production Environment

Production is the default environment when the user does not specify one. If the user explicitly says `test`, switch to the dedicated non-production backend they provide.

Expected behavior:

- default `base_url`: `https://qingflow.com/api`
- confirm the production `qf_version` explicitly when browser traffic depends on routed versions such as `canary`
- confirm the exact workspace before any live validation
- prefer read-only checks first
- avoid mock data, smoke writes, or destructive tests unless the user explicitly asks for them

Production guardrails:

- do not store credentials in skill files or examples
- do not assume the same workspace ids as test
- treat startup verification and auth verification as separate steps
- when sharing snippets, label them as `prod` and `test` clearly
- when MCP and browser results diverge, compare `request_route` with the browser route before blaming the query logic

## Reporting Rule

When you give setup instructions, always state:

- active environment
- selected `base_url`
- selected `qf_version` when relevant
- whether the next step is read-only or write-impacting
