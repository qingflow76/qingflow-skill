---
name: qingflow-cli
description: |
  【强制】在执行或编排任何 qingflow CLI 命令前必须优先加载本 Skill。
  Qingflow CLI 包以本 Skill 作为 CLI 主入口；record/app-builder/task/workflow 等相关说明按场景组织在 reference 子目录。
  指导安装、执行上下文失败恢复、查询与写入；规定 task/record/import/builder 查询落盘；覆盖普通成员读数、字段 kind 与数据形态、任务上下文、批量导入、record access/list/get/insert/update/delete 与管理端边界。
  Builder SOP 按智能体任务路径组织：完整系统、单应用、AppForm、视图、报表、门户、关联资源、流程、发布校验；表单字段、分组、布局和应用设置统一使用 versioned AppForm；按钮随视图 action_buttons 声明；更新动作并入对应资源文档，批量读/批量写/局部改作为资源文档内的写法变体；明细见「关联文件」表与文末命令索引。
---

# Qingflow CLI 使用技能

> **Skill 版本**：`qingflow-skills-2026.07.01.04`（入口文档版本；CLI 包版本用 `qingflow --version`；需要定位版本漂移时用 `qingflow --json version` 读取 `version/package/command_path/executable_path/package_root/skill_version`）。

Use [$qingflow-common](../qingflow-common/SKILL.md) first when choosing between CLI and MCP. This Skill owns command-line invocation, JSON-file handling, and CLI-only validation; it does not redefine the underlying AppForm, record, task, or builder business contracts.

**硬约束（必读）**：正文各节与文末「命令速查」中的命令**只作子命令形态索引**，不覆盖 JSON 结构、`--*-file` 键名、枚举全集、执行顺序与排障细节。凡工作**偏复杂**（多步串联、大块 payload、导入全链、**Builder 搭建向**（应用/schema/流程/布局/视图/门户/报表/按钮/关联资源的配置与发布、系统列与字段 `type`）、契约型 `apply`、按 schema 组织写入 payload、任务下钻与 `task action` 等），或你判断当前任务与「关联文件」里某篇所描述的内容**需求一致、场景相同或大体同类**，都应**先 Read 对应 `reference/...` 文档**，再结合 `qingflow … --help` 与 **[EXPLORATION_REPORT](./reference/core/QINGFLOW_CLI_EXPLORATION_REPORT.md)**。**禁止**仅凭索引、习惯或类比去补参数、臆造字段名或推断服务端行为。**CLI 自动化场景只通过 `qingflow` 命令工作**；相关说明已按主题合并为本文档下的 `reference/` 子目录。**最终统计结论、分析报告、趋势/排名/比例/分布**统一走 **[record/analysis](./reference/record/analysis/README.md)** 的 `qingflow record access -> Python/pandas`。

> **CLI**：当前实际执行包以 `qingflow --json version` 返回的 `package / version / command_path / executable_path / package_root / skill_version` 为准；不要从安装文档或全局 npm 目录猜版本。人工快速查看可用 `qingflow --version`。**复杂任务先读 [reference/00-INDEX.md](./reference/00-INDEX.md)**。**搭建/创建/系统配置**：先区分 **完整系统/应用包** 与 **单应用**。应用表单、字段、分组、行布局和应用设置统一使用 versioned AppForm：先执行 `qingflow --json builder app-form schema` 固定版本；更新前执行 `qingflow --json builder app-form get --app-key APP_KEY --being-draft`；每次写入前执行 `qingflow --json builder app-form validate --schema-version VERSION --file DECLARATION.json`，再执行 `qingflow --json builder app-form apply --file DECLARATION.json`。不要调用已移除的 `builder schema apply` / `builder layout apply`，也不要把旧 `--apps-file` / `--form-file` 当成当前主路径。完整系统先 `builder package apply`，再逐个 AppForm 创建并记录每个 `appKey`，最后用已确认的 app keys 配置关系、视图、门户和流程。门户需要新报表时在 portal section 写 `chart`，不要把报表创建拆成完整系统主步骤。AppForm apply 超时、`partial_success`、`write_executed=true`、`safe_to_retry=false` 或回读不完整时，下一步固定是读取 draft/published form 后再恢复，禁止重复创建或用 V2/测试/随机后缀绕过重名；随后按 **[builder/README.md](./reference/builder/README.md)** 选择具体资源文档。仅成员读数速通仍可先打开 **[MEMBER_CHEATSHEET](./reference/core/QINGFLOW_CLI_MEMBER_CHEATSHEET.md)**。

## 关联文件


