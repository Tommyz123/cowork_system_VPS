---
name: reference_cowork_location
description: cowork/ 文件夹路径和核心文件位置速查
type: reference
originSessionId: 8a06505e-fc15-40da-9a68-546769d6bf1f
---
主公电脑桌面有一个专属文件夹 `Desktop/cowork/`，存放所有 Cowork AI 的规则和状态文件。

**Windows 路径：** `C:\Users\zhi89\Desktop\cowork\`
**WSL 挂载路径：** `/mnt/c/Users/zhi89/Desktop/cowork/`
**GitHub repo：** https://github.com/Tommyz123/cowork_system（私有）

**核心文件：**
- `context.md` → 电脑全局文件索引（找文件时读这里）
- `cowork_log.md` → Cowork 操作日志
- `CLAUDE.md` → AI 全局行为规则
- `ARCHITECTURE.md` → 系统架构说明
- `CURRENT_SESSION.md` → 项目进度存档
- `INSIGHTS.md` → 可复用经验积累
- `friction_log.md` → 摩擦/问题记录
- `BACKLOG.md` → 系统改进积压
- `memory/` → 跨对话记忆文件夹（本文件所在处）
- `playbooks/` → 各项目操作手册

**VPS 路径（当前主力运行环境）：** `/home/cowork/cowork/`
**VPS service 用户：** `cowork`（非 root；systemd service 为 `cowork-claude.service`）
**VPS SSH：** `ssh root@142.93.207.54`

**How to apply:** 每次新对话涉及文件操作时，请求桌面访问权限后直接读取 `Desktop/cowork/context.md`。VPS 上运行时路径是 `/home/cowork/cowork/`，不是 `/root/cowork/`。
