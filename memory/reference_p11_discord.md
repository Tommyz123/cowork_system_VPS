---
name: reference_p11_discord
description: VPS Discord接入参考：plugin已知bug+patch方法+降级方案(discord.py自建bot)
type: reference
originSessionId: 8a06505e-fc15-40da-9a68-546769d6bf1f
---
## 当前方案：Claude Code Discord Plugin

plugin v0.0.4，已 patch 修复 `fetchAllowedChannel` bug。
- patch 位置：`/root/.claude/plugins/cache/.../discord/0.0.4/server.ts`
- ⚠️ plugin 升级后需重新 patch（备份：`server.ts.bak_fix`）
- bug 详情：`ch.recipientId ?? dmChannelUserMap.get(id)` → partial DM channel 下 recipientId 错返 bot 自己 ID；修复：反转为 `dmChannelUserMap.get(id) ?? ch.recipientId`

## 降级备选方案：discord.py 自建 bot

plugin 修不好 / 升级后 patch 失效时可切换。

约 100 行代码，架构：
- 直接监听 Discord 消息（discord.py）
- 调 `claude --print` 处理消息
- 把回复发回频道

**优点**：不依赖 Claude Code plugin 版本，更稳定；双向通信（比 webhook 强）
**缺点**：功能降级（失去 MCP 工具调用能力，只能走 claude --print 文本模式）

适用场景：plugin 频繁出问题、或升级后 patch 代价太高时的替代方案。