| 文件                                                                                               | 说明                                                                                                                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------------ |---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `manifest.yaml`                                                                                  | 技能清单                                                                                                                                                                                                                                                                                  |
| [reference/00-INDEX.md](./reference/00-INDEX.md) | **总导航**：按用户目标选择 record / task / builder 文档；复杂任务先读 |
| [reference/QINGFLOW_CLI_MEMBER_CHEATSHEET.md](./reference/core/QINGFLOW_CLI_MEMBER_CHEATSHEET.md)     | **普通成员**主线：最短路径、`view_id`、与管理命令的差异预期                                                                                                                                                                                                                                                  |
| [reference/QINGFLOW_CLI_FIELD_DATA_TYPES.md](./reference/core/QINGFLOW_CLI_FIELD_DATA_TYPES.md)       | **字段数据类型**：`record schema …` 的 `fields[]`（`field_id`、`title`、`kind`、`options`…）；`record list/get/access` 与写入 payload 的形态对照                                                                                                                                                                    |
| [reference/QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md](./reference/core/QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md) | **应用记录获取数据**：`app get`（`accessible_views`）→ `record schema browse` → `record list(query)` 模糊定位 / `record get` 详情页首屏上下文 / `record logs` 全量日志；分析取数转 `record_access`                                                                                                                                                                        |
| [reference/QINGFLOW_CLI_TASK_CONTEXT_WORKFLOW.md](./reference/task/QINGFLOW_CLI_TASK_CONTEXT_WORKFLOW.md) | **任务(待办已办)上下文 SOP**：`task list` → `task get` → `task log` → `task report` → `task action`；只把 `task_id` 作为主定位参数                                                                                               |
| [reference/QINGFLOW_CLI_RECORD_IMPORT_WORKFLOW.md](./reference/record/QINGFLOW_CLI_RECORD_IMPORT_WORKFLOW.md) | **批量导入 SOP**：`app_get`（**`import_capability`**）→ `record_import_template_get` → `record_import_verify` →（可选）`record_import_repair_local` → `record_import_start` → `record_import_status_get`；CLI `import` / `record schema import`                                                   |
| [reference/builder/README.md](./reference/builder/README.md) | **Builder 总导航**：完整系统、单应用、字段、布局、视图、报表、门户、按钮/关联资源、流程、发布校验 |
| [reference/builder/10-build-single-app.md](./reference/builder/10-build-single-app.md) | **单应用搭建主入口**：一个应用端到端交付顺序 |
| [reference/builder/20-build-complete-system.md](./reference/builder/20-build-complete-system.md) | **完整系统/应用包主入口**：多应用、跨应用 relation、门户闭环 |
| [reference/builder/30-schema-fields.md](./reference/builder/30-schema-fields.md) | **字段 / schema**：字段类型、直觉别名、数据标题/封面、schema 创建与更新 |
| [reference/builder/40-layout.md](./reference/builder/40-layout.md) | **布局维护**：仅用于已有应用的分组、`rows` 矩阵、布局修复；新建应用布局写在 `form` 内 |
| [reference/builder/50-views.md](./reference/builder/50-views.md) | **视图**：表格/卡片/看板/甘特、固定筛选、查询面板、视图 patch |
| [reference/builder/60-charts.md](./reference/builder/60-charts.md) | **报表 / QingBI**：指标卡、图表、语义聚合、筛选、排序、更新 |
| [reference/builder/70-portal.md](./reference/builder/70-portal.md) | **门户**：标准工作台、业务入口、指标、图表、视图组件、发布 |
| [reference/builder/80-buttons-associated-resources.md](./reference/builder/80-buttons-associated-resources.md) | **关联资源 / 非主链路按钮维护**：关联视图/报表、`match_mappings`、上下文传参；按钮配置看视图文档 `action_buttons` |
| [reference/builder/90-workflow.md](./reference/builder/90-workflow.md) | **流程**：WorkflowSpec、`patch_nodes`、角色/成员、流程回读 |
| [reference/builder/99-publish-verify.md](./reference/builder/99-publish-verify.md) | **发布与回读**：`publish verify`、partial/readback 处理、最终汇报口径 |
| [reference/QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md](./reference/record/QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md) | **新建记录**：`record schema insert -> record insert --items-file`；成员/部门/关联优先自然语言输入；细节见 [record/insert](./reference/record/insert/README.md) |
| [reference/QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md](./reference/record/QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md) | **更新记录**：主链路是 `record get` → 智能体按 `fields[]` 组 key/value → **`record update`**；`record schema update` 仅用于失败后诊断可写字段/路径                                                                                                                                 |
| [reference/QINGFLOW_CLI_RECORD_DELETE_WORKFLOW.md](./reference/record/QINGFLOW_CLI_RECORD_DELETE_WORKFLOW.md) | **删除记录**：`record list/get` 精确定位 → `record delete --app-key --record-id --view-id system:*`；批量用 `--record-ids-file` |
| [reference/record/analysis/README.md](./reference/record/analysis/README.md) | **数据分析**：最终统计结论、分析报告、趋势/排名/比例/分布统一走 `record access -> Python/pandas` |
| [reference/builder/reference/app-delivery-sop.md](./reference/builder/reference/app-delivery-sop.md) | **底层交付参考**：历史完整 SOP、权限、系统列和工具细节；不是主入口 |
| [reference/builder/reference/workspace-icons.md](./reference/builder/reference/workspace-icons.md) | **图标参考**：`builder icon catalog`；新建应用包、应用、门户必须显式选择非 `template` 的 `icon + color` |
| [reference/builder/reference/match-rules.md](./reference/builder/reference/match-rules.md) | **统一筛选 / 条件写法**：`filters`、`visible_when`、QingBI 图表筛选、工作流条件、`match_mappings`、`field_mappings` 的 `operator/value` 规则 |
| [reference/builder/workflow/README.md](./reference/builder/workflow/README.md) | **工作流搭建**：已有应用的流程建模、节点配置、`builder flow apply` 与 `patch_nodes` |
| [reference/builder/code-integrations/README.md](./reference/builder/code-integrations/README.md) | **代码块 / Q-Linker 配置**：字段别名、绑定、输入字段插入和配置排障 |
| [reference/QINGFLOW_CLI_ADMIN_CHEATSHEET.md](./reference/core/QINGFLOW_CLI_ADMIN_CHEATSHEET.md)       | **管理员**：检索、导入等与成员差异（主技能正文不展开）                                                                                                                                                                                                                                                         |
| [reference/QINGFLOW_CLI_EXPLORATION_REPORT.md](./reference/core/QINGFLOW_CLI_EXPLORATION_REPORT.md)   | CLI 实测与 argparse/服务端对齐备忘                                                                                                                                                                                                                                                              |
| [reference/QINGFLOW_CLI_ONE_SHOT_CHEATSHEET.md](./reference/core/QINGFLOW_CLI_ONE_SHOT_CHEATSHEET.md) | **可选**：全角色「一次可复制」分项模板；默认执行技能**不必**打开                                                                                                                                                                                                                                                  |
| [scripts/find-app-by-keyword.py](./scripts/find-app-by-keyword.py)                               | **旧版 CLI 兼容脚本**：当 `app list --query` 不可用时，用 `app list` 本地解析；默认优先使用 `qingflow --json app list --query <关键词>`                                                                                                                                                                          |
| [scripts/builder-package-from-app-list.py](./scripts/builder-package-from-app-list.py)           | **旧版 CLI 兼容脚本**：当 `builder package list` 不可用时，才从 `app list` 曲线反查 **`package_name` / `resolve-id`**；新版默认直接用 `qingflow --json builder package list --query <关键词>`                                                                                                                    |

**Builder 删除回读语义**：删除类 apply 要区分 **DELETE 是否已发出** 和 **删除是否已回读确认**。若结果里有 **`delete_executed=true`**，但 **`readback_status=unavailable|still_exists`**，不要盲目重复删除；记录 **`safe_to_retry_delete=false`**，稍后用对应读取工具确认。

