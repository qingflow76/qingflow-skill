# Builder 工作区图标规则

用于应用包、应用、门户的新建与改名改图标场景。

## 默认链路

1. 先读取候选目录：

```bash
qingflow --json builder icon catalog
```

2. 新建应用包、应用、门户时，显式填写 `icon` 和 `color`。

3. 不要使用 `template`；这是通用图标，新建资源会被 CLI 阻断。

## 关键规则

- CLI 不会根据业务名称自动猜图标。
- 智能体必须自己选择业务贴合的图标和颜色；主写法只有 `icon + color`，例如 `"icon": "table", "color": "blue"`。
- CLI/MCP 继续兼容 `icon_name + icon_color`、`icon_config` 或 `icon: {name, color}`，但这些只用于历史载荷和读回适配，不作为新提示词示例。
- 创建应用包、应用、门户时缺少 `icon` 或 `color` 会失败。
- 同批多应用创建时，每个新应用应使用不同 `icon`。
- 编辑已有资源时，不传 `icon/color` 会保留现状；显式传入时仍会校验合法性。
- 读取结果里的 `icon_config` 是给 UI/agent 展示用的解构结果，包含 `icon_name`、`icon_color`、`icon_text`、`raw`。

## 示例选择

这些只是候选思路，不是 CLI 默认映射：

| 场景 | 可选 icon |
|---|---|
| 员工 / 花名册 | `business-personalcard`、`user-group` |
| 任务 / 待办 | `clipboard-check`、`action-work` |
| 工时 / 时间 | `clock`、`action-hourglass-full` |
| 商机 / 增长 | `business-graph`、`business-trend-up` |
| 订单 / 交付 | `delivery-box-1`、`shopping-bag` |
| 回款 / 收款 | `money-receipt-2-1`、`money-wallet-1` |
| 门户 / 数据大屏 | `view-grid`、`chart-square-bar` |

常见安全选择：

| 场景 | 推荐 icon | 推荐颜色 |
|---|---|---|
| 应用包 / 门户 | `view-grid`、`chart-square-bar` | `blue`、`indigo`、`qing-purple` |
| 表单 / 台账 | `table`、`database`、`document` | `blue`、`azure` |
| 流程 / 任务 / 审批 | `clipboard-check`、`clipboard-list`、`action-work` | `emerald`、`green` |
| 时间 / 计划 | `clock`、`calendar` | `orange`、`yellow` |
| 设备 / 资产 | `server`、`comp-devices`、`cog`、`wrench-f` | `azure`、`indigo` |
| 风险 / 异常 | `exclamation-circle`、`shield-exclamation`、`bug-f` | `red`、`orange` |
| 财务 / 收付款 | `currency-yen`、`money-wallet-1`、`money-receipt-2-1` | `orange`、`qing-orange` |
| 人员 / 组织 | `user`、`user-group`、`business-personalcard` | `emerald`、`blue` |

不要写不存在的泛化图标名，例如 `warning`、`approval`、`asset`。需要警告类图标时用 `exclamation-circle` 或 `shield-exclamation`；需要审批类图标时用 `clipboard-check`。

## 当前 catalog 快照

以下清单来自当前 CLI 的 `builder icon catalog`。如果本机 CLI 返回的 catalog 与这里不同，以命令返回为准。

颜色：

`qing-orange`, `yellow`, `green`, `emerald`, `blue`, `azure`, `indigo`, `qing-purple`, `purple`, `pink`, `red`, `orange`

图标：

- `user`, `user-group`, `user-remove`, `user-add`, `user-circle`, `base-camera`, `view-grid`, `inbox`
- `inbox-in`, `share`, `sitemap`, `airplane`, `template`, `music-note`, `movie-play`, `clock`
- `document`, `document-search`, `clipboard-check`, `document-download`, `document-text`, `clipboard-copy`, `presentation-chart-bar`, `chart-square-bar`
- `database`, `server`, `calendar`, `mail`, `annotation`, `chat`, `bell`, `key`
- `shopping-bag`, `download`, `eye`, `eye-off`, `emoji-happy`, `emoji-sad`, `sun`, `moon`
- `cloud`, `lightning-bolt`, `fire`, `star`, `sparkles`, `heart`, `cake`, `gift`
- `light-bulb`, `exclamation`, `cog`, `thumb-up`, `thumb-down`, `cloud-download`, `cloud-upload`, `printer`
- `phone-incoming`, `phone-missed-call`, `terminal`, `search-circle`, `x-circle`, `check-circle`, `exclamation-circle`, `question-mark-circle`
- `information-circle`, `academic-cap`, `briefcase`, `home`, `phone`, `photograph`, `puzzle`, `color-swatch`
- `lock-open`, `lock-closed`, `shield-check`, `shield-exclamation`, `currency-dollar`, `currency-yen`, `globe`, `at-symbol`
- `slack`, `microphone`, `speakerphone`, `trash`, `book-open`, `truck`, `filter`, `essetional-filter-search`
- `essetional-filter-tick`, `table`, `calculator`, `location-radar`, `essetional-weight`, `school-award`, `comp-cloud-connection`, `comp-cloud-remove`
- `comp-cpu-charge`, `comp-cpu-setting`, `comp-cpu`, `comp-devices`, `comp-driver-2`, `comp-driver-refresh`, `location-global`, `location-location`
- `location-map`, `location-gps`, `essetional-ranking`, `chart-bar`, `business-graph`, `business-status-up`, `business-trend-down`, `business-trend-up`
- `business-presention-chart`, `business-favorite-chart`, `business-health`, `receipt-refund`, `receipt-tax`, `money-receipt-2-1`, `money-transaction-minus`, `action-hourglass-full`
- `action-work`, `bug-f`, `essetional-pet`, `files-folder`, `badge-check`, `money-wallet-1`, `money-ticket`, `money-money`
- `money-tag`, `money-wallet-2`, `business-personalcard`, `car-airplane`, `car-bus`, `car-car`, `car-driving`, `car-gas-station`
- `car-smart-car`, `car-ship`, `location-map-1`, `location-route-square`, `cone`, `design-brush-4`, `paint-roll`, `wrench-f`
- `essetional-reserve`, `essetional-broom`, `design-brush-2`, `essetional-judge`, `design-bucket`, `palette`, `comp-electricity`, `vial`
- `beaker`, `leaf-f`, `cursor-click`, `solid-search-alt-2`, `md-library`, `building-3`, `office-building`, `building-hospital`
- `school`, `store`, `video-camera-vintage-f`, `comp-monitor`, `delivery-truck`, `delivery-box-1`, `delivery-box-add`, `delivery-box-remove`
- `settings-setting-3`, `document-duplicate`, `essetional-flag-2`, `flag`, `icon-currency-dollar`, `clipboard-list`, `save-as`, `wifi`
- `status-online`, `scissors`, `globe-alt`, `ban`, `finger-print`, `qrcode`, `paper-clip`, `translate`
- `cube-transparent`, `variable`, `switch-vertical`, `sports-baseball`, `sports-basketball`, `sports-soccer`, `sports-football`, `sports-volleyball`
