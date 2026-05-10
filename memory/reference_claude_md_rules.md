---
name: reference_claude_md_rules
description: Claude Code官方CLAUDE.md规则：行数上限200行，拆分加载机制，token节省方法（2026-04-30更新）
type: reference
---

**来源：** Claude Code 官方文档（code.claude.com/docs/en/memory，2026-04-30核查）

## 核心规则

- **目标行数：每个 CLAUDE.md 控制在 200 行以内**
- 超过 200 行会消耗过多 context，且降低规则遵守率（instruction adherence）
- 官方原话："Longer files consume more context and reduce adherence"

## 拆分方式（两种）—— ⚠️ 都不省 token

**① @import 语法**
```markdown
详细工作流见 @docs/workflows.md
```
- **加载时机：对话启动时全量载入**（非按需）
- "Imported files are expanded and loaded into context at launch"
- 相对路径相对于引用它的文件；最大嵌套深度：5层

**② .claude/rules/ 目录**
按模块拆成多个 .md 文件，Claude Code 启动时自动全部加载：
- **加载时机：启动时自动全量加载**（非按需）
- ⚠️ 已知 bug（2026年初）：~/.claude/rules/ 里带 `paths:` frontmatter 的规则被静默忽略（GitHub #21858）

## ⚠️ 关键结论（2026-04-30验证）

**拆文件 = 零 token 节省，只是整理结构。**
真正要省 token 只有一条路：**直接删内容（减字数），不是拆文件。**

## How to apply

每次修改 CLAUDE.md 前：
1. 先 `wc -l CLAUDE.md` 确认当前行数
2. 超过 180 行 → 优先**删旧内容**，而不是继续加或拆文件
3. 超过 200 行 → 必须拆分（结构整理用，不是为了省 token）
4. 添加新区块时，问自己：能不能合并进现有区块？能不能用一行代替三行？
5. 拆文件只用于**维护方便**，不用于 token 优化