**Builder 写后回读语义**：`package apply/update`、`app-form apply`、`portal apply`、`charts apply` 以及其它 builder apply 若返回 **`status=partial_success`** 且 **`write_executed=true` / `safe_to_retry=false`**，表示写动作已经发出或已成功，后续回读/发布校验可能被 40002、404、超时或元数据延迟阻挡。此时不要把结果解读为“未写入”；下一步是 **`readback_before_retry`**，AppForm 先读 draft/published form，再只修复确认的差异；最终说明按 `verification.readback_unavailable`、`details.*readback_error`、`summary.write_executed` 组织。禁止未经读回就重放创建、拆成单应用重建、创建 V2/测试/随机后缀应用，或猜测未确认的 `appKey`。

**Builder contract 读取路径**：`qingflow --json builder contract --tool-name ...` 成功时，真实契约固定在 **`$.contract`**；优先读返回的 **`json_paths`**。`allowed_keys` 是 `$.contract.allowed_keys`，`allowed_values` 是 `$.contract.allowed_values`，且 allowed_values 使用 **扁平 dotted key**，例如 `["field.type"]` / `["chart.chart_type"]`，不是嵌套对象。成功响应顶层 `allowed_values` 通常为空，不要从顶层取字段枚举。`builder icon catalog` 的候选固定读 `$.icon_names` / `$.icon_colors`。

**Builder apply 输出读取路径**：`package/schema/views/charts/portal` 等 builder apply 成功或 partial 时，优先读返回的 **`json_paths`**；稳定主路径是 `$.summary` 与 `$.resources[]`。资源 ID/key/name 先看 `$.resources[].id/key/name`；写入状态先看 `$.write_executed`、`$.safe_to_retry`、`$.next_action`，再看 `$.summary.write_executed` / `$.summary.safe_to_retry`。旧字段只作兼容或 debug。

**0 字节输出**：写入类命令如果目标文件或捕获 stdout 为 0 bytes，不要按成功或失败二选一猜测；标记为 **`write_state_unknown`**，先做对应读回（如 `builder app get` / `portal get` / `record get` / `record list`）再决定是否重试。只要读回显示资源已创建/更新，就按成功路径汇报；读回证明缺失时才重试最小缺失项。在 CLI repo 或测试 harness 中，可用 `python scripts/validate_qingflow_output_files.py --glob 'tmp/*.json'` 扫描 0 bytes / 非 JSON 输出。

---

## 安装

> 仅qingflow命令执行后发现不可用再安装，不需要进行校验动作

```bash
npx qingflow-cli@latest install
```

安装器会安装真实 CLI 包 `@qingflow-tech/qingflow-cli@latest`；会预检 Node.js、npm、Python 3.11+；若全局 npm 目录权限不足，会 fallback 到用户目录（macOS/Linux 为 `~/.local`，Windows 为用户 AppData npm 目录）并提示 PATH 配置，不会自动改 shell 文件。排障可加 `--verbose`。环境：Node.js v16+、npm、Python 3.11+、可达 npm registry / 轻流 API。

---

## 执行上下文准则（认证仅作失败恢复）

目标是 **少一次无用往返**、**先解决业务**、**再根据失败类型补鉴权**。

1. **不要**在每次任务开头固定执行 `qingflow --json auth whoami`「先验一遍是否登录」。假定 `default` profile **已持久化登录**（或由剧本先完成 `auth use-credential` / `auth login`）。
2. **优先直接执行业务读/写**（如下文 **落盘规则** 带好重定向）：例如 `app list` → `app get` → `record list`/`task list`。
3. **仅当**业务命令返回明确 **未登录 / session 无效 / `Profile '…' is not logged in` / 401** 时，再执行：
  - `qingflow auth use-credential …` 或 `qingflow auth login …`（`--base-url "$QINGFLOW_BASE_URL"`）；成功后再 **重试原业务命令**，而不是先绕一大圈。
  - 必要时 `qingflow --json auth whoami` **核对**账号与 `selected_ws_id`。
4. **仅当**业务失败且症状像 **租户/工作区不对**（数据空、明显越权）时，再使用 `workspace list` / `workspace get` / `workspace select`。**读应用内记录不依赖**前置 `workspace get`；且 `workspace select` 在部分环境会遇 **59004**（流币/AI 配额），与「没登录」区分。
5. 与 **普通成员读数最短路径**（下节）一致：能 2～3 步调通就不要先堆 5～6 步调身份。

**安全**：密码、credential **只走 stdin / 环境变量**，禁止写进命令行历史。

---

## 失败恢复时的认证方式

凡带 `--base-url` 的认证，在环境已配置时 **必须** 使用环境变量 `\`"$QINGFLOW_BASE_URL"\``（勿省略引号以避免空值/word-split），勿写死域名。

### 方式 A：Credential（自动化推荐）

```bash
echo "$QINGFLOW_CREDENTIAL" | qingflow --profile default auth use-credential \
  --base-url "$QINGFLOW_BASE_URL" \
  --credential-stdin \
  --persist
```

### 方式 B：交互式登录

```bash
qingflow auth login \
  --base-url "$QINGFLOW_BASE_URL" \
  --email "user@example.com" \
  --password-stdin \
  --persist
```

### 核对会话（排障用，非例行首步）

```bash
qingflow --json auth whoami
```

常用参数：`--credential-stdin`、`--password-stdin`、`--persist` / `--forget-persisted`；详见 `qingflow auth --help`。

---

## 输出落盘规则（task / record / import / builder 查询类）

以下 **必须** 将标准输出重定向到文件（如 `tmp/qingflow_*.json`），**禁止**把终端大 JSON 直接交给 LLM；后续用读文件 / 脚本处理。


| 子系统        | 必须落盘的子命令                                                                                                                                                            |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **task**   | `list`、`get`、`log`、`report`                                                                                                                                         |
| **import** | `template`、`verify`、`repair`、`start`、`status`（**`verify` / `start` 链依赖本机 `~/.qingflow-mcp` 校验/任务落盘，自动化须开放写权限**） |
| **builder** | **`app get`（summary/app map、fields、layout、views、flow、charts；summary 含 `custom_buttons` / `associated_resources`）**、`contract`、`app-form schema/get/validate/apply`；以及 **`views apply` / `button apply` / `associated-resource apply` / `flow apply` / `charts apply` / `portal apply` / `portal delete` / `publish verify` / `package apply`** 等大 JSON 响应 |
| **record** | `list`、`get`、`logs`、`access`、`schema browse`；以及 `schema insert` / `schema update` / `schema import` / `schema code-block` 等大体积 schema 子命令（体量大时同上）；**创建前列字段时用 `schema insert` / `record_insert_schema_get` 同上**；**写操作 `insert` / `update` 响应体大时同样建议落盘** |


**规则摘要**

