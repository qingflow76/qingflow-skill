# Qingflow MCP & CLI Skills

Qingflow MCP & CLI Skills 是面向 AI Agent 的轻流操作指南和客户端集成层。它把工作区、应用、表单数据、任务、视图、图表、门户和应用搭建能力，连接到支持 MCP 的 AI 客户端或 `qingflow` CLI。

本仓库包含：

- Hosted Qingflow MCP 的接入说明；
- 本地 stdio MCP 和 `qingflow` CLI 的源代码及 npm 打包脚本；
- 可安装到 Codex、Claude Code、Cursor 或通用 Agent 目录的 Skills、参考文档和示例。

仓库不包含 Qingflow 后端、生产 Cloud MCP 部署配置或任何用户凭据。项目当前处于 Beta 阶段，具体能力仍受 Qingflow 服务端版本和当前账户权限控制。

## 快速入口

| 目标 | 推荐入口 |
| --- | --- |
| 直接在 AI 客户端中使用 | [打开 Qingflow MCP 接入页面](https://qingflow.com/product/qingflowMcp) |
| 在终端或脚本中使用 | `npx qingflow-cli@latest install` |
| 在本地运行 stdio MCP | 安装 `@qingflow-tech/qingflow-mcp`，见[本地 Agent 文档](docs/local-agent-install.md) |
| 参与开发或提交问题 | [贡献指南](CONTRIBUTING.md) · [安全政策](SECURITY.md) |

## 能力范围

| 能力 | 典型任务 |
| --- | --- |
| 发现业务结构 | 查找工作区、应用、表单、视图、门户和图表，理解现有系统结构 |
| 管理业务数据 | 查询、新增、修改、删除、导入和导出记录 |
| 分析业务信息 | 统计分布、比例、排名和趋势，基于可访问数据生成结论 |
| 处理流程待办 | 查看待办与流程上下文，读取流程日志，执行当前节点允许的动作 |
| 搭建业务应用 | 创建或调整表单、布局、视图、流程、图表、门户和应用包 |
| 安全执行 | 先读取 schema 和权限范围，写操作前确认目标，并在执行后校验结果 |

CLI 与 MCP 覆盖相近的业务能力，但使用方式不同：MCP 适合在 AI 客户端中直接用自然语言工作，CLI 适合终端操作、脚本和自动化任务。

## 方式一：Hosted Qingflow MCP

Hosted Qingflow MCP 是由轻流托管的远程 MCP 服务。普通用户无需下载或部署 MCP 服务，直接通过[接入页面](https://qingflow.com/product/qingflowMcp)选择 Codex、Cursor、Kimi Code、WorkBuddy 或其他兼容客户端的配置方式，并使用 OAuth 授权。

在 Codex 客户端中，可以添加一个 `Streamable HTTP` MCP 服务器：

```text
名称：qingflow
地址：https://mcp.qingflow.com/mcp
```

也可以通过 Codex CLI 完成配置：

```bash
codex mcp add qingflow --url "https://mcp.qingflow.com/mcp"
codex mcp login qingflow
codex mcp list
```

建议先使用只读请求验证连接：

```text
请列出我当前有权访问的轻流应用，并简要说明每个应用的用途。先不要修改任何数据。
```

连接成功后，可以继续提出业务目标，例如：

```text
汇总本周所有延期项目，分析风险原因并生成跟进清单。
```

涉及审批、写入或删除时，应先确认目标和影响范围。

### 安装 MCP Skills

下面的命令只把 MCP 相关 Skills 复制到 Codex 的用户级 Skill 目录，不会安装或启动本地 MCP 服务：

```bash
npx -y -p @qingflow-tech/qingflow-mcp@latest \
  qingflow-mcp-skills install --agent codex --scope user --copy
```

查看包内包含的 Skills：

```bash
npx -y -p @qingflow-tech/qingflow-mcp@latest qingflow-mcp-skills list
```

安装器也支持 `claude-code`、`cursor` 和 `generic`。如需安装到当前项目，将 `--scope user` 改为 `--scope project`。

## 方式二：本地 stdio MCP

需要把 MCP 服务进程运行在本机时，安装统一 MCP npm 包：

```bash
npm install -g @qingflow-tech/qingflow-mcp
qingflow-mcp
```

也可以不做全局安装直接运行：

```bash
npx -y -p @qingflow-tech/qingflow-mcp@latest qingflow-mcp
```

本地 stdio 接入适合 Claude Desktop、Cursor 或其他支持本地 MCP 进程的 Agent。配置示例和认证边界见[本地 Agent 文档](docs/local-agent-install.md)和[MCP 配置说明](docs/mcp-setup.md)。

## 方式三：Qingflow CLI

Qingflow CLI 将认证、工作区、应用、记录、任务和 Builder 能力封装成可脚本化命令，适合开发者在终端中直接使用，也适合由 AI Agent 调用。

开始前请准备 Node.js 16.16+、npm 和 Python 3.11+。

### 安装 CLI 和 CLI Skills

先安装 CLI：

```bash
npx qingflow-cli@latest install
```

再查看并安装 CLI Skills：

```bash
qingflow-skills list
qingflow-skills install --agent codex --scope user --copy
```

如需安装到当前项目，将 `--scope user` 改为 `--scope project`。已有同名 Skill 时安装器不会覆盖；确认需要替换后再显式添加 `--force`。

### OAuth 登录

面向个人开发者和本地 Agent，推荐使用 OAuth：

```bash
qingflow auth login --method oauth
qingflow auth whoami
```

无人值守任务使用 stdin 注入短生命周期 credential，不要把 credential、密码或 token 写入仓库、JSON 配置或日志：

```bash
printf '%s' "$QINGFLOW_CREDENTIAL" | qingflow auth use-credential \
  --base-url "${QINGFLOW_BASE_URL:-https://qingflow.com/api}" \
  --credential-stdin --persist
```

### 使用 CLI

登录后可以从只读命令开始：

```bash
qingflow --help
qingflow app list
qingflow task list
qingflow record --help
qingflow builder --help
```

复杂的数据写入和应用搭建任务建议交给已安装 Skills 的 Agent：Agent 会先读取对应 schema 和命令帮助，再生成参数或 JSON 文件，避免猜测字段与权限。

退出登录并清除本机持久化凭据：

```bash
qingflow auth logout --forget-persisted
```

## 开发与验证

```bash
python3 -m venv .venv
./.venv/bin/pip install -e '.[dev]'
./.venv/bin/pytest -q
npm install
npm run pack:npm
```

构建的 npm tarball 写入 `dist/npm/`，该目录不会进入 Git。发布前请阅读[发布指引](docs/publish-guide.md)，不要直接提交构建产物。

## 相关文档

- [CLI OAuth 认证](docs/cli-auth.md)
- [MCP 配置说明](docs/mcp-setup.md)
- [本地 Agent 安装](docs/local-agent-install.md)
- [GitHub 与 npm 发布指引](docs/publish-guide.md)
- [贡献指南](CONTRIBUTING.md)
- [安全政策](SECURITY.md)

## 许可证

MIT，见 [LICENSE](LICENSE)。
