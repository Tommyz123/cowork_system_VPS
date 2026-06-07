---
name: feedback_savework_continuous
description: 收工必须连贯一口气跑完、commit+push全自动，中途绝不停下来反复问git授权
type: feedback
originSessionId: 1a423ab7-bb9f-465f-87c7-51b4a0d0ff11
---
**收工是连贯的、不中途停止的流程——一旦触发就一口气跑完6步，commit+push 全自动，绝不中途停下来反复向主公要 git 授权。**

**Why:** 2026-06-07 主公明确指正"收工是连贯的，没停止的，理解吗？自动commit"。系统本就这么设计（收工SKILL.md：收工commit无需额外确认，discord_approve.py 自动写 git_approved=savework 覆盖整个收工，放行且不消耗）。当天中途卡两次是 bug 不是正常行为——根因：主公第一次"收工"是在上个响应**执行中异步到达**的（system-reminder "message arrived while you were working"），异步消息不触发 UserPromptSubmit 授权链 → savework 标记没生成 → git 守卫误拦。主公独立发"收工"时正常连贯跑完，证明设计本身没问题。

**How to apply:**
- 主公说"收工"时，默认 git 全程已授权（savework），连贯做完全部步骤，不要因 git 守卫拦截就停下问授权——正常情况不会被拦。
- 若真被守卫拦（说明遇到异步时序 bug 等异常），先查 git_approved_<实例> 是否为 savework；缺失则一句话说明 bug 并请主公重发"收工"，不要在收工中途反复纠缠授权细节。
- 待修 bug：让异步到达的"收工"也能触发授权链，或收工检测到 savework 缺失时主动提示。已记 friction_log（2026-06-07）。
