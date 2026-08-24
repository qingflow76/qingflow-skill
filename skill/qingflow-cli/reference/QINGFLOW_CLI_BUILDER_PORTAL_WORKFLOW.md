# Builder 门户创建与变更 SOP：`qingflow builder portal`

搭建侧稳定入口：**`qingflow builder portal`**：`list` / `get` / **`apply`** / **`delete`**（与根命令 **`qingflow portal`** 的「成员可读列表/详情」不同，见 **[QINGFLOW_CLI_EXPLORATION_REPORT.md](./QINGFLOW_CLI_EXPLORATION_REPORT.md) §4.6**）。

实现要点来自 CLI 打包内的 `builder_facade/models.py`（`PortalApplyRequest`、`PortalSectionPatch`）、`builder_facade/service.py`（`portal_apply` / `portal_delete`）、`cli/commands/builder.py`。已对 **`package_id=2030703`**、应用 **`ead8ims5i401`** **实跑**：**新建**（`--no-publish`）、**`--publish` 更新**（网关 **503** 恢复后已重试成功）、**五类区块可稳定落库**；**`filter`（`type:6`）经 CLI 直传未落库** 见 **§3.4 / §8**。另已对测试包 **`1414907`** 实跑 **`portal delete`**：临时门户 **`etcivtmv5402`** 删除后回读 **`readback_status=deleted`**。

> **权限**：**更新**需 **`edit_portal`**；**新建**按后端 `DashCtrl.createDash` 链路只预检目标包 **`add_app`**，不额外要求包 **`edit_app`**。失败时参见主技能与 **ADMIN** 速查。

> **契约**：`qingflow --json builder contract --tool-name portal_apply`；删除契约：`qingflow --json builder contract --tool-name portal_delete`

---

## 1. 读：`list` → `get`

```bash
qingflow --json builder portal list > tmp/builder_portal_list.json

qingflow --json builder portal get --dash-key "<DASH_KEY>" > tmp/builder_portal_get.json
qingflow --json builder portal get --dash-key "<DASH_KEY>" --no-being-draft
```

- **`list`** 可能带 **`PORTAL_PERMISSION_READ_UNAVAILABLE`**，**`verified: false`** 仍可能有可用 **`items[]`**。
- **`get`**：**`--dash-key`** 必填；默认 **`--being-draft`** 为草稿。

---

## 2. 写：`apply` 两种模式（互斥）

**不可同时**出现 **`--dash-key`** 与 **`--package-id`**。

| 模式 | 必备参数 | 含义 |
|------|----------|------|
| **新建** | **`--package-id`** + **`--dash-name`** | **`--sections-file` 须非空**。 |
| **更新** | **`--dash-key`** | 不要带 **`package_id`**。 |

| 参数 | 说明 |
|------|------|
| **`--publish` / `--no-publish`** | 默认 **`--publish`**。仅 **`--no-publish`** 时不会调用发布接口；契约说明 **`publish=false` 不宣称线上已变**。 |
| **`--payload-file`** | 完整门户 JSON 对象；**标准字段写 `dash_name`**。新版 CLI 兼容 **`name -> dash_name`**、单页 **`pages[0].components -> sections`**，但 agent 默认不要依赖兼容别名。 |
| **`--sections-file`** | JSON **数组**；**全量替换**。省略时仅改基础信息，且 **`hide_copyright` / `dash_global_config` / `config`** 不能单独提交（**`PORTAL_SECTIONS_REQUIRED`**）。 |
| **`--layout-preset`** | 可选：**`auto` / `dashboard_2col` / `dashboard_3col`**。当区块未显式写 **`position`** 时由工具生成大屏布局。 |
| **`--visibility-file`** | 与 **`--auth-file`** 不能同时用。 |
| **`--icon`** / **`--color`** | 新建门户必须显式传合法的非 `template` 图标和颜色；候选用 `qingflow --json builder icon catalog`。编辑已有门户时省略则保留现状。 |
| **`--hide-copyright`** / **`--dash-global-config-file`** / **`--config-file`** | 见契约；部分键 **依赖与 `sections` 同批提交**。 |

**图标规则**：CLI 不按门户名自动猜图标；智能体需要自行选择业务贴合的 `icon + color`。读回结果里的 `icon_config` 可直接用于前端资源卡片展示。

