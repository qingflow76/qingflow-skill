# Qingflow CLI 当前版本审计备忘

> 本文件只记录当前 CLI 与 skill 主路径容易混淆的事实。它不是执行 SOP；具体任务仍按 [SKILL.md](../SKILL.md) 与对应专题 reference 执行。CLI 升级后优先重新跑 `qingflow ... --help` 复核。

---

## 1. 当前能力树摘要

- 顶层：`qingflow {auth|workspace|app|portal|view|chart|record|import|export|task|builder|build} ...`
- `builder` 与 `build` 等价；默认写法仍推荐 `builder`。
- `record schema`：公开主路径为 `browse`、`insert`、`update`、`import`、`code-block`；`applicant` 仅为兼容保留入口，不作为推荐链路。
- `record` 公开执行入口：`list`、`access`、`get`、`logs`、`insert`、`update`、`delete`、`code-block-run`。
- 最终统计结论统一由 `qingflow-record-analysis` 走 `record_access -> Python/pandas`，不要寻找或使用其它聚合捷径。

---

## 2. 不要被 `--help` 方括号误导

部分参数在 argparse 帮助中看起来可选，但运行时由工具层或后端强制要求：

| 命令 | 实际要求 |
| --- | --- |
| `app list` | 可选 `--query` / `--keyword`，只在当前用户可见应用中本地过滤 |
| `builder package list` | 可选 `--query`，直接读取 Builder 应用包 `/tag` 列表并本地过滤 |
| `record schema browse` | 必须 `--app-key` + `--view-id` |
| `record list` | 必须 `--app-key`；业务记录读取应显式给 `--view-id` |
| `record access` | 必须 `--app-key` + `--view-id` |
| `builder member search` | 必须 `--query` |
| `builder role search` | 必须 `--keyword` |

自动化里读取命令优先使用根级 JSON 形态：`qingflow --json ...`；builder 写入/apply 命令默认只输出 JSON，不需要额外选择格式。builder apply 响应统一优先读 `operation + summary + resources[]`，其中 `resources[].id/key/name/ids/parent` 是 UI/智能体展示资源的稳定入口；旧字段只作兼容和排障。查 CLI 包版本直接用 `qingflow --version`；需要结构化输出时用 `qingflow --json version`。

---

## 3. Record 当前口径

| 入口 | 当前定位 |
| --- | --- |
| `record list` | 样本浏览 / 模糊定位候选；默认最多返回 10 条，返回 `data.pagination.total_count`，带 `--query` 时看 `lookup.total_count` 与 `lookup.next_action` |
| `record access` | 默认分析取数入口；自动分页写本地 CSV；不暴露 `page/page_size/limit/max_rows/profile` |
| `record get` | 前端详情页首屏上下文；字段、引用、首屏数据日志、首屏流程日志、关联资源、`media_assets`、`file_assets` |
| `record logs` | 单条记录全量可见数据日志 + 流程日志；自动分页写本地 JSONL，响应给路径和完整性 |
| `record insert` | 批量 `items` JSON；单条也是 `items` 数组一行；CLI 用 `--items-file` |
| `record update` | 单条 `--record-id + --fields-file` 或批量 `--items-file`；不要混用 |

`record_get` 下载到本地的图片读 `media_assets.items[].local_path`；文档、表格、PDF 等读 `file_assets.items[].local_path` 与 `extraction.text_path`。不要直接访问远端 Qingflow 附件 URL。

---

## 4. Builder 当前口径

| 入口 | 当前定位 |
| --- | --- |
| `builder app get` | 应用地图；轻量返回字段摘要、视图、图表、自定义按钮、关联资源池 |
| `builder app-form schema/get/validate/apply` | 当前表单/字段/布局/应用设置入口；固定 AppForm schema 版本，完整声明写入并保留现有 IDs；旧 `builder schema apply` / `builder layout apply` 仅为已移除的内部兼容适配器 |
| `builder views apply` | 业务视图；固定筛选写 `filters`，前端查询栏写 `query_conditions` |
| `builder button apply` | 自定义按钮默认路径；新增数据按钮用 `field_mappings/default_values`，绑定位置用 `header/detail/list` |
| `builder associated-resource apply` | 应用级关联视图/报表池 + 视图展示配置；报表来源用 `report_source`，不让智能体填写后端 raw source |
| `builder charts apply` | QingBI 报表配置；报表变更 immediate-live，不等同于应用发布 |
| `builder publish verify` | 发布后核验应用状态 |

按钮和关联资源 apply 有成功写入时会自动发布；没有成功写入、全阻断或全失败时不应额外发布。

---

## 5. ID 口径

| 名称 | 用途 |
| --- | --- |
| `view_id` | 用户态记录读取，形如 `system:all` 或 `custom:<viewKey>`；来自 `app get.accessible_views` |
| `view_key` | Builder 视图配置；用于 `builder view get`、`builder views apply`、按钮/关联资源视图配置 |
| `chart_id` / `chart_key` | 报表本体 ID/key；不可直接当作视图关联资源 ID |
| `associated_item_id` | 应用级关联资源项 ID，即后端 `form_asos_chart.id`；视图展示关联资源时必须用它 |

普通成员读数时，`custom:` 后仅数字的视图（如 `custom:1`、`custom:12`）常见 40038，应跳过并换 `system:all` 或其它表格类 `custom:*`。

---

## 6. 错误判断

- `59004` 多与额度/流币/AI 配额相关，不等同于未登录。
- `40002` 常是成员权限不足，尤其是角色检索、部分管理向操作；按关键词找应用优先用 `app list --query`。
- `record list/access requires view_id` 不是数据为空，是缺少视图上下文。
- 大 JSON 记录/任务查询仍建议落盘到 `tmp/...json` 后再读，不要直接塞入模型上下文；builder 写入/apply 工具默认直接 stdout，前端展示时优先解析 `resources[]`，需要留档时使用 `tee`。builder 读取命令仍显式加 `--json`。
