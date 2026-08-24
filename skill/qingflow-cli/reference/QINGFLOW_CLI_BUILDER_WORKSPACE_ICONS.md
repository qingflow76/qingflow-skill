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

颜色候选以 `builder icon catalog` 返回为准，例如 `emerald`、`blue`、`azure`、`orange`、`red`。
