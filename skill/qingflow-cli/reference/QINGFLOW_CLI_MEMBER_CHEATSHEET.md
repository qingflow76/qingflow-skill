# Qingflow CLI 普通成员命令速查表

> **适用对象**：当前会话为 **普通/基本成员**（`permission_level` 非租户/应用管理员、`import_capability` 常为无导入权等）。Wingent Momo runtime 下不要先跑 `auth whoami`；只有业务失败、账号不确定或排障时才核对身份。
> **与主技能关系**：请以 **[SKILL.md](../SKILL.md)**（本目录上一级）的规则与命令速查表为准。**本表**：成员侧最短读数与高概率通路；**租户/管理员向差异**请参阅同目录 **[QINGFLOW_CLI_ADMIN_CHEATSHEET.md](./QINGFLOW_CLI_ADMIN_CHEATSHEET.md)**。
> **可选补充**：同一目录 **[QINGFLOW_CLI_ONE_SHOT_CHEATSHEET.md](./QINGFLOW_CLI_ONE_SHOT_CHEATSHEET.md)** 收录 **全体角色通用**的子命令逐项模板（与本文分工：本文偏「成员能跑通的策略」，ONE_SHOT 偏「参数逐项闭合示例」）。

> **实证**：以下结论以会话内 `qingflow …` 为准；换账号/环境请以 `qingflow … -h` 与必要的身份核对结果为准。

**统一习惯**

- **只读拉取表单记录的最短链路**：见本节 **「最短路径：普通成员只读记录数据」**（可省略 `schema browse`）。**需先拉浏览视图表结构**时见 **[QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md](./QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md)**；最终统计结论统一使用 **`qingflow-record-analysis` 的 `record_access -> Python/pandas`**；**字段 `kind` / 数据形态**见 **[QINGFLOW_CLI_FIELD_DATA_TYPES.md](./QINGFLOW_CLI_FIELD_DATA_TYPES.md)**；**新建记录默认批量 JSON 链路**请用 **`qingflow-record-insert`**（`record_insert_schema_get -> record_insert(items)`，CLI 为 `record insert --items-file`，成员/部门/关联优先自然语言）；**浏览视图下更新记录**见 **[QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md](./QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md)**。
- 避免无必要地先绕 `workspace`、`view get`。
- 加 `--json`，便于区分 **CONFIG_ERROR**（少参）与 **backend**（权限/业务）。
- `app get` / `portal list` 等业务体常在 `**{ "data": { ... } }`** 里：取 `accessible_views`、`items` 前先 unwrap `data`。

---

## 最短路径：普通成员「只读记录数据」

> **目标**：直接使用当前 CLI 会话，用**最少 RPC、无多余子命令**，走到 `**record list` 成功返回样本/候选 JSON**；找应用用 `**app list [--query 关键词]`**，在读数前**不必**调用 `auth whoami` / `workspace get` / `view get` / `record schema browse`（除非你另需结构、query field 或排障）。

### 调用次数


| 前置           | 命令数    | 说明                                       |
| ------------ | ------ | ---------------------------------------- |
| 从零选应用        | **3**  | `app list` → `app get` → `record list`   |
| 已知 `APP_KEY` | **2**  | `app get` → `record list`                |
| 排障           | **+1** | 业务命令明确提示会话不可用、账号不确定时，再追加 `auth whoami` |


### 固定写法（复制后只换占位符）

```bash
qingflow --json app list
# 如果用户只给应用关键词：
qingflow --json app list --query <关键词>
# 在 items 中取 app_key → APP_KEY

qingflow --json app get --app-key <APP_KEY>
# 从返回 JSON 中取出应用对象（若存在顶层 .data 则先用 .data）；在 accessible_views 里选 view_id，见下文「先有通路、再要有数据」

qingflow --json record list \
  --app-key <APP_KEY> \
  --view-id <VIEW_ID>
```

大 JSON 按规范 **重定向落盘**（`> tmp/qingflow_records.json`）。

### 先有通路、再要有数据