- 重定向示例：`qingflow --json record list … > tmp/qingflow_records.json`
- 线上真实测试、子智能体并行任务、批量 `--*-file` 入参优先使用**绝对路径**，或在命令前固定确认 `pwd`；不要假设子智能体当前目录与主线程一致。
- `auth`、`workspace`、`app`、`portal`、`view`、**非上述列出的**等，可直接终端查看或按需落盘。
- 错误在使用 **`--json`** 时多在 **stdout** 的 JSON 信封里；stderr 多为 argparse usage。

---

## 应用记录：获取数据工作流（推荐闭环）

与常见 **编排/API 文档**里的命名对齐时的固定顺序为：

1. **`app_get`**：`qingflow --json app get --app-key <APP_KEY>` → 在 **`data.accessible_views`**（或等价路径）选取 **`view_id`**。
2. **`record_schema_get`（`schema_mode=browse`）**：`qingflow --json record schema browse --app-key <APP_KEY> --view-id <VIEW_ID>`（CLI 子命令 **`browse`** 即浏览视图表结构）。
3. **`record_list` / `record_get` / `record_logs_get`**：`record list …` 用于样本浏览或模糊定位候选；`record get --record-id …` 下钻单条前端详情页首屏上下文（字段、首屏日志、引用、图片与文件资产）；只有需要完整审计历史时，再用 `record logs --record-id …` 读取全量数据日志和流程日志 JSONL。

`app get` 里的 `CUSTOM_VIEW_LIST_UNAVAILABLE` 表示自定义视图列表读取被权限或后端限制降级；若 `accessible_views` 中仍有 `system:*`，可继续用该视图读数。若没有任何视图，再回到前端 URL、`app list` 可见应用、或用户提供的 `viewgraphKey` 补充上下文，不要直接断言应用不可读。
`app get.data.can_create=false` 才表示 applicant/create 路径不可用；创建权限探测遇到 auth / server 等非权限类错误时应直接按失败处理，不要包装成“未知创建权限”或“用户无新建权限”。

**细则、响应解包、`view_id` 雷区与命令模板**见 **[reference/QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md](./reference/core/QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md)**（编写前已对当前 CLI **实跑**校验）。若仅需「最快看一眼有没有行」，可省略 **`schema browse`**，直接走下文「最短路径」。如果用户要任何最终统计结论、分析报告、趋势/排名/比例/分布，按 **[record/analysis](./reference/record/analysis/README.md)** 执行 `record access -> Python/pandas`。

---

## 应用记录：创建记录工作流（申请节点 → 写入）

推荐顺序：

1. **`record schema insert`**：先读取 insert-ready schema、`required_fields`、`payload_template`、`format_hint`、`example_value`、联动与运行时必填提示。
2. **`record insert --items-file`**：单条也是 `items` 数组的一行；成员、部门、关联字段优先写自然语言（如 `"张三"`、`"直销部"`、`"海军军医大学"`），仅在返回 `needs_confirmation` 时再让用户确认候选。
3. **写后读回**：单条重要数据用 `record get`，批量样本用 `record list` 或业务视图校验；`partial_success` 只重试失败行，不重放全批。

**细则、字段 JSON 结构与排障**见 **[reference/QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md](./reference/record/QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md)**。

---

## 应用记录：更新记录工作流（详情 → 写入）

主链路是先读详情，再直接提交用户要求修改的 key/value。不要把 `record schema update` 当成更新前置步骤：

1. **`record get`** → 拿 **`record_id`、当前值、fields[].title / field_id / kind**；已知前端/自定义视图时必须带同一个 **`--view-id`**。未知时 CLI 会先试默认 `system:all`，权限拒绝后再尝试可访问视图，但智能体仍优先从 `app get.accessible_views` 取 view。
2. 智能体根据 `record get.fields[]` 和用户要求，组一个只包含待改字段的 JSON 对象（标题 → 值）。字段必须来自当前详情上下文的 `fields[]`；带 `--view-id` 时，视图隐藏的字段不要强写。若用户要求改的字段不在当前 `record get.fields[]`，先换到包含该字段的视图/详情上下文，或用 `record schema update` 做失败诊断。
3. **`record update`** → **`--record-id` + `--fields-file`**，已知前端视图时同样带 **`--view-id`** 让 CLI 优先走该 view；批量用 **`--items-file`**（**`--dry-run` 仅批量**）。
4. 只有字段范围不清、候选歧义、或 `record update` 失败时，才用 **`record schema update`** 诊断本条记录的 **`writable_fields / payload_template / available_update_routes`**；已知前端视图时同样带 **`--view-id`**，让诊断优先探测同一个详情页上下文。

**更新路径**：`record update` 会自动先尝试数据管理员直改，再 fallback 到前端同源的 custom view 详情编辑路径；如果当前用户存在这条记录的唯一待办且目标字段在当前节点可编辑，最后会尝试 workflow save-only。成功时只需要读 **`status / update_route / verification_status`**；失败时再读失败原因与路线诊断。不要把中间 route 或辅助 schema/readback 探测的 40002 / 40027 / 404 当作最终失败。

**大号 `record_id`（常见于 Snowflake 类 id）**：若干 CLI 版本在 **`record update` 写入路径**上对 `apply_id` 会做 **JavaScript 安全整数**相关校验，`list`/`get`/`schema update` 仍可能正常而 **更新落库报错**（常为 `apply_id must be positive`）。排障见 **[reference/QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md](./reference/record/QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md)**。业务统计与最终结论仍必须按 **[record/analysis](./reference/record/analysis/README.md)** 使用 `record access -> Python/pandas`。

**命令模板、批量 `items` 形态、与新建相同的写入值约定**（按 **`kind`** 分题型见 **[QINGFLOW_CLI_FIELD_DATA_TYPES.md](./reference/core/QINGFLOW_CLI_FIELD_DATA_TYPES.md)**）见 **[reference/QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md](./reference/record/QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md)**。

**成员 / 部门候选排障**：若成员、部门字段返回 `needs_confirmation` 或候选不清，使用 `qingflow record member-candidates` / `qingflow record department-candidates`；它们优先走表单字段候选范围接口（与前端选择器一致）。不要改用通讯录管理类查询去“补候选”，那会把普通成员误带到 ContactAuth 管理权限链路。

**部门名筛选 / 写入**：`record list/access/analyze/insert/update` 遇到部门字段时可直接传部门名或候选对象；CLI 会优先走成员可见的目录搜索解析部门。不要先用通讯录管理接口查询部门 id，否则普通成员容易被 ContactAuth 错误阻挡。