---

## 3. `sections[]`：六类组件与回读 `type`

### 3.1 公共键

- **`title`**（必填）、**`source_type`**（必填，小写）、可选 **`position`**（**`pc`/`mobile`** 各 **`x,y,cols,rows`**；省略则由**实现自动排布**）。
- **`config`**、**`dash_style_config`**：按类型 Optional。默认只写 snake_case 规范键。

### 3.1.0 Payload 字段口径

推荐完整 payload 直接使用 CLI 标准键：

```json
{
  "dash_name": "产品研发数据大屏",
  "package_id": 1414909,
  "layout_preset": "dashboard_2col",
  "pages": [
    {
      "title": "研发总览",
      "components": [
        {
          "title": "部门分布",
          "source_type": "chart",
          "chart_ref": {"app_key": "APP_KEY", "chart_id": "CHART_ID"}
        }
      ]
    }
  ]
}
```

`name` 只是兼容别名；如果遇到旧版 CLI 报 **`name Extra inputs are not permitted`**，不要反复重试，改成 **`dash_name`** 或升级 CLI。

### 3.1.1 布局硬规则：PC 24 栅格，mobile 6 栅格

**门户 PC 端不是 12 栅格，而是 24 栅格。**如果把两列写成 **`x=0/6, cols=6`**，所有组件只会占左半屏，工具会返回 **`PORTAL_LAYOUT_HALF_WIDTH`**。

推荐：

| 场景 | PC 写法 |
|------|---------|
| 不确定布局 | **省略 `position`**，或传 **`--layout-preset auto`** |
| 两列可视化图表 | **`x=0/12, cols=12`**，图表 **`rows >= 7`** |
| 三列可视化图表 | **`x=0/8/16, cols=8`**，图表 **`rows >= 7`** |
| 四个指标卡 | **`x=0/6/12/18, cols=6, rows=5`** |
| 具体数据视图 / 明细表 | 优先 **`cols=12`** 或 **`cols=24`**，视图 **`rows >= 11`** |

mobile 写法固定按 **6 栅格**：通常 **`x=0, cols=6`**。如果只写了 PC position，CLI 会自动补 mobile position，并返回 **`PORTAL_MOBILE_POSITION_MISSING`** 提醒。

图表卡片过小时会返回 **`PORTAL_CHART_CARD_TOO_SMALL`**；指标卡按 **`pc.cols >= 6, pc.rows >= 5`** 校验，普通可视化图表按 **`pc.cols >= 8, pc.rows >= 7`** 校验。指标区图表建议写 `role: "metric"`；此时必须引用 `target` / `indicator` 图表，否则返回 **`PORTAL_METRIC_SECTION_CHART_TYPE_MISMATCH`**，应先用 `app_charts_apply` 创建缺失指标卡再组门户。标准工作台数量也会进入 `layout_diagnostics.standard_template_counts`：指标卡推荐 4-6 个、BI 图表 2-3 个、业务视图 1-2 个，超出或不足会返回 `PORTAL_STANDARD_*_COUNT_OUT_OF_RANGE`。

### 3.1.2 推荐门户模板：业务工作台

默认按 **业务入口 → 核心指标 → BI 可视化 → 业务视图** 搭建。门户首屏应直接呈现可用工作台，不要做营销页、说明页或大面积装饰区。

| 区域 | 推荐组件 | PC 布局 | 要点 |
|------|----------|---------|------|
| 顶部业务入口 | **`grid`** + 可选 **待办 `task`** | `grid x=0,y=0,cols=12,rows=4`；待办 `x=12,y=0,cols=12,rows=4` | `grid` 放 2-6 个核心业务入口；待办用于当前用户任务概览。当前公开 `portal apply --sections-file` 暂未支持 `source_type=task`，不要伪造；见下方边界说明。 |
| 核心指标 | **`chart`** 指标卡 + `role: "metric"` | 4 张：`x=0/6/12/18,y=4,cols=6,rows=5` | 指标卡推荐高度 **5**。24 栅格下单卡最小 `cols=6`，所以一行 4 张最稳；如果要 5 个指标，拆成两行。 |
| BI 可视化 | **`chart`** 图表 | 3 张：`x=0/8/16,y=9,cols=8,rows=7`；或 2 张：`x=0/12,cols=12,rows=7` | 可视化图表推荐高度 **7**，一行 2-3 个，1-2 行。 |
| 业务数据视图 | **`view`** | `x=0/12,y=16,cols=12,rows=11`；或单表 `cols=24,rows=11` | 数据视图推荐高度 **11**，一行 1-2 个，1-2 行。只挂业务视图，不要创建或引用默认的 **全部数据 / 我的数据** 当主门户视图。 |

