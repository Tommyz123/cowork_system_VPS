---
name: Skill执行与历史查询规则
description: Skill触发限制+历史设计类问题的正确两步查询流程
type: feedback
originSessionId: 9d2c8c96-b073-4c5e-ba3b-e71935c35b53
---
**规则1：自研Skill的触发方式**
`disable-model-invocation: true` 的 Skill 不能用 Skill tool 触发，必须直接读 SKILL.md 在当前上下文执行。Discord 工作流下不适合用斜杠命令（需切到终端）。

**Why:** Claude Code Skill tool 调用受此 flag 限制；Discord 无法直接执行终端斜杠命令。

**How to apply:** 收到"收工/整理记忆/系统复盘/审核架构"等指令 → 直接读对应 SKILL.md 文件，按步骤执行，不调用 Skill tool。

**延伸：** SKILL.md 是纯 Markdown 指令文件，模型无关 — Codex 或其他 AI 也可以通过读文件来执行这些 Skill。

---

**规则2：历史设计类问题两步查询**
遇到"为什么这样设计"或"XXX功能现在状态"类问题，必须两步都做：
① 先读相关 `memory/` 文件了解背景决策
② 再用搜索 Skill 查历史对话确认实际部署状态

**Why:** 只读 memory 可能停留在计划阶段，漏掉已上线的变化；只搜历史可能缺背景原因。被纠正过一次（回答某功能状态时说"还没做"，实际已上线）。

**How to apply:** 任何涉及"当时为什么/现在状态"的问题，两步缺一不可。