**目录搜索边界**：按关键词找成员/部门应优先使用成员可见搜索（如 `directory_search` 或记录字段候选工具）；部门树遍历、外部联系人完整列表、builder 成员/角色检索、通讯录管理类查询属于配置/管理向能力，普通成员无权时不要当作记录读写失败。若目录工具返回 `CONTACT_DIRECTORY_PERMISSION_DENIED`，只表示 ContactAuth/通讯录管理边界不可读；记录成员/部门字段仍应改用 `record_member_candidates` / `record_department_candidates` 或直接按字段值写入。`builder member search --query` 与 `builder role search --keyword` 都必须传明确关键词，且不要作为记录成员/部门字段候选 fallback。

**导出 / 下载 / Excel**：只有用户明确要文件时才用 `export start/direct`；导出必须显式传 **`--view-id`**，从 `app get.accessible_views` 或前端 URL 取同一个视图，省略会直接报缺少视图上下文。导出字段按前端 read/export scope 解析，不按 record update/write scope；`applicant schema`、`viewList`、`data/listBaseInfo` 等辅助字段源的 40002 只能作为降级信号，不能覆盖同一 `custom:*` view 或 `system:all`/type=8 导出链路。若状态/下载结果带 `EXPORT_HISTORY_UNAVAILABLE`，表示导出历史列表不可读；只要当前进程详情显示 `running/succeeded` 且有文件链接，就按当前进程结果继续处理，不要把历史读取 40002 当作导出失败。

**代码块运行**：`record code-block-run` 主链路是已有记录/任务详情上下文 → 传明确的 `--code-block-field`（优先字段 ID）直接运行；已知前端/custom view 时同样带 **`--view-id`**，让运行优先读取同一个详情页 answers。`record schema code-block` 只用于字段选择不清或需要查看 alias / 绑定回写配置时；若申请表单 schema 无权限，会返回 `CODE_BLOCK_SCHEMA_UNAVAILABLE` 的结构化诊断结果，不代表代码块运行无权限。运行可继续使用详情 answers，绑定回写可能跳过。

---

## 普通成员：读取记录数据「最短路径」（速通）

适用于 **`auth whoami`** 输出的 **`permission_level`** 为普通/基本成员等低权限账号；选应用使用 **`app list`** 或 **`app list --query <关键词>`**。

**调用次数**

- 从零选应用：**3 次** → `app list` → `app get --app-key` → `record list … > 文件`
- 已知 `APP_KEY`：**2 次** → `app get` → `record list … > 文件`

**写法（占位符替换后即可）**

```bash
qingflow --json app list
qingflow --json app get --app-key <APP_KEY>
# 从 JSON 中取应用对象：若存在顶层 key `data` 则先解包；在 accessible_views 中取 view_id

qingflow --json record list \
  --app-key <APP_KEY> \
  --view-id <VIEW_ID> \
  > tmp/qingflow_records.json
```

`record list` 默认最多返回 10 条，适合样本检查和模糊定位；需要更大或更小样本时用 `--page-size <N>`，但最终统计结论仍转 `record_access -> Python/pandas`。若用户只给出模糊文本，使用 `--query` 和可选 `--query-field <FIELD_ID>` 收窄候选，再用 `record get` 读详情。若用户明确要完整日志/审计历史，继续执行 `qingflow --json record logs --app-key <APP_KEY> --record-id <RECORD_ID> --view-id <VIEW_ID> > tmp/qingflow_record_logs.json`，再读取返回的 `data_logs.local_path` / `workflow_logs.local_path`。

**找应用包（Builder 管理面）**：默认直接用 **`builder package list --query <关键词>`**；它调用应用包后端 `/tag`，能看到空包、同名包和包级权限。拿到 `items[].package_id` 后再 `builder package get --package-id <ID>`。`package get` 会优先读 `/tag/{id}/baseInfo`，再尝试增强读取 `/tag/{id}`；若返回 `PACKAGE_DETAIL_READ_DEGRADED`，表示详细配置接口需要包编辑/加应用权限但基础信息已读到，不要当成包读取失败。旧版 CLI 没有该命令时，才看 **[reference/builder/reference/app-delivery-sop.md](./reference/builder/reference/app-delivery-sop.md) §2.3** 与 **[scripts/builder-package-from-app-list.py](./scripts/builder-package-from-app-list.py)**。

**按关键字找应用（成员可用）**：默认直接用 **`app list --query`**，它只读取当前用户可见应用并在本地过滤，响应看 `items[].app_key`、`matched_count`、`unfiltered_count`、`filter_mode`。

```bash
qingflow --json app list --query '发票'
# 兼容别名：
qingflow --json app list --keyword '发票'
```

若所在环境仍是旧版 CLI、`app list --query` 不存在，再使用本技能目录 **[scripts/find-app-by-keyword.py](./scripts/find-app-by-keyword.py)** 作为兼容 fallback。

### **`view_id` 要点（与成员表一致）**

- **待办 / 已办 / 抄送**：**不要**再把 `record list --view-id system:todo` / `system:done` / `system:cc` 当作 **任务中心**；该类用法已过时。任务箱一律用本节下文 **「待办 … SOP」** 中的 **`task list --task-box …`**。**应用内表格读数**仍可用 `app get` 里其它视图（例如部分环境里 **`system:all`「全部数据」**仍可用于 `record list`，与上述任务箱不是同一概念）。
- **显式 `view_id` 是前端当前视图语义**：`record list/access/schema browse/logs/export` 传了 `system:all` 就只读「全部数据」链路；若返回 40002 / 40027 / 404 / 500，不要把它自动改成 `system:initiated`、`system:todo` 等其它系统视图。需要换视图时必须重新从 `app get.accessible_views` 或前端 URL 选取。
- **`--view-id`** 仅从 **`app get`** 的 **`accessible_views`** 选取 **业务 / 自定义视图**（优先 **非「`custom:` 后仅数字」**，如带字母后缀的 `custom:…`）。
- 若 `app get.warnings` 含 **`CUSTOM_VIEW_LIST_UNAVAILABLE`**，说明 custom view 列表辅助读取不可用；已有 `system:*` 视图仍可继续使用，缺 custom view 本身不等同于应用无权。
- **禁止**把 `custom:1`、`custom:12` 等纯数字后缀自定义视图当作读数首选：成员侧常见 **`schema browse` / `record list`** 返回 **40038**。
- 读数前**不必**前置 `workspace get`、`view get`。若仅需列表可先省略 **`record schema browse`**；若要列定义或与 **「获取数据工作流」** 对齐，见 **[reference/QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md](./reference/core/QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md)**。