| 关注点         | 说明                                                                                                                                                                       |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **连通性优先**   | 从 `app get.accessible_views` 选择表格类业务视图，优先 `system:all` 或明确可读的 `custom:*`。`record list` 默认最多 10 条，只用于样本/候选。 |
| **不一定有明细行** | 业务视图可能因视图筛选为空；`items` 为空不等于 CLI 坏了。若目标是任务中心待办/已办/抄送，应换 `task list --task-box …`。 |
| **读不到数据时**  | 在同一应用的 `accessible_views` 里切换其它表格类视图，跳过 **纯数字后缀** `custom:*`；不要用 `system:todo/done/cc` 当业务记录入口。 |


**普通成员不要使用「自定义 + 纯数字 id」去读数：** 形如 `**custom:1`、`custom:2`、`custom:12`**（`custom:` 后**仅数字**）。此类在实测中 `**record schema browse` / `list` / `access` 一致 40038**（`Object not exist`），**不可用其作为换源备选**——应直接跳过并在 **其它视图 id** 上取样。

### 为何不再多调这些


| 不先调                                | 原因                                                       |
| ---------------------------------- | -------------------------------------------------------- |
| `workspace get` / `workspace list` | 读应用记录**不依赖**；徒增一次往返，且 list 在部分环境受 **59004** 等影响。         |
| `view get`                         | `**record list` 不前置要求**；读后仍要看 `app get` 给的 `view_id` 才稳。 |
| `record schema browse`             | 只读「有哪些列」才需要；纯拉数据 **list 足够**。                            |


---

## 1. 优先使用（成员场景下实测高概率 exit 0）


| 场景                      | 命令                                                                               | 说明                                                                                                                             |
| ----------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| CLI 版本                  | `qingflow --version`；需要 JSON 用 `qingflow --json version`                         | 不依赖登录，不需要先查 npm 安装路径。                                                                                                     |
| 帮助                      | `qingflow -h`、`qingflow record schema browse -h`                                 | 嵌套子命令勿整体加引号。                                                                                                                   |
| 身份与租户                   | `qingflow --json auth whoami`                                                    | 用 `selected_ws_id` / `selectedWsId` 当作当前工作区。                                                                                   |
| 工作区只读                   | `qingflow --json workspace get --ws-id <WS_ID>`                                  | `WS_ID` 与 whoami 一致最稳。                                                                                                         |
| 工作区枚举                   | `qingflow --json workspace list --page 1 --page-size 40`                         | 若遇 59004（流币等），仍可依赖 whoami + `workspace get`。                                                                                   |
| 应用发现                    | `qingflow --json app list [--query <关键词>]`                                                       | 成员通常可看「有权限的应用」列表；`--query` 只在可见应用中本地过滤。                                                                                                              |
| 应用详情                    | `qingflow --json app get --app-key <APP_KEY>`                                    | 从 `data.accessible_views`（或顶层兼容结构）取 `**view_id`**；同源可取 `**package_id` / `package**`，供 `builder package get`。                   |
| 用户侧视图只读                 | `qingflow --json view get --view-id <VIEW_ID>`                                   | 用于补充视图配置，不是 `record list` 前置；业务记录读取仍以 `app get.accessible_views` 中的可读表格类视图为准；解析 app 只看同源 view/form 与可见应用树，不走旧应用搜索。                                    |
| 门户                      | `qingflow --json portal list`、`qingflow --json portal get --dash-key <DASH_KEY>` | `items` 常在 `data.items` 中取 `dash_key`。                                                                                         |
| Record 元数据（多只需 app-key） | `qingflow --json record schema insert --app-key <APP_KEY>` 等                  | 新建记录用 `insert` schema；`import` / `code-block` 仅在对应专项场景使用；`applicant` 仅兼容保留，不作为推荐入口。                                                                                         |
| Record 带视图              | 见下节 **「view-id 选取」**                                                             | `browse` / `list` / `access` 必须 `--view-id`。                                                                                  |
| 待办列表                    | `qingflow --json task list --app-key <APP_KEY> --page 1 --page-size 50`          | 无待办时也可能 **0 条但 exit 0**；`task get` / `task log` / `task report` 需有效 `**task_id`**（及必要的 `report_id`），**无待办则无 id 可测**（非 CLI 错误）。 |
| Builder（只读且成员常可用）       | `qingflow --json builder member search --query <关键词>`                            | `**--query` 必填**（服务端）。                                                                                                         |
| Builder 发布自检            | `qingflow builder publish verify --app-key <APP_KEY>`                     | builder 校验命令自动 JSON，相对安全。                                                                                                                     |
| 应用包读取                   | `qingflow --json builder package get --package-id <整数>`                          | `**package_id` 必须以 `app get`（等）返回为准**；偶发占位 id 在某环境可读**不可依赖**，换应用/包即可能失败。                                                       |


