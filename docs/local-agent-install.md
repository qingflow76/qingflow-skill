# 本地 Agent、stdio MCP 与 CLI

Qingflow MCP 是在线产品界面，普通用户无需安装 MCP 服务或配置本地 stdio。直接访问：

[立即体验 Qingflow MCP](https://qingflow.com/product/qingflowMcp)

本仓库中的 Skills 用于 CLI 和 Agent 能力说明。Hosted Qingflow MCP 无需本地部署；如果需要把 MCP 服务进程运行在本机，使用下面的 stdio 包和客户端配置。

## 本地 stdio MCP

安装并启动统一 MCP 包：

```bash
npm install -g @qingflow-tech/qingflow-mcp
qingflow-mcp
```

一次性启动：

```bash
npx -y -p @qingflow-tech/qingflow-mcp@latest qingflow-mcp
```

通用 MCP 客户端的 stdio 配置示例：

```json
{
  "mcpServers": {
    "qingflow": {
      "command": "qingflow-mcp",
      "env": {
        "QINGFLOW_MCP_DEFAULT_BASE_URL": "https://qingflow.com/api"
      }
    }
  }
}
```

独立 MCP 客户端启动后，先在对话中调用 `auth_use_credential` 或 `auth_login` 建立会话；不要把密码、token 或 credential 放进客户端配置并提交到 Git。只有 CLI 的无人值守自动化才使用 stdin 注入 credential，详见下面的 CLI 说明。

## CLI

```bash
npx qingflow-cli@latest install
qingflow auth login --method oauth
```

CLI 人类用户优先使用 OAuth。自动化环境不应模拟浏览器登录，而应通过 stdin 注入 credential：

```bash
printf '%s' "$QINGFLOW_CREDENTIAL" | qingflow auth use-credential \
  --credential-stdin \
  --base-url "${QINGFLOW_BASE_URL:-https://qingflow.com/api}" \
  --persist
```

## 安全边界

- 不要把密码、token、credential 写进 JSON 配置并提交到 Git；
- OAuth 的 refresh token 由本机 keychain 优先保存；
- CI 使用短生命周期的 credential 或专用 profile；
- 生产环境通过环境变量覆盖 base URL 和 OAuth Resource URL。
