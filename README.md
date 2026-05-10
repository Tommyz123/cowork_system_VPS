# Cowork System

私人 AI 工作系统，基于 Claude Code 构建。

## 系统概览

这个 repo 追踪 Cowork AI 助手的核心架构文件，包括行为规则、长期记忆、项目进度和工作手册。

## 文件结构

```
CLAUDE.md              # AI 行为规则（唯一权威来源）
ARCHITECTURE.md        # 系统架构说明
context.md             # 文件夹结构与项目状态速查
CURRENT_SESSION.md     # 活跃项目进度
BACKLOG.md             # 待办功能列表
INSIGHTS.md            # 积累的经验与规律
friction_log.md        # 规则摩擦与修复记录

memory/                # 长期记忆（跨会话持久化）
  ├── user_profile.md
  ├── feedback_*.md
  ├── project_*.md
  └── reference_*.md

playbooks/             # 各项目操作手册
  ├── cowork_system.md
  ├── marketing.md
  ├── legal_library.md
  └── ...
```

## 版本控制范围

只追踪系统架构文件。以下内容不在此 repo 中：
- `cowork_log.md`（操作流水账，变动过于频繁）
- `newscripts/`（独立 repo：github.com/Tommyz123/cowork-scripts）
- `backups/`、`scraper/`、`idea/`、`research/`（非系统文件）
