---
name: trading/scripts 读 env 必须用 tide_utils.load_env
description: trading/ 和 scripts/ 下需要读 DISCORD_BOT_TOKEN 等 env 的脚本，必须 `from tide_utils import load_env`，不许本地复制写 load_env()
type: feedback
originSessionId: b68a0307-4fb1-4816-ae90-9f3443efdd9c
---
trading/ 和 scripts/ 下需要读 env（DISCORD_BOT_TOKEN / BREVO_API_KEY / 任何 env）的新脚本，**第一选择 `from tide_utils import load_env`**，不许再本地复制写 `load_env()` 函数。

**Why**: 2026-05-17 P9 一次性提醒发送失败，根因是脚本本地写的 load_env() 只读 `config/api_keys.env`，但 `DISCORD_BOT_TOKEN` 实际在 `~/.claude/channels/discord/.env`（api_keys.env 顶部注释有说明，被忽略）；扫描发现 trading/ 下 6 个脚本全部有同一 bug（scanner_tracker/thesis_monitor/price_guard/quarterly_review/cognitive_scanner/close_position）。`tide_utils.load_env` 已经写好了正确的 fallback 逻辑——先读 api_keys.env，缺 DISCORD_BOT_TOKEN 就 fallback 到 .claude/channels/discord/.env。本地复制粘贴 load_env 等于绕过这个 fallback。

**How to apply**:
- 写 trading/ 下任何新 .py：直接 `from tide_utils import load_env`，绝不本地定义 load_env()
- 写 scripts/ 下需要发 Discord/邮件的脚本：用 `sys.path.insert(0, '/home/cowork/cowork/trading')` 后 `from tide_utils import load_env`；或者完整复制 tide_utils.load_env 的 fallback 逻辑（含读 ~/.claude/channels/discord/.env）
- 看到现存脚本本地写 load_env() → 主动建议替换成 tide_utils.load_env
- 第二次再发生这个 bug → 升级为 PreToolUse Hook 强制拦截（按 feedback_rule_vs_hook 规则）
