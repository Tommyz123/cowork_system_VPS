---
name: feedback_rule_vs_hook
description: 规则描述期望，Hook强制执行——关键行为失效两次后升级为Hook
type: feedback
originSessionId: 80cd57ca-8b2f-42e7-8497-a4482b30b813
---
**规则 vs Hook 选择原则（2026-05-07确立）：**

规则描述期望行为；Hook 强制执行行为。两者不等价。

**Why:** Discord reply 漏发和立场一致性都曾是 CLAUDE.md 规则，但执行失败——规则存在不等于行为被约束。改用 Stop Hook（reply漏发检测）和 UserPromptSubmit Hook（立场一致性注入）后才形成真正约束。

**How to apply:** 某个行为规则被违反超过一次 → 评估是否能用 Hook 强制执行，能则升级；不能用 Hook 的（如判断类行为）才保留为纯规则。