mobile 固定按 **6 栅格** 从上到下堆叠：通常所有组件 `x=0, cols=6`，`y` 按 PC 顺序递增。若顶部同时有 `grid + task`，mobile 建议先业务入口 `y=0,rows=4`，再待办 `y=4,rows=4`，核心指标从 `y=8` 开始；若当前公开 CLI 只能写 `grid`，核心指标可从 `y=4` 开始。

**当前工具边界**：

- 公开 `sections-file` 稳定支持：**`grid` / `chart` / `view` / `text` / `link`**；`filter` 仍按 **§3.4** 的 raw `filterConfig` 边界处理，不作为主路径。
- **待办 `task` / 常用 `favorite`** 是前端/后端 raw 组件形状，不在当前公开 `source_type` 合约里。智能体不要在 `sections-file` 中写 `source_type: "task"`；只有工具后续显式支持 `task`，或维护者走 raw 门户写入链路时，才使用待办槽位。
- 推荐门户的可直接 apply 示例见 **[portal_sections_standard_workbench.example.json](./portal_sections_standard_workbench.example.json)**。该示例使用当前公开 CLI 可稳定写入的组件，顶部先用一个业务入口 `grid` 占满 24 栅格；如果工具已支持待办组件，再把顶部拆成 `grid cols=12 + task cols=12`。
- `grid` 必须写 **`config.items[]`**；只写 `gridTitle` / `beingShowTitle` 会生成空入口容器，工具会返回 **`PORTAL_GRID_ITEMS_EMPTY`**。

**待办组件 raw 形状参考**（仅用于工具实现对齐，当前不要作为 `--sections-file` 输入）：

```json
{
  "type": 8,
  "position": {
    "pc": {"x": 12, "y": 0, "cols": 12, "rows": 4},
    "mobile": {"x": 0, "y": 4, "cols": 6, "rows": 4}
  },
  "taskConfig": {
    "beingShowTitle": true,
    "componentTaskTitle": "待办",
    "beingShowHint": true,
    "componentTaskHint": "及时处理待办，可以有效提升流程效率",
    "dashTaskConfigList": [
      {"type": 1, "title": "all.taskTodo", "beingCheck": true, "ordinal": 0},
      {"type": 2, "title": "all.taskTimeout", "beingCheck": true, "ordinal": 1},
      {"type": 3, "title": "all.taskUpcomingTimeout", "beingCheck": true, "ordinal": 2},
      {"type": 4, "title": "all.taskRemind", "beingCheck": true, "ordinal": 3}
    ]
  }
}
```

### 3.2 `source_type` ↔ 回读 `components[].type`（搭建侧）

| `source_type` | 回读 `type`（数字） | 搭建侧含义 |
|---------------|---------------------|------------|
| **`chart`** | **9** | QingBI 图表块 |
| **`view`** | **10** | 应用视图块 |
| **`grid`** | **2** | 九宫格 |
| **`filter`** | **6** | 筛选条 |
| **`text`** | **5** | 富文本说明 |
| **`link`** | **4** | 外链 |

CLI 校验（`PortalSectionPatch`）：**chart** 须 **`chart_ref`**；**view** 须 **`view_ref`**；**text** 须 **`text`**；**link** 须 **`url`**。**grid** / **filter** 无额外 ref，**`config` 形状由后端接受为准**。

### 3.3 **`chart`**：几乎总须 **`builder charts apply` 先建报表**

- `portal` 只做 **`chart_ref` 解析**（`app_key` + **`chart_id`** 优先，否则 **唯一 `chart_name`**）。
- 若 **`builder app get charts`** 为空，先 **`builder charts apply --app-key … --upsert-file`** 创建（契约 **minimal_example** 如 **`target` + `indicator_field_ids: []`**），从响应 **`chart_results[].chart_id`** 取 id 再写 **`chart_ref`**.

