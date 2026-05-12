---
name: feedback_artifact_indexing
description: 任何新建持久化产物（脚本/cron/文档/工具/数据）必须最后一步加入索引层，否则视为任务未完成
type: feedback
---

主公明确原则（2026-05-12）：**任何新建的东西必须同时记录在某个索引层，否则=没做。**

**Why:** 主公原话："做了不留记录 = 不知道东西在哪里 = 失败"。反面教材实测：
- `scripts/index_conversations.py` JSONL_DIR 写死 `-root-cowork` 路径，没人知道直到 2026-05-12 收工时撞 bug
- 双 bot opus_home memory 目录一直空，实际在用 git repo 备份，**架构层面无人知晓**
- Agent View 调研后若不沉淀 reference，下次有人问还要重新派 subagent 浪费配额
- 沉默建的文件 = 半年后没人找得到 = 浪费

**How to apply:** 创建任何持久化产物时，**最后一步必须加索引**，索引到位才算任务完成：

| 产物类型 | 索引位置 | 注册内容 |
|---|---|---|
| 新建 .py / .sh 脚本 | `ARCHITECTURE.md` 脚本表 或 `scripts/README.md` | 路径 + 一行作用说明 + 触发方式 |
| 新建 cron 任务 | `reference/cron_jobs.md`（统一总览） | 时间 + 脚本路径 + 作用 + log 位置 |
| 新建 reference/* 文档 | `memory/MEMORY.md` 引用 或 `资料/INDEX.md`（如属于资料层） | 一行 hook + 文件路径 |
| 新建 legal_library/* 文档 | `legal_library/INDEX.md` + `CHANGELOG.md` | 主题关键词映射 |
| 新建 memory/* 文件 | `memory/MEMORY.md`（必须更新，按现有结构追加） | 一行描述 |
| 新建 playbook | `CLAUDE.md` 启动按需读取区块 + frontmatter triggers | 关键词 → 自动路由 |
| 新建数据/输出文件（生成型） | `context.md` "数据/输出文件位置"区块 | 路径 + 生成机制 |
| 新建 Skill | `~/.claude/skills/SKILLS_INDEX.md` | 触发词 + 简介 |

**强制检查清单（每次新建持久化产物时心里过一遍）：**
1. ✅ 文件已写入磁盘
2. ✅ 日志已记入 cowork_log.md（含路径）
3. ✅ **索引层已添加引用**（按上表）
4. ✅ 如有 [需同步] 标记，下次收工会扫到

**只有这 4 步都做完，任务才算完成。** 不做第 3 步 = 任务未完成 = 应立即补。

**反面案例（不能再犯）：**
- ❌ 写了脚本不在 ARCHITECTURE.md 注册
- ❌ 加了 cron 不在 cron_jobs.md 记录
- ❌ 写了 reference 文档不在 MEMORY.md 加引用
- ❌ 沉默地创建数据文件不告诉 context.md

**正面案例（2026-05-12 诉讼追踪闭环）：**
- 新建 `legal_library/docket_organic_blooms_904497.md` → 同步加入 `legal_library/INDEX.md`
- 新建 `scripts/cannabis_docket_reminder.py` → 同步加入 `ARCHITECTURE.md`
- 加 crontab 任务 → 同步加入新建的 `reference/cron_jobs.md`
- 新建 `reference/cron_jobs.md` 本身 → 同步加入 `MEMORY.md` + `context.md`

**这条规则覆盖范围：** 所有 `/home/cowork/cowork/`、`/home/cowork/legal_library/`、`/home/cowork/.claude/`、`/home/cowork/cowork/scripts/` 下的新建持久化文件。临时文件（`/tmp/`、`*.tmp`、`*.log` 等）不在此列。
