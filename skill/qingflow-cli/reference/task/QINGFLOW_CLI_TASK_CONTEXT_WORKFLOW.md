# 任务上下文 SOP：待办列表 → 详情 → 审批历史 → 关联报表 → 执行动作

本文与 **MCP / 服务端公开工具命名**对齐，并给出已安装的 `**qingflow` CLI** 等价命令。编写前已在当前环境对 `**task list` / `task get` / `task log`** 实跑；`**task report`** 在抽样任务上遇到过后端 `**40038` Object not exist**（见文末「实测排障」），属数据/权限/报表生命周期问题，**不否定**标准编排顺序。

**必须落盘**：`task` 的 `list`、`get`、`log`、`report` 以及 `**task action` 的响应**若体积大，均应 `> tmp/qingflow_*.json`，与主技能 [SKILL.md](../../SKILL.md) 一致。

**输出解包**：`task list/get/log/report` 的主数据通常在 `data` 下，不要求有顶层 `status`。没有顶层 `status` 不代表失败；先检查是否有错误字段，再按 `task list -> data.items[]`、`task get -> data.task / data.available_actions`、`task log -> data.items[]`、`task report -> data` 解包。

---

## 1. 编排顺序（固定）


| 步骤  | 工具名（文档/编排常用）                        | CLI 子命令                         | 说明                                                                            |
| --- | ----------------------------------- | ------------------------------- | ----------------------------------------------------------------------------- |
| 1   | `task_list`                         | `qingflow [--json] task list`   | `--task-box todo` 为待办（可省略则默认 todo）                                            |
| 2   | `task_get`                          | `qingflow [--json] task get`    | **优先** `--task-id`；从响应中取动作能力、关联报表摘要                                           |
| 3   | `task_workflow_log_get`             | `qingflow [--json] task log`    | 当前任务上下文的流程/审批历史条目（与详情独立接口，勿与 `extras.workflow_log` 混为一谈；记录级全量日志用 `record logs`） |
| 4   | `task_associated_report_detail_get` | `qingflow [--json] task report` | **必须** `--report-id`；ID 来自 **步骤 2** 的关联报表列表                                   |
| 5   | `task_action_execute`               | `qingflow [--json] task action` | **无 `--dry-run`**；调用即生效，`**--action` 须落在 `task get` 的 `available_actions` 内** |


实现侧 CLI 将上述工具映射到 `qingflow_mcp` 的 `TaskContextTools`（`task` 子命令源码：`task list/get/log/report/action` → `task_list`、`task_get`、`task_workflow_log_get`、`task_associated_report_detail_get`、`task_action_execute`）。

---

## 2. 定位方式

- **唯一默认路径**：全程使用列表里拿到的 `**task_id`**（字符串十进制；与大雪花 ID 一致时保持 **引号 / JSON 字符串** 习惯，避免其它子系统精度问题）。`task_id` 必须来自 `task_list.data.items[].task_id`，不是列表序号、record_id 或 workflow_node_id。
- `task_action_execute` / `task action` **只使用 `task_id` 定位**。不要传 `app_key`、`record_id`、`workflow_node_id`，也不要从其它输出里自行拼三键。
- `task get` / `task log` / `task report` 的底层读接口仍可能保留完整 locator 作为兼容排障能力；主链路不使用。

---

## 3. 步骤说明与命令模板

### 3.1 `task_list`（`task list`）

```bash
qingflow --json task list \
  --task-box todo \
  --flow-status all \
  --page 1 \
  --page-size 50 \
  > tmp/qingflow_tasks_todo.json
```

- `**--task-box**`：`todo`（待办）、`done`（已办）、`cc`（抄送）、`initiated`（我发起）等；与 `**--flow-status**`（箱内流程状态）为 **两个独立维度**，可同一次请求带给后端。
- `**--query`**：优先走后端检索；若后端零条，公开列表可能 **本地回退**匹配应用名、节点名、`app_key`、`record_id`（JSON 中可能出现 `TASK_LIST_QUERY_FALLBACK_APPLIED` 类警告）。
- `**--app-key`**：列表阶段 **常省略**（不按应用过滤）；与下钻阶段不同。

从 `data.items[]` 取 `**task_id`** 进入下一步。

### 3.2 `task_get`（`task get`）

```bash
qingflow --json task get \
  --task-id "<TASK_ID>" \
  > tmp/qingflow_task_get.json
```

可选（默认开启，大响应可关）：`--no-include-candidates`、`--no-include-associated-reports`。

**解析要点**（以 CLI `--json` 紧凑载荷为准，字段名以你环境实际 JSON 为准）：

- `**data.task`**：`app_key`、`record_id`、`workflow_node_id`、`workflow_node_name`、`actionable`、`task_id`。
- `**data.available_actions`**：当前节点 **允许** 的动作子集（**下文 `task action` 的 `--action` 必须落在此列表中**，否则 CLI 报 config）。
- `**data.editable_fields`**：可编辑字段（与 `**save_only`** 等配合）。
- `**data.extras**`：摘要信息，例如 `**workflow_log**`（是否可见、条数提示等）、`**associated_reports**`（`count`、`items[]`，每项含 `**report_id**` / `chart_key` / `chart_name` 等）。

### 3.3 `task_workflow_log_get`（`task log`）

```bash
qingflow --json task log \
  --task-id "<TASK_ID>" \
  > tmp/qingflow_task_log.json
```

