# Qingflow CLI 管理员命令速查表（Skill Reference）

> **适用**：`qingflow --json auth whoami` 中具备 **租户/工作区级管理、应用检索、导入、搭建配置** 等权限的账号（如 **超级管理员、应用管理员** 等，`permission_level` 以服务端为准）。
> **与普通成员对照**：权限较窄时请用 **[QINGFLOW_CLI_MEMBER_CHEATSHEET.md](./QINGFLOW_CLI_MEMBER_CHEATSHEET.md)**；**主流程与落盘规则**以 **[SKILL.md](../SKILL.md)** 为准。需要 **全子命令「一次可复制」逐项模板**时可参阅同目录 **[QINGFLOW_CLI_ONE_SHOT_CHEATSHEET.md](./QINGFLOW_CLI_ONE_SHOT_CHEATSHEET.md)**（任选，默认执行技能不必打开）。

---

## 1. 元与安装


| 场景        | 命令                                               | 备注                                  |
| --------- | ------------------------------------------------ | ----------------------------------- |
| 查 CLI 包版本 | `qingflow --version`；需要 JSON 用 `qingflow --json version` | 不依赖登录，不需要先查 npm 安装路径 |
| 帮助        | `qingflow -h`、`qingflow record schema browse -h` | 嵌套子命令勿整体加引号                         |


---

## 2. 会话与工作区


| 场景            | 命令                                                              |
| ------------- | --------------------------------------------------------------- |
| 当前身份与租户       | `qingflow --json auth whoami` → `selected_ws_id`                |
| 工作区详情         | `qingflow --json workspace get --ws-id <WS_ID>`                 |
| 枚举工作区         | `qingflow --json workspace list --page 1 --page-size 40`        |
| **切换租户**（改会话） | `qingflow workspace select --ws-id <WS_ID>`（可能 **59004** 流币/配额） |


---

## 3. 应用与门户（管理侧常用）


| 场景                     | 命令                                                                 | 管理员说明                              |
| ---------------------- | ------------------------------------------------------------------ | ---------------------------------- |
| 列表 / 关键字搜索                     | `qingflow --json app list [--query <词>]`                                         | 通用；`--query` 只过滤当前用户可见应用                                 |
| 详情（含 accessible_views） | `qingflow --json app get --app-key <APP_KEY>`                      | 正文常在 JSON 的 `**data**` 包裹内         |
| 门户                     | `qingflow --json portal list`、`portal get --dash-key <DASH_KEY>`   | `dash_key` 多在 `data.items`         |


---

## 4. 记录数据

与 **[成员速查](./QINGFLOW_CLI_MEMBER_CHEATSHEET.md)** 及 **[SKILL.md](../SKILL.md)**「命令速查」一致：`record schema browse`、`record list`、`record access` **必须** `--view-id`。查询类遵守 **SKILL 落盘**：`record list`、`get`、`access`、`schema browse` 等。最终统计结论、分析报告、趋势/排名/比例/分布统一使用 **`qingflow-record-analysis` 的 `record_access -> Python/pandas`**。

---

## 5. 待办

同 SKILL：`task list`、`get`、`log`、`report` 查询输出 **必须落盘**。`task action` **无 `--dry-run`**。

---

## 6. 导入（偏应用管理员）


| 步骤     | 命令                                                                           | 备注                                                                |
| ------ | ---------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| 模板说明   | `qingflow --json import template --app-key <APP_KEY>`                        | **常需应用管理权限**（成员常为 UNAUTHORIZED）                                   |
| 校验上传文件 | `qingflow --json import verify --app-key <APP_KEY> --file-path <FILE>`       | 文件须**服务端支持的模板格式**，否则 `**IMPORT_FILE_FORMAT_UNSUPPORTED`**         |
| 状态     | `qingflow --json import status [--app-key | --import-id | --process-id-str]` | **三选一**；仅 `--app-key` 且无唯一「最新导入」时可能 `**IMPORT_STATUS_AMBIGUOUS`** |


链路后续依赖 `verification-id`，见 `qingflow import -h`。

---

## 7. Builder

**只读、管理会话下常见可用**：


| 命令                                                           | 必填                                    |
| ------------------------------------------------------------ | ------------------------------------- |
| `qingflow --json builder member search --query <关键词>`        | `--query`                             |
| `qingflow --json builder role search --keyword <关键词>`        | `--keyword`（成员常 `ROLE_SEARCH_FAILED`） |
| `qingflow --json builder package list [--query <关键词>]`       | 直接读取应用包列表；看 `items[].package_id` |
| `qingflow --json builder publish verify --app-key <APP_KEY>` | —                                     |
| `qingflow --json builder package get --package-id <整数>`      | 整数，`package-id` 来自上下文                 |


写路径：`role create`、`package apply`、`solution install`、`flow apply`、各类 `*-apply` — **无 universal dry-run**，慎用。

---

## 8. 必败反例

与 **[QINGFLOW_CLI_MEMBER_CHEATSHEET.md](./QINGFLOW_CLI_MEMBER_CHEATSHEET.md)** 常见踩雷、**[SKILL.md](../SKILL.md)**「命令速查」末段「必败形态」一致；**逐条 CLI 形态表**另见 **[QINGFLOW_CLI_ONE_SHOT_CHEATSHEET.md](./QINGFLOW_CLI_ONE_SHOT_CHEATSHEET.md)** §9：`record list` 缺 `view-id`、子命令错引号、builder 缺 query/keyword、`import status` 多 selector。

---

*修订：以 `qingflow … -h` 与 **MEMBER**、[QINGFLOW_CLI_EXPLORATION_REPORT.md](./QINGFLOW_CLI_EXPLORATION_REPORT.md) 对齐。*
