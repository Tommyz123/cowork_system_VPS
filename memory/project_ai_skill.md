---
name: project_ai_skill
description: AI Skill 框架研究项目背景：cc_skill 框架、V5 版本、多智能体（进度见 CURRENT_SESSION.md）
type: project
originSessionId: 5c7836eb-106d-4460-b97f-2e692a4e1082
---
主公自主开发的 Claude Code AI 控制框架集合，从 资料/c_project/ 独立出来单独管理。

**Why:** 研究和优化 Claude Code 的技能框架，用于提升 AI 助理能力和可复用性。

**How to apply:** 涉及 cc_skill、skill、context 框架、多智能体时，直接使用此背景。目录结构和工作流见 `playbooks/ai_skill.md`。

**P2方向决策（2026-04-17）：**
从"规则文字约束AI自律"→"Hook/Skill自动执行"。
可观测行为→Hook/Skill强制执行；对话质量规则→留CLAUDE.md。

**关键历史决策：**
- SQLite优先：主公原话"历史数据现在不存就永远没有"，cowork.db与JSONL同步建立（2026-04-17）
