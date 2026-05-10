---
name: Discord plugin reply "not allowlisted" 报错
description: Discord plugin v0.0.4 fetchAllowedChannel partial DM channel bug，已查明根因 2026-05-09 修复
type: feedback
originSessionId: 57e36a48-d97c-4817-92a1-869e7417bf4d
---
`mcp__plugin_discord_discord__reply` 报错 "channel is not allowlisted"，即使 access.json 的 groups/allowFrom 配置正确也无效。**2026-05-09 已查明真根因并修复**。

**真根因（37 天悬案闭环）**：server.ts line 415 `const recipientId = ch.recipientId ?? dmChannelUserMap.get(id)`。`ch.recipientId` 在 partial DM channel 状态下错返 **bot 自己的 ID**（应为对方 = 主公 ID）。`??` 只在 null/undefined 时 fallback，bot ID 非空 → 不走 dmMap → `allowFrom.includes(bot_id)` → false → 抛错。两边都有 bug，WSL 运气好（ch.recipientId 真的是 undefined → 走 fallback），VPS 不走 fallback 暴露。

**Why:** Discord.js partial DM channel 数据不一致行为；运行时 cache/timing 决定 ch.recipientId 是 undefined 还是 bot ID。

**How to apply:**
- 修复：反转 `??` 顺序为 `dmChannelUserMap.get(id) ?? ch.recipientId`（dmMap 是 inbound gate 验证过的可靠值优先）
- ⚠️ plugin 升级（`~/.claude/plugins/cache/claude-plugins-official/discord/<version>/`）会丢失修复，需重 patch
- 完整诊断/修复脚本/可复用 patch.py：`archive/discord_plugin_reply_bug_fix_2026-05-09.md`
- dmPolicy 保持 `pairing`（不要改 allowlist，会触发 STATIC mode 强制降级路径）
