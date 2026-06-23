#!/usr/bin/env python3
"""
PreToolUse Hook · 拦截 AskUserQuestion（三实例共享）

为什么：AA/BB/CC 三实例都是主公通过 Discord 远程遥控，没人坐在终端前。
AskUserQuestion 工具一调用就弹「终端交互菜单」让人按键选——Discord 看不到这个 UI，
导致模型在等选择、主公在 Discord 干等，双方卡死（friction_log 2026-06-08 记录，
2026-06-22 又复发连卡 3 次）。CLAUDE.md 早有「禁交互式菜单」规则但约束不住惯性，
按 feedback_rule_vs_hook（违反超一次→升级 Hook）改用机制硬拦。

做什么：任何实例调用 AskUserQuestion → 直接 deny，并用 systemMessage 反馈模型
「改用 Discord reply 发文字编号选项」。这是唯一能在卡死「之前」截断的位置
（Stop hook 事后补救来不及，因为卡死发生在工具调用的当下）。

创建：2026-06-22（趋势档案任务后顺手治 BB 反复弹菜单的根因）
配置：共享层 .claude/settings.json → PreToolUse matcher=AskUserQuestion
"""
import json
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    # 读不到输入就放行，不阻塞正常流程
    sys.exit(0)

tool_name = data.get("tool_name", "")

if tool_name == "AskUserQuestion":
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Discord 遥控模式禁用 AskUserQuestion 终端菜单",
        },
        "systemMessage": (
            "❌ 禁止使用 AskUserQuestion（会弹终端交互菜单，主公在 Discord 看不到→卡死）。"
            "改用 Discord reply 工具发文字编号选项，例如："
            "「主公，请选：1) 方案A  2) 方案B」，等主公文字回复。"
        ),
    }
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)

# 其余工具放行
sys.exit(0)
