---
name: Discord 权限弹窗机制
description: Claude Code 的 Allow/Deny 权限确认框会出现在 Discord 频道，可从手机操作
type: reference
originSessionId: a423e1c0-1c79-4665-a6b9-1860c8bf80a0
---
Claude Code 的工具权限确认弹窗（Allow / Deny 按钮）会直接出现在 Discord 频道里，不需要在电脑终端操作。

因此，主公在手机上通过 Discord 遥控 Claude 时，仍然可以直接批准或拒绝工具执行请求。

**实际应用：**
- 从 settings.json 的 `permissions.allow` 列表中移除某个路径 → 该路径的 Edit/Write 操作会在 Discord 弹出确认
- 当前系统改用 `/tmp/task_approved` token 机制，效果类似但更灵活（可批准整个任务而非逐个文件）
