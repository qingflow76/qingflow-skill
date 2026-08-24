# Qingflow CLI 各场景「一次即可跑通」命令速查表

> **面向普通/基本成员账号时**：更易踩 **应用搜索/import/角色检索** 等权限类失败，请先读 **[QINGFLOW_CLI_MEMBER_CHEATSHEET.md](./QINGFLOW_CLI_MEMBER_CHEATSHEET.md)**（策略与最短读数路径）；**管理向差异**参阅 **[QINGFLOW_CLI_ADMIN_CHEATSHEET.md](./QINGFLOW_CLI_ADMIN_CHEATSHEET.md)**。

> **本文档目的**：按**场景**给出**形态正确、参数闭合**时的命令模板，便于复制后替换占位符即跑，减少「缺参 / 引号 / 根级选项」类返工。  
> **不是**「任何账号、任何租户、任何时刻都 100% HTTP 200」——若遇 `59004`（流币/AI 配额）、401、或目标资源不存在，仍可能失败；那种情况属于**环境与权限**，不是本表要解决的「命令写对一次成」问题。

**统一建议**

- 自动化读取命令优先加 `**--json`**；builder 写入/apply 命令默认只输出 JSON，不需要额外选择格式；展示写入结果时优先读 `operation + summary + resources[]`，不要按不同工具分别解析旧字段。
- 需要稳定 profile 时加 `**--profile default`**（或与你的会话一致的名字）。
- `task` / `record` 的大 JSON 查询类输出，按团队规范**落盘**（例如 `> tmp/qingflow_*.json`），本表为简洁只写核心参数。

---

## 1. 元：版本与帮助（不依赖登录）


| 场景        | 一次成功写法                                                   | 说明                                           |
| --------- | -------------------------------------------------------- | -------------------------------------------- |
| 查 CLI 包版本 | `qingflow --version` | 不依赖登录；只输出版本号。 |
| 查 CLI 包版本（JSON） | `qingflow --json version` | 不依赖登录；返回 `version` 与 `package`。 |
| 看顶层能力     | `qingflow -h`                                            | 确认子命令集合。                                     |
| 看某子命令帮助   | `qingflow <子命令> -h` 或 `qingflow record schema browse -h` | 嵌套子命令**不要**整体加引号。                            |


---

## 2. 会话恢复（仅业务命令失败后使用）


| 场景                 | 一次成功写法                                    | 必填/注意                                                                                                        |
| ------------------ | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 查看当前会话             | `qingflow --json auth whoami`             | 仅在业务命令提示会话不可用、账号不确定或需要排障时使用；不要作为每个任务的首步。                                                       |
| Credential 登录（自动化） | `echo "$QINGFLOW_CREDENTIAL"              | qingflow --profile default auth use-credential --base-url "$QINGFLOW_BASE_URL" --credential-stdin --persist` |
| 安全退出               | `qingflow auth logout --forget-persisted` | 需要清本机持久化凭证时用。                                                                                                |


---

## 3. 工作区（只读优先，避免误切租户）


| 场景          | 一次成功写法                                                   | 必填/注意                                                                                 |
| ----------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| 当前会话工作区详情   | `qingflow --json workspace get --ws-id <WS_ID>`          | `**<WS_ID>`** 与 `auth whoami` 中选中租户一致最稳；**不依赖**先 `workspace list`（list 在部分环境会因配额等失败）。 |
| 枚举工作区（可选）   | `qingflow --json workspace list --page 1 --page-size 40` | 可能因配额等失败；失败时仍以 **whoami + workspace get** 为基准。                                        |
| 切换工作区（会改会话） | `qingflow workspace select --ws-id <WS_ID>`              | **必填** `--ws-id`；可能触发 **59004**；自动化探针若不想改租户应**不调用**。                                  |


---

## 4. 应用与门户/视图/报表（只读）


