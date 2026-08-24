# GitHub 与 npm 发布指引

这个目录是从内部工作区整理出的公开发布副本。原工作区不应作为 GitHub 仓库直接推送。

## 1. 发布前检查

```bash
git status --short
rg -n -i "password|secret|token|redis://|oalite|hackers" . \
  --glob '!skills/**' --glob '!uv.lock'
```

确认没有：

- 真实 token、密码、Redis URL；
- 内部域名、内部 Git 地址和部署凭据；
- `.venv/`、缓存、`dist/`、测试产物；
- 包含真实用户数据的 JSON 或 transcript。

## 2. 本地验证

```bash
python3 -m venv .venv
./.venv/bin/pip install -e '.[dev]'
./.venv/bin/pytest -q tests/test_cli_oauth.py
npm install
npm run pack:npm:cli
```

构建产物位于 `dist/npm/`，不要提交到 Git。

## 3. 创建 GitHub 仓库

在 GitHub 创建一个空仓库，例如 `qingflow-mcp`，然后在本目录执行：

```bash
git init
git add .
git commit -m "chore: publish Qingflow MCP and CLI skills"
git branch -M main
git remote add origin https://github.com/<org>/qingflow-mcp.git
git push -u origin main
```

如果当前目录仍在上层 monorepo 中，不要覆盖上层仓库的 `origin`；应在这个副本目录中初始化独立 Git 仓库。

## 4. npm 发布

先确认包名、版本号和 npm scope 已被组织授权：

```bash
npm login
npm publish dist/npm/qingflow-cli-<version>.tgz --access public
npm publish dist/npm/qingflow-tech-qingflow-cli-<version>.tgz --access public
npm publish dist/npm/qingflow-tech-qingflow-mcp-<version>.tgz --access public
```

三个包的作用分别是：`qingflow-cli` 是一键安装器，`@qingflow-tech/qingflow-cli` 是实际 CLI，`@qingflow-tech/qingflow-mcp` 是本地 stdio MCP。发布前先执行 `npm run pack:npm`，并以 tarball 内的 `package.json` 为准确认包名和版本。

发布后至少验证以下入口：

```bash
npx qingflow-cli@latest install --help
npx -y -p @qingflow-tech/qingflow-cli@latest qingflow --version
npx -y -p @qingflow-tech/qingflow-mcp@latest qingflow-mcp-skills list
```

## 5. GitHub 引流

README 首页只保留两个明显入口：

```text
CLI：npx qingflow-cli@latest install
MCP：访问 https://qingflow.com/product/qingflowMcp
```

再补充 OAuth 演示、30 秒使用示例、GitHub Discussions、Issue 模板和企业接入链接。下载链接和官网链接使用 UTM 参数，以区分 GitHub README、Release 和 npm 带来的访问。

README 还应明确 Hosted MCP、本地 stdio MCP 和 CLI 的边界，并链接到 `CONTRIBUTING.md`、`SECURITY.md`、OAuth 文档和本地 Agent 配置文档。

## 6. Release 习惯

- 使用 Git tag 发布，例如 `v1.0.0`；
- Release notes 写清 CLI、MCP、skill 的变化；
- OAuth 协议或权限变化必须单独标注；
- 发现凭据泄露时先吊销，再清理 Git 历史。
