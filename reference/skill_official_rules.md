# Claude Code 官方 Skill 规则参考

> 来源：Claude Code 官方文档（context7，2026-04-16）
> 每次做新 Skill 前必须参照此规则

---

## 1. 目录结构

```
.claude/skills/<skill-name>/   ← 项目级（当前项目可用）
└── SKILL.md

~/.claude/skills/<skill-name>/ ← 全局级（所有项目可用）
└── SKILL.md
```

旧格式（不推荐）：`.claude/commands/<name>.md`

---

## 2. SKILL.md frontmatter 字段

```yaml
---
name: skill-name                    # 必填：Skill名称，决定 /command 名
description: "触发说明..."          # 必填：Claude 用来判断何时自动调用
allowed-tools: Read, Grep, Bash    # 可选：允许的工具（空格或列表分隔）
model: claude-opus-4-6             # 可选：指定模型
disable-model-invocation: true     # 可选：禁止自动触发（仅手动 /command）
---
```

---

## 3. description 写法规范

- 说清楚"什么情况下触发" → Claude 用来判断是否自动调用
- 格式：`Use when <场景>. <功能说明>.`
- 示例：
  ```
  description: Reviews code for best practices. Use when reviewing code, checking PRs, or analyzing code quality.
  ```

---

## 4. 完整 SKILL.md 示例

```markdown
---
name: security-check
description: Run security vulnerability scan. Use when asked to check for security issues, vulnerabilities, or exposed credentials.
allowed-tools: Read, Grep, Glob
model: claude-opus-4-6
---

Analyze the codebase for security vulnerabilities including:
- SQL injection risks
- XSS vulnerabilities
- Exposed credentials
- Insecure configurations
```

---

## 5. 使用 skill-creator 创建 Skill

每次新建 Skill 必须通过 `/skill-creator:skill-creator` 调用官方工具：
- 会生成符合规范的 SKILL.md
- 自动验证 frontmatter 格式
- 可测试 Skill 触发准确性

---

## 6. 关键原则

1. **description 是灵魂** — 写不好 Claude 不会自动触发
2. **allowed-tools 最小化** — 只给 Skill 需要的工具
3. **项目级 vs 全局级** — 系统工具（如/收工）放全局 `~/.claude/skills/`
4. **一个 Skill 一个目录** — 不要把多个 Skill 塞进一个文件
5. **disable-model-invocation** — 只手动触发的 Skill 加此字段，避免误触发
6. **$ARGUMENTS** — slash command 后的文字自动捕获为 `$ARGUMENTS`，可在 SKILL.md 内容中引用

---

## 7. skill-creator 调用方式

skill-creator 是插件级 Skill，调用方式：
```
/skill-creator:skill-creator
```
用途：创建新 Skill / 修改现有 Skill / 测试 Skill 触发准确性
每次新建 Skill 必须通过此工具生成，确保符合官方规范。

---

## 8. /收工 Skill 特别注意

/收工 是手动触发，必须加 `disable-model-invocation: true`，防止 Claude 在对话中自动触发收工流程。
位置：`~/.claude/skills/收工/SKILL.md`（全局级，所有项目可用）
