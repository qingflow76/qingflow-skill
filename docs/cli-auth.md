# CLI OAuth 认证指引

## 推荐入口

```bash
qingflow auth login --method oauth
```

执行后 CLI 会：

1. 读取 OAuth Authorization Server metadata；
2. 生成随机 `state`、PKCE verifier 和 S256 challenge；
3. 在本机随机 loopback 端口等待 `/oauth/callback`；
4. 打开浏览器完成用户授权；
5. 使用 authorization code + verifier 交换 access token 和 refresh token；
6. 将 OAuth profile 保存到本机会话目录。

CLI 是 Public Client，不保存密码，也不携带 client secret。普通业务命令不会因为缺少登录态而自动打开浏览器，必须由用户显式执行 login。

## 服务端 metadata

`${QINGFLOW_MCP_DEFAULT_BASE_URL}/.well-known/oauth-authorization-server` 至少应返回：

```json
{
  "issuer": "https://qingflow.com",
  "authorization_endpoint": "https://qingflow.com/api/oauth/authorize",
  "token_endpoint": "https://qingflow.com/api/oauth/token",
  "code_challenge_methods_supported": ["S256"],
  "grant_types_supported": ["authorization_code", "refresh_token"]
}
```

服务端需要校验 client ID、redirect URI、state、PKCE verifier、scope 和 resource。loopback 回调只能监听本机地址，不能接受任意公网回调地址。

## 常用命令

```bash
qingflow auth whoami
qingflow auth login --method oauth --no-browser
qingflow auth logout --forget-persisted
```

`--no-browser` 只是不自动打开浏览器，当前终端仍需接收本机回调。无头 CI 应使用：

```bash
printf '%s' "$QINGFLOW_CREDENTIAL" | qingflow auth use-credential \
  --credential-stdin --persist
```

## 故障排查

- metadata 缺少 PKCE S256 或 refresh grant：检查 OAuth discovery 响应；
- 回调超时：确认浏览器和 CLI 在同一台机器；
- refresh 失败：重新执行 `qingflow auth login --method oauth`；
- staging 环境：设置 `QINGFLOW_MCP_OAUTH_RESOURCE_URL`，不要修改源码里的生产默认值。