---

## 偏向「管理 / 高权限」的命令（普通成员常不可用或易失败）

以下为 **能力或数据面更偏管理/配置** 的路径；**普通成员**在未授权时会出现业务错误码（**非**「CLI 坏了」）：


| 区域    | 示例                                                | 典型现象（成员）                     |
| ----- | ------------------------------------------------- | ---------------------------- |
| 旧应用搜索入口  | 不使用；改用 `app list --query`                                      | `40002` 等                    |
| 导入    | `record schema import`、`import template`、`import verify`、`import start`… | `IMPORT_AUTH_PRECHECK_FAILED`、`IMPORT_*_UNAUTHORIZED`、无导入权 |
| 工作区切换 | `workspace select`                                | 可能 **59004**（配额），与未登录区分      |


**成员侧只读仍较稳**的示例：`app list` / `app get`、`portal list`。其它管理向子命令参见 **[reference/QINGFLOW_CLI_ADMIN_CHEATSHEET.md](./reference/core/QINGFLOW_CLI_ADMIN_CHEATSHEET.md)**。

---

## 典型工作流示例（含落盘）

### 待办查询

不限定应用时 **不要写死 `--app-key`**，直接落盘列举（详见下节 SOP）：

```bash
qingflow --json task list --task-box todo --flow-status all --page 1 --page-size 50 \
  > tmp/qingflow_tasks.json
```

已知 `APP_KEY` 时再收窄：

```bash
qingflow --json task list \
  --task-box todo \
  --app-key "[APP_KEY]" \
  --page 1 --page-size 50 \
  > tmp/qingflow_tasks_app.json
```

`task get` / `task log` / `task report` 同上，输出 **必须** `> tmp/...json`。

### 待办 / 已办 / 抄送处理 SOP（`task list`）

> **与编排工具名逐步对齐的独立长文**（含 **`task_workflow_log_get` / `task_associated_report_detail_get` / `task_action_execute`** 与 **`task log` / `task report` / `task action`** 对照、实测排障）：**[reference/QINGFLOW_CLI_TASK_CONTEXT_WORKFLOW.md](./reference/task/QINGFLOW_CLI_TASK_CONTEXT_WORKFLOW.md)**。
> **命令形态与参数级写法**见下文 **「命令速查 → 待办 `task`」**；本节约定 **执行顺序** 与 **是否传入 `--app-key`**。

**与前序通路区分**：若以 **待办 / 已办 / 抄送「任务箱」** 为目标，**须**按本节下文 **「待办 / 已办 / 抄送处理 SOP」** 使用 `**task list --task-box …`**； `**record list` + `system:todo`、`system:done`、`system:cc` 等 `view_id` 已过时，不作为推荐**。`record list` 用于 **应用内业务视图**：在 `**app get**` 的 `accessible_views` 中取可用的 `**custom:***` 等 `**--view-id**`，与本节 SOP 勿混为一谈。

`**--task-box` 取值（小写）**


| 业务箱      | `--task-box` | 备注                            |
| -------- | ------------ | ----------------------------- |
| 待办       | `todo`       | **默认**：省略 `--task-box` 等价于待办箱 |
| 已办       | `done`       |                               |
| 抄送       | `cc`         |                               |
| 我发起的（可选） | `initiated`  | CLI 合法值；按需使用                  |


#### `task-box` 与 `flow-status` 的区别（与实现 / 接口对齐）

二者是 **两个独立维度**，在一次 `task list` 里 **同时** 带给后端（`POST /task/dynamic/page` 的 JSON 体字段为 `**type**` 与 `**processStatus**`），不要二选一理解。

- `**--task-box` → `type`（任务箱）**：只看 **哪一类收件箱**——与本账号的关系维度（待办 / 我发起 / 抄送 / 已办）。
- `**--flow-status` → `processStatus`（流程状态筛选项）**：在 **已选定任务箱内** 再按 **流程进度、时效、是否未读** 等过滤；默认 `**all**`（`processStatus = 1`）表示本维度不减条件。

合法 `**task-box` → type**（小写，`--task-box` 省略时等价 `todo`）：


| `--task-box` | `type` | 语义（源码类注释一致） |
| ------------ | ------ | ----------- |
| `todo`       | 1      | 待办，需当前用户处理  |
| `initiated`  | 2      | 我发起的        |
| `cc`         | 3      | 抄送          |
| `done`       | 5      | 已办          |


