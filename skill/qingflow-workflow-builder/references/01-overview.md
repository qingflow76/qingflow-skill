# 轻流工作流搭建：概览与依赖

## 关联文件

| 文件 | 说明 |
|------|------|
| `manifest.yaml` | 技能清单 |
| `SKILL.md` | 主流程入口 |
| `scripts/validate_flow_spec.py` | 工作流 Spec 验证脚本，基于 JSON Schema + 自定义约束 |
| `scripts/diff_flow_spec.py` | 新旧 Spec 差异分析脚本，辅助更新模式下最小修改原则判断 |

---

## 依赖声明

本 Skill 关键依赖 **qingflow CLI**（已安装于 PATH，详见 `qingflow_cli` Skill）。以下 qingflow 命令为核心操作：

| 命令 | 用途 |
|------|------|
| `qingflow builder flow schema --json` | 获取最新 WorkflowSpecDTO JSON Schema |
| `qingflow builder flow get --app-key <KEY>` | 读取当前工作流 spec |
| `qingflow builder flow apply --app-key <KEY> --spec-file <FILE>` | 主链路：部署/更新 WorkflowSpec |
| `qingflow --json builder flow apply --app-key <KEY> --patch-nodes-file <PATCH>` | 局部修改现有节点 |
| `qingflow builder member search --query <关键词>` | 搜索成员 |
| `qingflow builder role search --keyword <关键词>` | 搜索角色 |
| `qingflow --json app get --app-key <KEY>` | 获取应用信息（字段列表等） |
| `qingflow --json builder app get --app-key <KEY> fields` | 获取应用可搭建字段详情 |
| `qingflow --json builder app get --app-key <KEY> flow` | 获取流程摘要（是否启用等） |

---

## 能力边界

| 在范围内 | 超出范围 |
|----------|----------|
| 基于已有应用搭建工作流 | 从零创建应用 |
| WorkflowSpec 生成与 apply；`patch_nodes` 局部修改 | 操作复杂命令拼接 |
| 审批/填写/抄送/分支条件等 WorkflowSpec 支持的流程 | 不读 schema/spec 就猜 raw 后端字段 |
| 审批/填写/抄送/自动化节点配置 | 修改字段定义 |
| 成员/角色搜索用于节点负责人 | 组织架构管理 |
| 验证 → apply → 校验循环 | 前端 UI 拖拽操作 |

---

无论线性、分支、Q-Robot、审批、填写还是抄送流程，都使用 WorkflowSpec `--spec-file`；已有节点的小修改使用 `--patch-nodes-file`。

← 返回主流程：[../SKILL.md](../SKILL.md)
→ 下一步：[02-update-mode.md](02-update-mode.md)