- 典型结构：`data.items[]` 含节点、操作者、`operation`、`operation_time`、备注与附件等（具体字段以后端为准）。
- `**data.visibility**`：审计/机器人日志可见性等元数据。
- 这不是记录详情页的全量数据日志工具；如果用户要某条记录的完整数据日志 + 流程日志，先定位 `app_key/record_id/view_id`，再用 `qingflow --json record logs ...`。

### 3.4 `task_associated_report_detail_get`（`task report`）

1. 在 `**task get**` 的 `**data.extras.associated_reports.items**` 中选一条，读取其 `**report_id**`（整数）。
2. 若 `**count == 0**`，跳过本步，无 `**--report-id**` 可填。

```bash
qingflow --json task report \
  --task-id "<TASK_ID>" \
  --report-id <REPORT_ID> \
  --page 1 \
  --page-size 20 \
  > tmp/qingflow_task_report.json
```

- 定位方式与 `task get` 相同：默认传 `task_list.data.items[].task_id`。
- 若关联项是 QingBI 报表，详情读取优先走前端同源的 **`/qingbi/charts/data/qflow/{chartId}/detail`**，再按 qflow `asos` 降级；只有 qflow 路由明确不存在/不适用时才退回旧 BI 数据接口。不要把中间 **`CHART_SEE` / 40002** 当成任务关联报表最终不可见。

### 3.5 `task_action_execute`（`task action`）

```bash
qingflow --json task action \
  --task-id "<TASK_ID>" \
  --action <ACTION> \
  [--payload-file tmp/task_action_payload.json] \
  [--fields-file tmp/task_action_fields.json] \
  > tmp/qingflow_task_action.json
```

`**--action` 允许字面量**（实现校验，大小写不敏感）：
`approve`、`reject`、`rollback`、`transfer`、`urge`、`save_only`。

**约束摘要**（与实现一致）：

- **定位只认 `task_id`**：来自 `task list` 的 `data.items[].task_id`；`app_key`、`record_id`、`workflow_node_id` 不是动作执行入参。
- `**approve` / `reject`**：执行上下文以当前待办详情或用户/前端已给出的显式 `formId` 为准；只有缺少 `formId` 时才兜底读取应用 baseInfo。不要把应用 baseInfo 的 `40002` 当作待办动作最终无权结论，最终是否可执行以后端审批动作接口为准。
- `**save_only`**：必须 提供非空 `**--fields-file`**（或 payload 与 fields 不能同时塞 `answers` 与 fields，具体以报错为准）。以当前待办节点的 `data.editable_fields` / `editableQueIds` 为准；若 `editableQueIds` 被当前权限链路挡住，但任务详情里的 `queAuthSetting` 已暴露可编辑字段，CLI 会按任务详情继续允许 save-only，并由最终保存接口裁决。申请表单 schema 或辅助 `editableQueIds` 的 `40002` 不是待办字段保存的最终无权结论。
- `**transfer**`：`**payload` 内需要** `target_member_id`（或别名 `uid` / `targetMemberId`）；不能转给当前登录人。未提供 `payload.answers` 且没有通过 `--fields-file` 修改字段时，CLI 会先读取当前待办详情，并将已有 `answers` 原样带入转交请求；显式 `payload.answers` 或 `--fields-file` 合并结果优先。
- **意见必填**：若详情里 `**action_constraints.feedback_required_for`** 包含当前动作，需在 `**payload.audit_feedback`**（实现从 payload 抽取审计意见，具体键名以 `--help` / 服务端为准）中提供，否则会 config 错误。
- `**urge`**：**不支持** 与 `fields` 同时提交。
- **禁止臆测动作**：只允许 `**data.available_actions`** 中出现的动作；`approve` 不在列表则不可硬放行。

`**--payload-file` / `--fields-file`**：UTF-8 JSON 对象，与 `record update` 同类「文件用 JSON」习惯一致。

---

## 4. 与「应用内 `record list`」的边界

- **任务中心待办 / 已办 / 抄送**：用 `**task list --task-box …`**，**不要**再用过时的 `record list --view-id system:todo` 等当作任务箱。
- **业务表读数**：仍在 `app get` 的 `**accessible_views`** 里选 `**custom:`* 等**，走 [QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md](../core/QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md)。

---

## 5. 实测与排障（编写时实跑）


| 命令                                      | 结果                                                                                                                                                          |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `task list --task-box todo`             | 返回多条，`items[].task_id` 为字符串；列表项可能不含 `app_key`（详情阶段再解析）。                                                                                                     |
| `task get --task-id …`                  | `data.task` 含完整定位；`available_actions` 示例含 `approve`/`reject`/`rollback`/`transfer`；`extras.associated_reports` 可为 `count: 0` 或大于 0。                         |
| `task log --task-id …`                  | 返回 `data.items` 审批/流程历史。                                                                                                                                    |
| `task report --task-id … --report-id …` | 某条 `**count>0`** 的抽样上曾返回后端 `**40038` Object not exist**；同一 `task get` 里仍列出 `report_id`。**建议**：换 `report_id`、确认报表未删除、核对轻流 BI 权限与节点关联；仍失败时保留 `request_id` 报障。 |


**说明**：本文编写时仅用读接口抽样校验；`**task action`** 可依照 **第 3.5 节** 在自动化剧本中直接调用，由编排侧控制目标待办与动作，避免误批。

---

## 6. 交叉引用

- 主技能 [SKILL.md](../../SKILL.md)：**落盘规则**、`**task-box` / `flow-status`** 枚举、与 `record` 混用雷区。
- [QINGFLOW_CLI_MEMBER_CHEATSHEET.md](../core/QINGFLOW_CLI_MEMBER_CHEATSHEET.md)：成员侧最短路径。
