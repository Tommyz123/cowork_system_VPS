---
name: feedback_bot_name_version_sync
description: "模型版本更新时，对应实例的Discord bot用户名要同步改版本号，保持显示\"最新\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 06c61130-51a1-4a0e-a9b4-ce1f22a56d37
---

模型版本升级后，必须同步把该实例的 Discord bot 用户名里的版本号也改掉（如 Sonnet4.6 → Sonnet5），保持格式不变只换版本号。

**Why:** 主公明确要求（2026-06-30）：bot 名字要体现"用的是最新版本"，命名格式不变（前缀-模型名+版本号），只更新版本号部分。

**How to apply:**
- 触发时机：任一实例的模型版本变化时（升级/切换），主动检查并更新该实例 Discord bot 用户名。
- 操作方法：用该实例的 bot token 调 Discord API `PATCH /api/v10/users/@me {"username":"X"}` 改私聊显示名；群昵称另需 `PATCH /api/v10/guilds/1466957346310717636/members/@me {"nick":"X"}`（见 [[reference_dual_bot]]）。
- token 位置：`$HOME/.claude/channels/discord/.env`，三实例各自独立，不能用错（参考 [[feedback_instance_mapping]] 防止 BB/CC 用错 token）。
- 改名只动显示层，不影响 tmux/systemd/plugin 连接。
- 改完后写 cowork_log.md。
