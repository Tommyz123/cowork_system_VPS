---
name: project_design_principles
description: Cowork系统设计讨论时必须考虑的维度：模型无关性（不绑定特定AI）
type: project
originSessionId: fb7379c1-70fd-4004-8ae4-b866fc324cb8
---
**Cowork 系统设计原则：模型无关性**

主公希望系统日后可以灵活切换模型（Claude / GPT / Gemini 等），不被任何一家锁死。

**Why:** 2026-04-16 讨论 Codex 建议时确定；主公明确说"日后喜欢什么模型都可以直接用"。

**How to apply:** 讨论系统架构或设计方案时，主动把"模型无关性"列为评估维度之一——该方案是否依赖 Claude Code 专属能力？是否容易替换调用层？