### 3.4 **`filter`**：`config` **整包**即接口里的 **`filterConfig`**

实现：组件为 **`{"type": 6, "filterConfig": deepcopy(section.config)}`**。

- **理论上**与 solution 编译器一致：外层 **`{"filterConfig": [ … ], "graphList": [ … ]}`**；**`graphList`** 常含 **`graphType`**（如 **`CHART`**）、**`graphKey`** 或 **`graphRef`（`entity_id` / `chart_id`）** 等。
- **本环境 CLI 直写实测（多次 `--publish`）**：在已验证 **chart / view / grid / text / link** 均可落库的前提下，**`source_type: filter` 始终未出现在 `draft_result.components` 中**；尝试过：**空数组**、**仅 `graphList` + QingBI `chart_id`**、**`graphKey` 为门户 `dashChartId`**、**`chart` 排在 **`filter` 前**、**仅 2 块（chart+filter）** 等，回读仍 **只有 chart（`count: 1`）** 或 **五类缺 `type: 6`**。  
  **结论**：当前宜 **在搭建界面创建筛选条**，再 **`builder portal get` 反抓** 原始 `filterConfig` 形状；或向后端确认 **POST `/dash/{dashKey}`** 对 **`type: 6`** 的必填字段。**自动化不要默认认为 `filter` 已写入。**
- portal `filter` 组件仍按 raw `filterConfig` 处理，不纳入视图 / 报表 / 关联资源的统一筛选 DSL 主链路。

### 3.5 **`grid` / `text` / `link` / `view`**

- **grid**：**`config`** 并入 **`gridConfig`**；业务入口必须写 **`config.items[]`**。应用入口项推荐 `{ "type": 1, "jumpMode": 1, "linkAppKey": "APP_KEY", "linkFormType": 1, "title": "入口名" }`。空 `config` 或空 `items` 只会生成空入口容器，并触发 **`PORTAL_GRID_ITEMS_EMPTY`**。
- **text** / **link**：**`text`** / **`url`** 必填。
- **view**：**`view_ref`**；**`view_key`** 来自 **`builder app get views`**。

---

## 4. 前置数据

| 目的 | 命令 |
|------|------|
| **`package_id`** | **`builder app resolve --app-key …`** → **`package_ids`** |
| **`view_key`** | **`builder app get --app-key … views`** |
| **`chart_id`** | **`builder app get charts`** 或 **`charts apply` 创建** |

---

## 5. 新建最小例（`--no-publish`）

见上文 **§2** 与 **`visibility`** 最小对象；**`sections`** 可先用 **单块 `view`**。成功后拿 **`dash_key`** 再 **更新 / 发布**。

---

## 6. 更新与替换语义

- **`--dash-key`** + **`--sections-file`**：**列表即全量**；没写进去的区块会被拿掉。
- 仅改 **可见性 / 图标 / 分组**：**不传 `--sections-file`**，且不要单独带 **§2** 所列「仅在有 sections 时允许」的键。

---

## 7. 删除：`delete`

```bash
qingflow --json builder portal delete --dash-key "<DASH_KEY>" > tmp/builder_portal_delete.json
```

- **只按 `dash_key` 删除一个门户**；先用 `builder portal list/get` 确认目标，不要按名称猜。
- 返回成功时重点看：**`delete_executed`**、**`readback_status`**、**`safe_to_retry_delete`**、`summary.removed`。
- **`delete_executed=true` + `readback_status=deleted`**：删除已执行且回读确认不存在。
- **`delete_executed=true` + `readback_status=unavailable|still_exists`**：DELETE 已发出，但回读不可确认或短时间仍存在；**不要盲目重复删除**，稍后用 `builder portal get/list` 确认。
- DELETE 本身失败时才按 `status=failed` / `error_code` 处理。

---

## 8. **发布**（`--publish`）

