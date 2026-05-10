# Insights — 临时缓冲区

> **工作流：** 新经验写这里 → 健康检查触发审核 → 有价值的迁入 `reference/knowledge_base.md` → 清空
> 格式：`[YYYY-MM-DD] [项目/领域] 标题 → 内容（一两行，说清楚怎么用）`
> 已审核的稳定参考知识在：`reference/knowledge_base.md`

---

[2026-05-07] [系统管理] 系统停用/改方向必须三层同时清理 → 停用系统时不能只停代码：①DB旧记录（DELETE/DROP旧系统表）②账号旧持仓（平掉旧系统建的仓）③引用文件（playbook/memory里的遗留描述）；缺任何一层都会导致新系统数据混乱无法信任

[2026-05-09] [Claude Code] `claude --channels plugin:<name>@<marketplace>` 是 plugin channel 订阅开关 → 不带这个参数 host 不会订阅 plugin notification（如 Discord plugin 的 `notifications/claude/channel`），收到也直接丢；部署 systemd/守护服务时容易漏（VPS P11 真根因）；TUI 启动后会显示 "Listening for channel messages from: ..." 一行可作为订阅生效证明

[2026-05-09] [Claude Code] 诊断 plugin/工具执行失败必须先看 claude session jsonl（`~/.claude/projects/<cwd>/<sid>.jsonl`），解析 `user/assistant/tool_use/tool_result` 事件流看 claude 实际做了什么；只看 hook log/server stderr 会反复误判（P11 4 次诊断错的核心教训）。Python 解析模板见 `archive/discord_plugin_reply_bug_fix_2026-05-09.md` 里的 `parse_session.py` 思路

[2026-05-09] [Discord plugin] v0.0.4 `fetchAllowedChannel` 在 partial DM channel 状态下 `ch.recipientId` 错返 bot 自己 ID，导致 reply 抛 "channel is not allowlisted" → 修复：反转 `??` 顺序为 `dmChannelUserMap.get(id) ?? ch.recipientId`（dmMap 是 inbound 验证过的可靠值）；plugin 升级后会丢失，需重 patch；详细诊断+修复脚本见 `archive/discord_plugin_reply_bug_fix_2026-05-09.md`

[2026-05-09] [Claude Code] `??` 操作符盲区：只在 null/undefined 时 fallback，"错的非空值"会跳过 fallback；当主数据源不可靠（如 partial 数据/外部 API），应把 fallback 设为优先 `fallback ?? primary` 或加显式校验；写代码时遇到 `primary ?? cache` 模式要警惕

[2026-05-09] [Discord plugin] reply 等 5 个 mcp 工具应加到 settings.json `permissions.allow` 免每次弹 permission：`mcp__plugin_discord_discord__{reply,react,edit_message,fetch_messages,download_attachment}`；设计哲学：发回主公自己 channel 等同于 Write(Desktop/*) 白名单，永远 allow 无风险
