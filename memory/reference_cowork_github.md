---
name: reference_cowork_github
description: cowork_system VPS 私有 GitHub repo 位置和版本控制范围
type: reference
originSessionId: 33cf13b1-1f79-43d2-9545-2396c5075c88
---
cowork 系统有私有 GitHub repo，用于追踪核心系统文件的变更历史。

**Repo URL（VPS 主力）：** https://github.com/Tommyz123/cowork_system_VPS（私有）
**旧 Repo（WSL 归档）：** https://github.com/Tommyz123/cowork_system（私有，不再更新）
**GitHub 账号：** Tommyz123
**SSH Key：** VPS 已配置 ed25519 key（~/.ssh/id_ed25519），alias: cowork-vps

**追踪的文件（纳入版本控制）：**
- CLAUDE.md、ARCHITECTURE.md、context.md
- memory/、playbooks/
- CURRENT_SESSION.md、BACKLOG.md、INSIGHTS.md、friction_log.md
- skills/（收工时从 ~/.claude/skills/ 同步过来）

**不追踪的文件：**
- cowork_log.md（流水账，变动太频繁）
- newscripts/（独立 repo）
- backups/、idea/、research/、scraper/
- 所有 .log 文件

**How to apply:** 每次收工时，改动核心文件后 commit 到此 repo（收工流程步骤3）。