---

## 2. `view-id` 选取（成员必读）

`app get` 返回的 `accessible_views` **顺序上第一个**未必有数据读权限：**部分** `custom:*` 在基本成员下对 `schema browse` / `record list` 会返回 `**backend_code=40038`（如 `Object not exist`）**；**另有部分** `custom:*`（例如名称「我的数据」类）可与系统视图一样 **exit 0**，须按 **具体 `view_id`** 判断（见下「按视图探测」）。待办/已办/抄送属于任务中心语义，不再作为业务记录读取首选。

**特例（务必区分）：** `**custom:` 后仅为数字**（`custom:1`、`custom:12` 等）在普通成员会话下 **不适合作为读数备选**（三命令实测 **一致 40038**）；可读业务数据时请加用 **非纯数字后缀的 `custom:…`**（如 `custom:ebdl…`）或 `**system:*` / 本节策略**切换，勿与「部分 custom 不可用」泛泛混为一谈。

建议策略：

1. 优先选择 `system:all` 或名称明确的表格类 `custom:*` 业务视图来确认 `record list` 能通；若 `items` 为空，先判断当前视图筛选是否导致为空，再换其它表格类视图。若某个显式 `view_id` 返回权限或服务端错误，不要在同一次调用里把它自动改成其它系统视图；需要换视图时重新从 `app get.accessible_views` 或前端 URL 选。
2. `**custom:` 后仅数字**的 id（如 `**custom:1`、`custom:12`**）：**普通成员不可用其读数**，与策略 1 并行时**直接跳过**，不要在「换视图」时误选。
3. `view get` 只用于补充视图配置/导出能力，不是 `record list` 的前置条件；拉数以 `app get.accessible_views` 选出的 `view_id` 为准。

**按视图探测**：对同一 `app_key` 下 `**custom:<纯数字>` 之外**的 `view_id` 按需跑 `**record schema browse` / `list`** 筛通路。实测：`custom:1/2/12` 均 **40038**；`custom:ebdl…`「我的数据」可用；系统视图可用。

---

## 3. 成员常见「命令写对仍失败」（不要当 CLI 坏了）


| 命令/场景                                  | 典型现象                                                          | 含义（成员）                                                                                         |
| -------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 旧应用搜索入口                           | `backend_code=40002`                                          | 工作区级搜索常无权限；改用 `**app list --query`** 或 `**app list`** 选应用。                                                           |
| `import template` / `import verify`    | `IMPORT_TEMPLATE_UNAUTHORIZED`、`IMPORT_AUTH_PRECHECK_FAILED`  | 非应用导入管理员。                                                                                      |
| `import status` 仅 `--app-key`          | `IMPORT_STATUS_AMBIGUOUS`                                     | 无最新唯一导入记录或无权解析。                                                                                |
| `builder role search`                  | `ROLE_SEARCH_FAILED` / `backend_code=40002`                   | 搭建侧角色检索对成员常关闭。                                                                                 |
| `chart get` 随意 id                      | `network` / 报表类错误                                             | 需**真实且有权**的 `chart-id`（从应用/门户配置取）。                                                             |
| `**custom:1`、`custom:2`…（冒号后仅数字）** 上读数 | 基本成员 **不可用**上述 id 作主数据源；实测 **browse/list/access→40038**（见上文） | **不要**把它们当作「换一个 custom 试试」；应换同一应用下其它表格类业务视图，如 `system:all` 或 `custom:` 后缀含字母等（如 ebdl…）的视图；任务箱请走 `task list --task-box` |
| 某非标 `custom:*` 上 `record …`            | `40038` / `Object not exist`（exit 4）                          | 该成员对该视图无权限；换**同一应用**下其它 `**view_id`**（见上文排除规则）。                                                |
| `record get`                           | 需 list 里出现 `record_id`                                        | 若当前视图下列表无数据，则**无 id 可测**（与权限无关时的空结果）。                                                          |
| `workspace select`                     | `59004`                                                       | 流币/AI 配额与操作类型相关，与其他失败区分。                                                                       |
| 本会话未展开                                 | `auth login` / `use-credential`、写操作                           | 与角色无关的**命令形态**见通用表；成员仍可能因业务策略无法写。                                                              |


