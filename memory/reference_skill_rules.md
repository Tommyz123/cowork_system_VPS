---
name: reference_skill_rules
description: Claude Code Skill官方规则和cowork自定义约定：何时用skill-creator，何时可手写，Skill目录结构
type: reference
---

**官方Skill规则存档位置：** `cowork/reference/skill_official_rules.md`

**何时必须用skill-creator：**
- 新的有判断逻辑的Skill（参数解析、输出格式不确定）
- 需要测试案例验证正确性的Skill

**何时可直接手写SKILL.md（例外场景）：**
- 从CLAUDE.md迁移的Skill（内容稳定、1:1搬运，无新逻辑）
- 确认后在SKILLS_INDEX.md注明"内容稳定，免eval"

**Skill目录结构：**
- 实体位置：`~/.claude/skills/<skill名>/SKILL.md`（Claude Code全局加载）
- 本地备份：`cowork/skills/<skill名>/SKILL.md`（git追踪，可版本控制）

**当前自研Skill（cowork/skills/）：**
收工 / 搜索 / 整理记忆 / 系统复盘 / 审核架构

**How to apply:** 创建新Skill时先判断类型，稳定迁移型可手写，新能力必须用skill-creator。