| 场景           | 一次成功写法                                                               | 必填/注意                                                             |
| ------------ | -------------------------------------------------------------------- | ----------------------------------------------------------------- |
| 列出应用         | `qingflow --json app list`                                           | 通常仅需有效会话。                                                         |
| 成员侧按关键字找应用 | `qingflow --json app list --query <关键词>` | 只读取当前用户可见应用并本地过滤；看 `matched_count` / `unfiltered_count` / `items[].app_key`。 |
| 应用详情（含可访问视图） | `qingflow --json app get --app-key <APP_KEY>`                        | **必填** `--app-key`；后续 **view-id** 多从返回的 `accessible_views` 等字段选取。 |
| 门户列表         | `qingflow --json portal list`                                        | 一般只读。                                                             |
| 单个门户         | `qingflow --json portal get --dash-key <DASH_KEY>`                   | **必填** `--dash-key`。                                              |
| 用户侧视图        | `qingflow --json view get --view-id <VIEW_ID>`                       | **必填** `--view-id`（与用户态 id 一致，勿与 builder 的 `view-key` 混用）。        |
| 用户侧图表        | `qingflow --json chart get --chart-id <CHART_ID>`                    | **必填** `**chart-id` 合法且有权访问**。                                    |


---

## 5. 记录：`record`（区分「仅需 app-key」与「必须 view-id」）

下面「一次成功」指 **CLI 不会因缺参报错**；服务端仍可能因权限返回错误 JSON。


| 场景                      | 一次成功写法                                                                                    | 必填/注意                                                         |
| ----------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Insert schema              | `qingflow --json record schema insert --app-key <APP_KEY>`                             | 新建记录默认走 `qingflow-record-insert`；CLI 用 insert-ready schema + `record insert --items-file`。 |
| Import / code-block schema | `qingflow --json record schema import --app-key <APP_KEY>` / `qingflow --json record schema code-block --app-key <APP_KEY>` | 仅在导入或代码块任务明确需要时使用。 |
| Schema：browse（浏览态字段）    | `qingflow --json record schema browse --app-key <APP_KEY> --view-id <VIEW_ID>`            | **必须 `--view-id`**；不要用引号包住 `record schema browse` 整段。         |
| 列表/候选定位（运行时强校验）           | `qingflow --json record list --app-key <APP_KEY> --view-id <VIEW_ID>` | **必须 `--view-id`**；默认最多返回 10 条，适合样本/模糊定位；可加 `--query` / `--query-field`。 |
| 分析取数                    | `qingflow --json record access --app-key <APP_KEY> --view-id <VIEW_ID> --columns-file columns.json --where-file where.json` | 最终统计结论统一使用 `qingflow-record-analysis` 的 `record_access -> Python/pandas`。 |
| 单条读取                    | `qingflow --json record get --app-key <APP_KEY> --record-id <RECORD_ID>`                  | **必须** `--record-id`；返回前端详情页首屏上下文、引用、图片/文件资产。 |
| 全量记录日志                | `qingflow --json record logs --app-key <APP_KEY> --record-id <RECORD_ID> [--view-id <VIEW_ID>]` | 仅在需要完整审计/日志历史时使用；全量数据日志和流程日志写本地 JSONL。 |


**高风险写操作**（本表不保「业务上你希望的一次成功」，只列形态）：`record insert/update/delete`、`record code-block-run`（可能写回）需按 `-h` 逐项带齐文件类参数与安全开关。

---

## 6. 待办 `task`（查询类建议落盘）


| 场景   | 一次成功写法                                                                    | 必填/注意                                                                                   |
| ---- | ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| 待办列表 | `qingflow --json task list --task-box todo --flow-status all --page 1 --page-size 50` | 不限定应用时不要硬塞 `--app-key`；已知应用后再追加 `--app-key <APP_KEY>` 收窄。 |
| 待办详情 | `qingflow --json task get --task-id <TASK_ID>`                            | `<TASK_ID>` 必须来自 `task list` 的 `data.items[].task_id`；不要使用列表序号、record_id、workflow_node_id 或自行拼三键。 |
| 流程日志 | `qingflow --json task log --task-id <TASK_ID>`                            | 需有效 `**task-id`** 或等价组合。                                                                |
| 关联报表 | `qingflow --json task report --task-id <TASK_ID> --report-id <REPORT_ID>` | `**report-id`** 需有效。                                                                    |
| 执行动作 | `qingflow task action --task-id <TASK_ID> --action <ACTION> ...`          | **无 `--dry-run`**；属写操作，慎跑。                                                              |