合法 `**flow-status` → processStatus`**（CLI 报错信息中的英文关键字与此一致）：


| `flow-status` | processStatus | 语义   |
| ------------- | ------------- | ---- |
| `all`（默认）     | 1             | 全部   |
| `in_progress` | 2             | 流程中  |
| `approved`    | 3             | 已通过  |
| `rejected`    | 4             | 已拒绝  |
| `pending_fix` | 5             | 待完善  |
| `urged`       | 6             | 催办   |
| `overdue`     | 7             | 超时   |
| `due_soon`    | 8             | 即将超时 |
| `unread`      | 9             | 未读   |
| `ended`       | 10            | 流程结束 |


**勿把记录列表的 `list_type`（或过时文档里的 `system:*` 视图口径）与任务中心的 `type` 混为一谈**：`task list --task-box …` 的映射见上表（例如任务中心「已办」为 `type=5`）；**不要**再把旧表单视图侧的编号抄到 `**--task-box`** 或自行拼接请求 `type`。

更深的行为差异与踩坑备忘仍见 **[reference/QINGFLOW_CLI_EXPLORATION_REPORT.md](./reference/core/QINGFLOW_CLI_EXPLORATION_REPORT.md)**。

#### `--query`（列表检索与回退）

`qingflow task list --help` 中与实现一致：**先走后端待办检索**（请求体中为 `searchKey`）；当 **后端返回零条** 时，公开 `**task_list` 可能对当前页结果做本地匹配**（字段涉及应用名、节点名、`app_key`、`record_id` 等）。若走 JSON/`--json` 信封且触发了该路径，响应中可出现 `**TASK_LIST_QUERY_FALLBACK_APPLIED`** 类提示——**不等于**后端无权限，解析列表前先看 `warnings`。

**标准流程**

1. **列表（必须落盘）**
  - **未显式掌握 `APP_KEY`**：不要硬编应用；直接执行（按需将 `--task-box` 设为 `todo` / `done` / `cc`）：
   `qingflow --json task list --task-box <todo|done|cc> --flow-status all --page 1 --page-size 50 > tmp/qingflow_tasks_<箱名>.json`
   `**--app-key` 整段省略**——与速查表「`task` 列表」一致：`--app-key` 非必须，由后端返回当前会话可见的任务页。
  - **已知或已从业务收窄到单应用**：在同上命令末尾追加 `--app-key <APP_KEY>`（`APP_KEY` 来自 `**app list` → `app get`**，与普通成员最短路径一致）。
  - 可选 `**--query**`：语义见上节「`--query`」；零条时可能是真无数据，也可能是未触发回退或关键词不匹配。
  - **排序**：当前 `**qingflow task list` CLI 无 `--sort-by` / `--sort-direction`**；勿编造排序类参数。
2. **从列表下到详情 / 日志 / 报表 / 动作**
  - **唯一默认路径**：列表 JSON 中取 `**task_id`**，使用 `**--task-id**`；它必须来自 `data.items[].task_id`，不是列表序号、record_id 或 workflow_node_id。示例：
   `qingflow --json task get --task-id <TASK_ID> > tmp/qingflow_task_get.json`
  - **不要自行凑三键**：`app_key / record_id / workflow_node_id` 只用于用户已明确提供完整 locator 的排障场景；普通执行不要从其它输出里猜。
  - `**task report`**：除定位参数外 **必须** `--report-id`；支持 `**--page` / `--page-size`** 分页（见速查表）。
  - 与「列表可省略 `--app-key`」不同：下钻单条默认必须有 `**task_id**`。
  - `save_only` 可用性优先看当前节点 `editableQueIds`；只有该辅助接口 40002 / 40027 / 404 时才降级使用当前待办详情的 `queAuthSetting`，非权限类错误不要当成“节点不可保存”。
  - 评论提及、退回候选、转交候选等辅助候选接口只有 40002 / 40027 / 404 可视为候选不可用；500 / auth 等非权限错误不要包装成权限边界。
3. **排查**
  - 某一箱 `**items` 为空但 exit 0**：常为真实无数据，可换 `--task-box` 或分页；若在「omit `app_key`」下发散且仍空，再用 `**app list`/`app get`** 确认是否在正确应用与工作区再看是否需补 `--app-key`。
  - 未登录、权限错误：回到上文 **鉴权行为准则**，先重试业务再补鉴权。

### 记录：表结构、列表、分析取数

多级子命令 **不要** 整体加引号；`record list` / `record access` **运行时必须** `--view-id`（从 `app get` 的 `accessible_views` 取）。最终统计结论、分析报告、趋势/排名/比例/分布必须按 **[record/analysis](./reference/record/analysis/README.md)** 使用 `record access -> Python/pandas`。

```bash
qingflow --json record schema browse \
  --app-key "[APP_KEY]" --view-id "[VIEW_ID]" \
  > tmp/qingflow_schema.json

qingflow --json record list \
  --app-key "[APP_KEY]" --view-id "[VIEW_ID]" \
  > tmp/qingflow_records.json

qingflow --json record access \
  --app-key "[APP_KEY]" --view-id "[VIEW_ID]" \
  --columns-file tmp/columns.json \
  --where-file tmp/where.json \
  > tmp/qingflow_record_access.json