---

## 4. 仍建议避免的写法（与通用表一致）


| 错误                                                            | 原因                                                            |
| ------------------------------------------------------------- | ------------------------------------------------------------- |
| `record list` 无 `--view-id`                                   | `CONFIG_ERROR` / `requires view_id`。                          |
| **用 `custom:1`、`custom:12`** 等（`custom:` 后**仅数字**）作普通成员的主读数视图 | 实测 **browse/list/access 一律 40038**，与业务空数据不同，**换源时请跳过**该类 id。 |
| `builder member search` 无 `--query`                           | `MEMBER_QUERY_REQUIRED`。                                      |
| `builder role search` 无 `--keyword`                           | `ROLE_QUERY_REQUIRED`（有参数也可能因权限仍失败）。                          |


---

## 5. 扩展链路（含 workspace / schema）

若你还要 **核对当前工作区** 或 **先看 browse 字段**，在 **§「最短路径」** 之外可增加（顺序仍建议 **先最短再扩展**）。注意：最终统计结论、分析报告、趋势/排名/比例/分布必须使用 `qingflow-record-analysis` 的 `record_access -> Python/pandas`：

```bash
qingflow --json auth whoami  # 仅业务失败、账号不确定或需要写清当前租户上下文时
# 记下 selected_ws_id → WS_ID

qingflow --json workspace get --ws-id <WS_ID>   # 仅当需要写清「当前租户上下文」时

qingflow --json app list
qingflow --json app get --app-key <APP_KEY>
# accessible_views：优先表格类业务视图；若无业务行再换其它 view（勿用 custom:+纯数字，见前文）

qingflow --json record schema browse --app-key <APP_KEY> --view-id <VIEW_ID>   # 需要字段结构时
qingflow --json record list --app-key <APP_KEY> --view-id <VIEW_ID>
```

大数据请按团队规范 **重定向落盘**。

---

## 6. 与其它文档的关系


| 文档                                                                               | 用途                                                                             |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| [SKILL.md](../SKILL.md)                                                          | **主文档**：认证、落盘规则、正文「命令速查」与高危操作节选。                                                                     |
| [QINGFLOW_CLI_ADMIN_CHEATSHEET.md](./QINGFLOW_CLI_ADMIN_CHEATSHEET.md)        | **导入 / `builder role search` 等**管理向差异与成员侧失败对照。                                                        |
| [QINGFLOW_CLI_ONE_SHOT_CHEATSHEET.md](./QINGFLOW_CLI_ONE_SHOT_CHEATSHEET.md)     | 可选：全角色通用；各节「一次可复制」命令块与附录必败清单。                                                                     |


---

*修订时请同步：若服务端权限枚举或 CLI 改名，以 `qingflow … -h` 与实测为准。*

---

## 7. 验证清单（维护者）

以下结论来自 **基本成员** 会话与 help/实测归纳；配额、权限与数据为空等属环境差异：**换账号时请自行复验**。


| 主张                                                                                                                | 说明                                                                                                                                                |
| ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| §1 表内多数「高概率 exit 0」命令                                                                                             | 在典型成员会话下过 help/试跑对齐；仍以当前 CLI 与服务端为准。                                                               |
| `custom:*` 与 `system:*` 在 browse/list/access 上差异                                                                 | 同上；`custom:+纯数字` 读数常 40038 已在上文单列。                                                                  |
| `workspace select` 可能 59004                                                                                       | 流币等配额与其它失败区分；非每次必现。                                                                                                                               |
| **§「最短路径」**（app list→get→record list；优先表格类业务视图；空数据则换其它可读表格视图；**勿用 `custom:<仅数字>`**） | 不包含多余 `workspace get`/`schema browse`，除非另行需要。 |
| 本文未逐条自动化验证的项                                                                                                      | `task get`/`log`/`report`（缺 id）、`chart get`（缺真实 id）、**写路径** `record insert` 等 — 按通用表与业务策略，需有数据/权限时再测                                              |
