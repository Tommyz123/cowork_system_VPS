---
name: claude CLI vs Anthropic API
description: 能用claude CLI订阅不调Anthropic API，这是主公的明确原则
type: feedback
originSessionId: b769602c-d31f-44f4-88dc-c7f33006fd41
---
脚本需要AI分析时，优先用 `claude --print --output-format text --dangerously-skip-permissions -p "$PROMPT"` 调用Claude CLI，不调Anthropic API。

**Why:** 主公有Claude订阅，CLI调用不额外付费；API调用每次都要钱。主公说"能用订阅的就用订阅"是明确原则（2026-04-20）。

**How to apply:** 设计脚本方案时，如需AI生成内容，默认方案是subprocess调claude CLI，不要建议anthropic SDK或API key方案。参考：run_daily_news.sh就是范例。
