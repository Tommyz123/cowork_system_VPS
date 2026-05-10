# Cowork 框架版本历史

> 每次框架升级前备份，升级后在此记录变更。出问题时看这里，去 backups/ 还原。

---

## v1 → v2（2026-03-24）

**升级原因：**
context.md、CURRENT_SESSION.md、memory/project_*.md 三个地方都在记录项目状态，分开维护容易不一致，需要手动同步。

**改动内容：**
- `context.md` — 删除"活跃项目状态快照"区块，改为一行指针指向 CURRENT_SESSION.md
- `memory/project_cannabis_advisor.md` — 移除"当前进度/数据库状态"字段，只保留不变的背景信息（目标、技术栈、工作目录）
- `memory/project_ai_skill.md` — 移除"当前状态"字段，只保留背景信息
- `CLAUDE.md` — 更新"保存进度"规则，只更新 CURRENT_SESSION.md 一个地方
- `ARCHITECTURE.md` — 更新分工说明，反映新的单一来源设计

**新分工：**
- 项目当前状态 → 只在 `CURRENT_SESSION.md`
- 项目背景信息 → 只在 `memory/project_*.md`
- 文件夹导航 → 只在 `context.md`

**回退方法：**
从 `backups/v1/` 复制对应文件回 `Desktop/cowork/` 覆盖。

---

## v1（2026-03-23，初始版本）

备份位置：`backups/v1/`

初始架构建立：CLAUDE.md + ARCHITECTURE.md + context.md + memory/ + playbooks/ + CURRENT_SESSION.md + INSIGHTS.md + friction_log.md + BACKLOG.md
