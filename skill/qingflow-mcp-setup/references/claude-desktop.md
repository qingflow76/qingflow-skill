# Claude Desktop

Use this when the user wants to install Qingflow MCP in Claude Desktop.

## Config snippet

```json
{
  "mcpServers": {
    "qingflow": {
      "command": "<ABSOLUTE_PATH_TO_REPO>/qingflow-support/mcp-server/qingflow-mcp",
      "args": [],
      "env": {
        "QINGFLOW_MCP_DEFAULT_BASE_URL": "<QINGFLOW_BASE_URL>"
      }
    }
  }
}
```

## Environment examples

- `prod` (default): set `QINGFLOW_MCP_DEFAULT_BASE_URL` to `https://qingflow.com/api`
- `test`: if needed, set `QINGFLOW_MCP_DEFAULT_BASE_URL` to the explicitly provided non-production backend

Keep separate snippets for `test` and `prod` so switching environments does not require editing values in-place under pressure.

## Notes

- After updating the config, restart Claude Desktop
- Replace `<ABSOLUTE_PATH_TO_REPO>` with the real checkout path on the current machine
- If the server path changes, update the `command` field
- The server is local stdio MCP, so no remote URL is required
- Do not store Qingflow credentials in Claude Desktop config; pass the createClaw credential through `auth_use_credential` inside the chat, or use `auth_login` when credential exchange is unavailable
