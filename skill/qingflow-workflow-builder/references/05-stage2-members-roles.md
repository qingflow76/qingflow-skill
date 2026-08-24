# 阶段 2：获取成员/角色信息

在配置节点负责人（`responsible`）前，需要搜索可用成员与角色：

```bash
# 搜索成员
qingflow --json builder member search --query "<姓名/关键词>" --page-size 20
# 搜索角色
qingflow --json builder role search --keyword "<角色名>" --page-size 20
```

## 注意事项

- `responsible` 是 **MemberRefDTO 数组**，不是单值对象
- `type` 字段可取：
  - `user`（指定人）
  - `role`（角色）
  - `dept`（部门）
  - `applicant` / `leader` / `formEmail` / `formMember` / `formDept` / `nodeLeader`
- 指定人时使用 `uid` 传入成员 UID（整数）
- 角色时使用 `roleId` 传入角色 ID（整数）
- 部门时使用 `deptId` 传入部门 ID（整数），可选 `havingSubDept`
- 避免硬编码 UID/角色 ID/部门 ID，始终从搜索结果中提取

---

← 上一步：[04-stage1-business-modeling.md](04-stage1-business-modeling.md)
← 返回主流程：[../SKILL.md](../SKILL.md)
→ 下一步：[06-stage3-build-spec.md](06-stage3-build-spec.md)
