---
name: Claude Routines 功能
description: Anthropic 2026-04-14 发布的云端定时执行功能，Pro 每天5次
type: reference
originSessionId: a423e1c0-1c79-4665-a6b9-1860c8bf80a0
---
Claude Routines（2026-04-14 发布）：在 Anthropic 云端定时执行任务，不依赖本地机器开机。

**配额：** Pro 5次/天，Max 15次/天

**触发方式：** 定时（cron）/ API POST / GitHub 事件

**适合 Routine 的任务类型：**
- push 触发的自动检查/验收（不需要持久 db）
- 发 Email 报告（SMTP via Full 权限）
- 发 Discord 通知（curl webhook，需 Full 或 Custom 权限允许 discord.com）
- 读写 GitHub 仓库（设计甜区）

**不适合 Routine 的：**
- 需要持久化 SQLite db 的任务（每次运行独立 VM，数据不保留）
- 量化交易/机票/新闻监控 → 继续用本地 cron / Mac mini

**主动提醒规则：**
主公要做任何新的自动化任务时，主动评估 Routine 是否合适并给出建议，不局限于特定项目。

**入口：** claude.ai/code/routines

**官方规则存档：** `cowork/reference/routines_rules.md`（完整坑点/触发类型/网络权限说明）
