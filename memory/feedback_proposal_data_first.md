---
name: feedback_proposal_data_first
description: 推系统优化方案前必须先拉friction_log/cowork_log数据验证痛点真实性，禁止凭直觉推方案
type: feedback
originSessionId: f80ef6e0-4363-4121-ac5d-b927f4613745
---
**核心规则：推任何"系统优化/新机制/新工具"类方案前，第一动作 = 拉数据验证痛点真实性。**

具体操作：
1. `grep` friction_log.md 看相关类型的摩擦真实频率（近4周多少条？）
2. `grep` cowork_log.md 看相关事件密度
3. 频率低 → 痛点可能不成立 → 先说明再推方案或建议 BACKLOG

**Why:** 2026-05-21 花了 5-6 轮推 CodeGraph D/F/G/H 方案，主公两次追问"用证据说话"后才去拉 friction_log → 发现 4 周 0 条"漏更新关联文件"记录，整套讨论的假设前提不成立。这是 feedback_honesty 的"数据诚信"规则在方案审议阶段的扩展——不只是陈述事实时要有来源，提方案时也要有数据支撑。

**How to apply:**
- 触发条件：我主动提议"我们可以做 X 来改善 Y"时
- 先说："我去查一下 Y 的实际 friction 频率"
- 频率 ≥ 2次/2周 → 有依据推方案
- 频率 = 0 或极低 → 说"friction 数据不支持这个优先级，建议 BACKLOG"