- **默认会发布**：未显式 **`--no-publish`** 即 **`publish: true`**；公开入口仍是 **`portal_apply`**，发布动作由工具内部执行并回读 **`being_draft=false`**。
- **已发布线索**：成功路径上 **`published: true`**；**`live_result.publishStatus`** 常见 **`2`** 表示已发布（以你环境枚举为准）。
- **`partial_success` + `PORTAL_READBACK_PENDING`**：草稿/线上 **组件数量或元数据** 与「本次期望」不一致时会出现；**`PORTAL_*_VERIFICATION_INCOMPLETE`** 警告。应 **`builder portal get --dash-key …`**（草稿与 **`--no-being-draft` 线上**）**肉眼核对**区块是否齐全，而不是仅信 **`verified: true`**。
- **网关 503**：**与 CLI 无关**；环境恢复后重试 **`portal get` / `portal apply`**。（本轮在网关恢复后 **`portal apply` 已成功**。）

---

## 9. 本环境实测摘要

| 步骤 | 命令要点 | 结果 |
|------|-----------|------|
| 新建门户 | `--package-id 2030703`、`--dash-name "CLI门户探针_可删"`、`--no-publish`、单 **view** | **`dash_key`: `ecdcell64s02`** |
| 补报表 | **`builder charts apply`**，`name: 门户探针_目标图`，**`target`** | **`chart_id`: `mcp_fb104267c5c249ca`** |
| 503 后重试 | **`--dash-key ecdcell64s02`、`--publish`** + 含 **filter** 的六类 **`sections-file`** | **`published: true`**；**`filter` 仍不落库** → **`partial_success`**，**`components expected 6, got 5`**（与 **§3.4** 一致） |
| **filter 专项** | 仅 **chart + filter** 两块的多种 **`graphList`/`graphRef`/`dashChartId`/`filterGroupConfig`** 组合 | **回读恒为 1 块（仅 `type: 9`）** |
| **稳定可复现** | **`--publish`** + **[portal_sections_five_types.example.json](./portal_sections_five_types.example.json)**（**grid / text / link / view / chart**） | **`status: success`**，**`types: [2,4,5,9,10]`**，**`published: true`** |
| 删除门户 | `builder portal delete --dash-key etcivtmv5402` | **`status: success`**，**`delete_executed: true`**，**`readback_status: deleted`**，**`summary.removed: 1`** |

**推荐工作台模板示例**：[portal_sections_standard_workbench.example.json](./portal_sections_standard_workbench.example.json)

**含 `filter` 的六类示例（`filter` 是否落库视环境/后端而定）**：[portal_sections_all_types.example.json](./portal_sections_all_types.example.json)

---

## 10. 排障

| 现象 | 处理 |
|------|------|
| `portal apply accepts exactly one selector mode` | **`dash-key`** vs **`package-id`** 二选一。 |
| `PORTAL_READBACK_PENDING` / **`components expected N, got M`** | **`portal get`** 数组件；若多写了 **`filter`** 而回读少一块，见 **§3.4**（**CLI 写 filter 可能整体不生效**）；也可能是 **异步回读**，可再 **`get`** 一次。 |
| **`published: true` 但 `verified: false`** | 读 **§7**；用 **`get` 草稿+线上**对照。 |
| **503** | 网关/运维；稍后重试。 |
| 缺 **chart** | **[QINGFLOW_CLI_BUILDER_CHARTS_WORKFLOW.md](./QINGFLOW_CLI_BUILDER_CHARTS_WORKFLOW.md)**：`builder charts apply`；或换有报表的应用。 |
| **VISIBILITY_CONFLICT** | 只用 **`--visibility-file`**。 |
| `delete_executed=true` 但 `readback_status=unavailable|still_exists` | DELETE 已发出，回读未确认；不要重复删除，稍后 `builder portal get/list` 复核。 |

---

## 11. 交叉引用

- [SKILL.md](../SKILL.md)
- [QINGFLOW_CLI_BUILDER_APP_DELIVERY_WORKFLOW.md](./QINGFLOW_CLI_BUILDER_APP_DELIVERY_WORKFLOW.md)
- [QINGFLOW_CLI_BUILDER_VIEWS_WORKFLOW.md](./QINGFLOW_CLI_BUILDER_VIEWS_WORKFLOW.md)
- [QINGFLOW_CLI_BUILDER_CHARTS_WORKFLOW.md](./QINGFLOW_CLI_BUILDER_CHARTS_WORKFLOW.md)
- [QINGFLOW_CLI_EXPLORATION_REPORT.md](./QINGFLOW_CLI_EXPLORATION_REPORT.md)