```

### 危险操作（节选）


| 命令                     | 备注                                                                     |
| ---------------------- | ---------------------------------------------------------------------- |
| `task action`          | **无 `--dry-run`**，执行即生效                                                |
| `record delete`        | **无**安全开关                                                              |
| `record insert/update` | 可用 `--verify-write`；`record update --dry-run` **仅批量**且需 `--items-file` |


更多见 **[reference/QINGFLOW_CLI_MEMBER_CHEATSHEET.md](./reference/core/QINGFLOW_CLI_MEMBER_CHEATSHEET.md)**；**管理向**（检索/导入等）见 **[reference/QINGFLOW_CLI_ADMIN_CHEATSHEET.md](./reference/core/QINGFLOW_CLI_ADMIN_CHEATSHEET.md)**。

`record delete` 必须传可访问的系统 `--view-id system:*`；删除前可用 custom/system view 的 `record list/get` 精确定位 record_id，但真正删除提交不要传 `custom:*`、`list_type`，也不要省略系统视图上下文。完整规则见 **[RECORD_DELETE](./reference/record/QINGFLOW_CLI_RECORD_DELETE_WORKFLOW.md)**。

### 注销

```bash
qingflow auth logout --forget-persisted
```

---

## 常见失败与处理


| 迹象                                                               | 处理                                                                                                                                      |
| ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| 未登录 / profile 未登录                                                | **再**走「认证方式」节，重试业务命令                                                                                                                    |
| `record_list requires view_id`                                   | 先 `app get --app-key`，取 `view_id`                                                                                                       |
| JSON 内 `backend_code` / `error_code`                             | 区分配额、权限与参数错误；普通成员见上节「偏向管理」；非本技能速查表覆盖的报错见 **[reference/QINGFLOW_CLI_ADMIN_CHEATSHEET.md](./reference/core/QINGFLOW_CLI_ADMIN_CHEATSHEET.md)** |
| `task get` / `task log` / `task report` / `task action` 报 config | 回到 `task list`，复制 `data.items[].task_id` 后再传 `--task-id`；不要用列表序号、record_id、workflow_node_id 或自行拼三键。详见 **「待办 … SOP」步骤 2**                              |
| 成员 + `custom:` 后纯数字视图                                            | 读数时**跳过**，换 `system:*` 或其它 `custom:*`                                                                                                   |
| `record update` 报 **`apply_id must be positive`** 等而 `get`/`list` 正常           | 常为 **超大 `record_id`（超 JS 安全整数）** 下的 CLI 校验问题；见 **[reference/QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md](./reference/record/QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md)** |


---

## 命令速查（骨架）

**何时须细读引用、勿凭本节推测**：见**文首「硬约束（必读）」**。

> **适用范围**：普通/基本成员在只读或小范围写入里**较高概率可用**的形态；勿照抄旧应用搜索入口、无权的 **`import …`**（易 **40002 / IMPORT_\***）；管理闭环见 **[reference/QINGFLOW_CLI_ADMIN_CHEATSHEET.md](./reference/core/QINGFLOW_CLI_ADMIN_CHEATSHEET.md)**。

**形态**：`qingflow [--profile 名] [--json] …` · 自动化**始终**建议 `--json` · `profile` 是根级执行上下文，若 `builder contract` 示例 JSON 里出现 `"profile": "default"`，不要复制进 CLI 的 `--*-file` 载荷；CLI 要写 `qingflow --profile default ...` · 嵌套子命令（如 `record schema browse`）**勿**整体加引号 · 包版本用 `qingflow --version`；需要结构化输出时用 `qingflow --json version`。

| 分组 | 骨架（细则见上文章节 + 「关联文件」） |
| ---- | ------------------------------------ |
| **auth** | `auth whoami` · `auth use-credential --base-url "$QINGFLOW_BASE_URL" --credential-stdin --persist` · `auth login …`（见「失败恢复时的认证方式」）· `auth logout --forget-persisted` |
| **workspace** | `workspace list` · `workspace get --ws-id` · `workspace select`（慎用，可读数前不必；可能 **59004**） |
| **app / portal / view / chart** | `app list [--query 关键词]` → **`app get --app-key`**（`accessible_views` / `view_id`、`import_capability`）· `builder package list [--query 关键词]` → `builder package get --package-id` · `portal list` · `portal get --dash-key` · `view get --view-id`（只读视图元信息；`baseInfo` 或 `viewConfig` 只有 40002 / 40027 / 404 这类权限/缺失边界可用另一侧降级，非权限类后端错误不隐藏；解析 app 仅依赖同源 view/form 与可见应用树，不回退旧应用搜索）· `chart get --chart-id`（图表 `baseInfo` / 数据 / 配置分阶段读取；单个辅助阶段 40002 / 40027 / 404 只作为 warning，非权限类后端错误不隐藏） |
| **record** | `record schema insert`（新建记录 insert-ready schema，仅 `--app-key`）· **`browse`/`list`/`access`：`--app-key` + `--view-id`（缺一常 CONFIG）** · `record list --query ... [--query-field FIELD_ID] [--page-size N]` 用于候选定位/样本浏览 · `record get --record-id` 读详情页首屏上下文 · `record logs --record-id` 读完整数据/流程日志 JSONL · `record insert --items-file`（单条也是 items 一行）· `schema update --record-id [--view-id]` / **`update`**（单条 `--fields-file` **或** 批量 `--items-file`/`--dry-run`，二者勿混）· `record delete --app-key --record-id --view-id system:*` / `--record-ids-file` · `export start/direct --view-id` 仅用于明确导出文件 · **大 schema**：先 **[FIELD_DATA_TYPES](./reference/core/QINGFLOW_CLI_FIELD_DATA_TYPES.md)** / **[RECORD_CREATE](./reference/record/QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md)** / **[RECORD_UPDATE](./reference/record/QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md)** / **[RECORD_DELETE](./reference/record/QINGFLOW_CLI_RECORD_DELETE_WORKFLOW.md)**，再 `-h` |
| **import** | `record schema import?` · `import template` → `verify` → `repair?` → `start`（**`being-enter-auditing` 必填**）→ `status`（**三者 selector 只选一**）；导入权限预检的 `baseInfo` 只有 40002 / 40027 / 404 可降级为 unknown，非权限错误不能当成无导入权或继续执行；**链路与本机目录**只靠本节不够 → **[RECORD_IMPORT](./reference/record/QINGFLOW_CLI_RECORD_IMPORT_WORKFLOW.md)** |
| **builder** | **搭建／系统化配置**：先按 **[INDEX](./reference/00-INDEX.md)** / **[BUILDER](./reference/builder/README.md)** 选主路径，再读 `builder contract`。**完整系统/应用包**：`builder package apply --config-file` → 每个应用依次执行 `builder app-form schema`、更新时 `get --app-key APP_KEY --being-draft`、`validate --schema-version VERSION --file DECLARATION.json`、`apply --file DECLARATION.json`（固定版本、完整声明、记录返回的 `appKey`）→ 视图（按钮随视图 `action_buttons` 写）→ 门户（缺报表时写 `chart`）→ 发布/回读。旧 `schema apply` / `layout apply` 不在当前 CLI parser 中。超时、`partial_success`、`write_executed=true`、`safe_to_retry=false` 或回读不完整时先读取 AppForm draft/published，再恢复，不得重复创建或创建 V2/测试/随机后缀绕过重名。**单应用**：新建和更新遵循同一 AppForm CLI 链路，再按需求配置流程/视图。更新动作归入对应资源文档：AppForm [30](./reference/builder/30-schema-fields.md)、视图 [50](./reference/builder/50-views.md)、报表 [60](./reference/builder/60-charts.md)、门户 [70](./reference/builder/70-portal.md)、关联资源/非主链路按钮维护 [80](./reference/builder/80-buttons-associated-resources.md)、流程 [90](./reference/builder/90-workflow.md)、发布 [99](./reference/builder/99-publish-verify.md)。 |
| **task**（须落盘见上文） | `task list [--task-box][--flow-status][--app-key][--query] --page --page-size`（**枚举、`--query`、与 `record` 视图口径勿混**：见上文 SOP · **[TASK_CONTEXT](./reference/task/QINGFLOW_CLI_TASK_CONTEXT_WORKFLOW.md)**）· **`get`/`log`/`report`/`action`**：默认只传 `task list` 返回的 **`data.items[].task_id`**；`report` 另须必选 **`--report-id`**；`action` **无 `--dry-run`** |

**高发必败**：旧应用搜索入口 · **`record list`/`browse`/`access` 缺 `--view-id`** · **`task report` 缺 `--report-id`** · **`record update` 批量与单条参数混用**。

更多成员策略：**[reference/QINGFLOW_CLI_MEMBER_CHEATSHEET.md](./reference/core/QINGFLOW_CLI_MEMBER_CHEATSHEET.md)** · 一次性长模板：**[reference/QINGFLOW_CLI_ONE_SHOT_CHEATSHEET.md](./reference/core/QINGFLOW_CLI_ONE_SHOT_CHEATSHEET.md)** · 对齐说明：**[reference/QINGFLOW_CLI_EXPLORATION_REPORT.md](./reference/core/QINGFLOW_CLI_EXPLORATION_REPORT.md)**。

---

*技能维护：CLI 升级时以 `qingflow --version`、`qingflow … --help` 与本文 **task-box / flow-status** 对照表为准复核。*
