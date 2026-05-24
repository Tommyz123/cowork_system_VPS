# Skill Archives 索引

> 这些 Skill 已从 `~/.claude/skills/` 移除以减少 token 注入（省 ~1500 token/对话）。
> 需要使用时，按下表触发词找到对应路径，读 `SKILL.md` 按步骤执行。
> 移入日期：2026-05-23

## 索引表

| 触发关键词 | Skill 路径 | 功能 |
|---|---|---|
| 生成项目计划 / 项目规划 | `cowork/skill_archives/project-plan-generator/SKILL.md` | 生成 PROJECT_PLAN.md（9/11/13 维度规划文档）|
| 审核项目计划 | `cowork/skill_archives/project-plan-reviewer/SKILL.md` | 审核 PROJECT_PLAN.md 是否符合 SPEC |
| 修复项目计划 | `cowork/skill_archives/project-plan-fixer/SKILL.md` | 根据审核报告修复 PROJECT_PLAN.md |
| 项目工作流 / 完整项目规划流程 | `cowork/skill_archives/project-workflow/SKILL.md` | 一键执行 生成+审核+修复 全流程 |
| 生成 TODOLIST / 任务清单 | `cowork/skill_archives/todolist-generator/SKILL.md` | 从 PROJECT_PLAN 生成 TODOLIST.md（拓扑排序）|
| 审核 TODOLIST | `cowork/skill_archives/todolist-reviewer/SKILL.md` | 审核 TODOLIST.md 是否符合 SPEC |
| 修复 TODOLIST | `cowork/skill_archives/todolist-fixer/SKILL.md` | 根据审核报告修复 TODOLIST.md |
| 审核系统架构 / 审核架构 | `cowork/skill_archives/审核架构/SKILL.md` | cowork 系统架构 7 维度审核 |
| 系统复盘 | `cowork/skill_archives/系统复盘/SKILL.md` | friction_log 归类统计 + 复发检测 |

## 使用方式

主公说出"生成项目计划"等触发词时：
1. 我在此 INDEX 找到对应 SKILL.md 路径
2. Read 读取该 SKILL.md
3. 按文档步骤执行

## 维护规则

- 新增归档 Skill → 在此表加一行
- 启用某个 Skill（搬回 `~/.claude/skills/`） → 删此表对应行
- 路径变动 → 同步更新此表