---

## 7. 导入 `import`（链式；单步「一次成」条件）


| 场景     | 一次成功写法                                                                       | 必填/注意                                                                                                                                                                   |
| ------ | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 拉模板说明等 | `qingflow --json import template --app-key <APP_KEY>`                        | 常需应用管理类权限。                                                                                                                                                              |
| 校验文件   | `qingflow --json import verify --app-key <APP_KEY> --file-path <LOCAL_FILE>` | **必须** `--file-path`，且文件须为服务端**支持的导入模板格式**；随意占位文件可能被 `IMPORT_FILE_FORMAT_UNSUPPORTED`。                                                                                  |
| 导入状态查询 | `qingflow --json import status --app-key <APP_KEY>`                          | **仅能三选一**：`--process-id-str` / `--import-id` / `**--app-key`**（独自表示读该应用**最新导入**）；混搭多个选择器易被拒。**仅 `--app-key` 且无唯一「最新导入」时**可出现 `IMPORT_STATUS_AMBIGUOUS`（与是否管理员无关，属数据状态）。 |


更后序的 `repair` / `start` 依赖前置返回的 `**verification-id`** 等，按 `import -h` 逐级带参。

---

## 8. Builder（只列「必填闭合即过 CLI」的常用只读）


| 场景    | 一次成功写法                                                       | 必填/注意                             |
| ----- | ------------------------------------------------------------ | --------------------------------- |
| 成员搜索  | `qingflow --json builder member search --query <关键词>`        | `**--query` 服务端必填**（帮助里可能看起来像可选）。 |
| 角色搜索  | `qingflow --json builder role search --keyword <关键词>`        | `**--keyword` 必填**。               |
| 应用包列表 | `qingflow --json builder package list --query <关键词>`          | 直接走 `/tag`；返回 `items[].package_id/package_name/permissions`。 |
| 应用包读取 | `qingflow --json builder package get --package-id <整数>`      | `**package-id` 须为整数**。            |
| 发布自检  | `qingflow builder publish verify --app-key <APP_KEY>` | builder 写入/校验类命令自动 JSON。                       |


`builder * apply` / `role create` / `package apply` / `solution install` 等为写路径，成功与否强依赖配置文件与租户策略，**不放入「默认一次必成」表**。

---

## 9. 必败反例（避免浪费时间）


| 错误写法                                                | 原因                                              |
| --------------------------------------------------- | ----------------------------------------------- |
| `qingflow record list --app-key xxx`（无 `--view-id`） | 运行时常报错：`requires view_id`。                      |
| `"qingflow record schema browse" --app-key ...`     | 子命令被整体加引号，解析器不认。                                |
| `builder member search`（无 `--query`）                | 常见：`MEMBER_QUERY_REQUIRED` / query is required。 |
| `builder role search`（无 `--keyword`）                | 常见：`ROLE_QUERY_REQUIRED`。                       |
| `import status` 同时丢多个互斥 selector                    | 见上文「三选一」。                                       |


---

## 10. 最小业务链路示例（Wingent Momo runtime 下不做登录前置）

在满足账号权限的前提下：

1. `qingflow --json app list [--query <关键词>]` → 选一个 `**app_key`**
2. `qingflow --json app get --app-key <APP_KEY>` → 选一个 `**view_id`**
3. `qingflow --json record list --app-key <APP_KEY> --view-id <VIEW_ID>`

若要落盘再给第 3 步加 `> tmp/qingflow_records.json`。只有业务命令明确返回会话不可用、账号不确定或工作区异常时，才回到第 2 节做会话恢复。

---

*文档生成说明：与 **[../SKILL.md](../SKILL.md)**、[QINGFLOW_CLI_EXPLORATION_REPORT.md](./QINGFLOW_CLI_EXPLORATION_REPORT.md) 对齐；若 CLI 版本升级，请以 `qingflow … -h` 为准做小步修订。*
