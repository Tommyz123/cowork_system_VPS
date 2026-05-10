# Cowork 系统架构说明

> 最后更新：2026-05-10（权限与守卫体系扩展：加 settings.json defaultMode/allow/deny + task-scoped 工作流；文件表加 MIGRATION_LOG.md）
> 用途：帮助 AI 在新对话中快速理解整套系统，不需要主公重复解释

---

## 一、整体结构

```
Claude 内部（跨对话持久）
  └── memory/          ← 【记忆层】AI 对主公的长期理解积累

Desktop/
  ├── cowork/          ← 【总控制层】AI 行为规则 + 全局地图
  ├── 资料/            ← 【主文件库】所有个人文件的归档地
  ├── marketing/       ← 【项目文件夹】纽约大麻 AI 顾问项目
  └── 其他文件夹...
```

**三个层次：**
- **memory/**（Claude 内部）= 跨对话记忆层，存储 AI 对主公的长期理解
- **cowork/** = 大脑，管所有事，告诉 AI 怎么工作、在哪找东西
- **各项目文件夹** = 被管理的对象，各自有自己的规则和索引

---

## 二、memory/ 层（跨对话记忆层）

**位置（双路径，需了解区别）：**
- Claude 内部路径：`/home/zhi8939/.claude/projects/-mnt-c-Users-zhi89-Desktop-cowork/memory/` — auto-memory 系统自动写入此处；每次对话自动加载 MEMORY.md
- Desktop 本地路径：`/mnt/c/Users/zhi89/Desktop/cowork/memory/` — 手动整理记忆写入此处；被 git 版本控制追踪

**两条写入路径说明：**
- **auto-memory**（Claude Code 平台内置）：对话中自动判断并写入 Claude 内部路径，无需触发
- **整理记忆**（主公触发）：人工审查后写入 Desktop 本地路径，同时更新 MEMORY.md 索引

**同步策略：** 每次执行"整理记忆"时，对比两个路径的文件差异，有分叉则合并，保持一致。

**用途：** 存储 AI 对主公的长期理解，跨对话持久生效。

| 文件 | 职责 | 加载方式 |
|------|------|---------|
| `MEMORY.md` | 记忆索引（v4升级：每条含核心内容摘要，可直接使用，无需每次读具体文件） | 每次对话自动载入 |
| `auto_pending.md` | 自动捕获缓冲区：AI在对话中自动判断是否值得存入，无固定触发周期，待 Claude 审核后写入正式文件 | 有[开头条目时列出审核 |
| `user_profile.md` | 主公基本信息（称呼、背景、偏好） | AI 判断相关时主动读取 |
| `feedback_honesty.md` | AI 行为反馈（哪些做法被认可/纠正） | AI 判断相关时主动读取 |
| *(其他记忆文件)* | 项目背景、引用资源等 | 按需读取 |

**记忆类型：**
- `user` — 主公的角色、目标、知识背景
- `feedback` — AI 行为规则（做了什么被纠正/认可）
- `project` — 项目背景和动机（非代码可推导的部分）
- `reference` — 外部资源位置（Linear 项目、Grafana 看板等）

**使用规则：**
- MEMORY.md 对话开始自动进来，AI 知道有哪些记忆
- 遇到相关场景，AI 主动读取对应记忆文件
- 对话中学到新内容，AI 写入新记忆文件并更新 MEMORY.md 索引
- 记忆可能过时，使用前先验证是否仍然准确

> ⚠️ **v2 变更**：v1 存在两套记忆（`.auto-memory/` + `cowork/memory/`）并存的问题。v2 起，手动整理记忆的真实源为 `cowork/memory/`（git 追踪），`.auto-memory/` 已废弃。
> ⚠️ **v3 说明**：auto-memory（平台内置）写入 Claude 内部路径，整理记忆写入 Desktop 本地路径，两者独立运行，通过整理记忆时的人工对比保持同步。

---

## 三、cowork/ 层（总控制层）

| 文件 | 职责 | 什么时候读 |
|------|------|----------|
| `CLAUDE.md` | AI 全局行为规则（称呼/启动流程/日志规则/进度管理） | Claude Code 自动加载，每次对话生效 |
| `ARCHITECTURE.md` | 本文件，系统架构说明 | 新对话开始时，需要理解系统时 |
| `context.md` | 全局地图：电脑上有哪些文件夹、各是什么、活跃项目状态 | 需要找文件或了解项目状态时 |
| `cowork_log.md` | 操作流水账：每次文件操作/任务都记一行 | 回顾历史操作时 |
| `friction_log.md` | 摩擦日志：规则模糊/冲突/缺失/被纠正/工具限制时自动写入，系统复盘时分析 | 说"系统复盘"时；收工时检查本次记录 |
| `CURRENT_SESSION.md` | 项目进度存档：各项目当前停在哪、下一步是什么（**v2 唯一进度来源**） | 说"保存进度"或"读取进度"时 |
| `INSIGHTS.md` | 可复用经验积累：有效方法/领域知识/踩坑解法，AI 自动写入 | 项目工作中遇到值得记录的经验时 |
| `BACKLOG.md` | 系统改进想法积压：短条目，注明触发条件 | 有新想法时追加；阈值触发时取来实现 |
| `MIGRATION_LOG.md` | 系统级迁移记录：VPS迁移/重大基础设施变更，时间倒序，每次迁移顶部追加新章节 | 排查迁移遗留问题、了解基础设施变更历史时 |
| `VERSIONS.md` | Cowork 框架版本历史：每次升级记录变更，出问题时对照还原 | 框架升级前后查阅 |
| `INDEX_TEMPLATE.md` | 通用模板：放进任意文件夹后让 AI 生成该文件夹的 INDEX.md | 需要为新文件夹建索引时使用 |
| `idea/` | 详细计划文档：求职、方案、模板等，单独成文件 | 需要展开记录详细计划时 |
| `playbooks/` | 各项目操作手册：启动序列/工作流/格式标准（v4升级：含 frontmatter triggers 触发词，匹配关键词自动路由） | 进入某个项目工作前读对应文件 |
| `backups/v1/` | v1 架构完整备份，含 CLAUDE.md / ARCHITECTURE.md / context.md / memory/ | 需要回退时读取 |
| `newscripts/` | 自动化工具脚本：每日新闻 RSS 抓取 + Discord DM 推送，含 Agent 操作指令 | 修改新闻配置时读取 news_agent_instructions.md |
| `flightscripts/` | 机票监控 Agent：SerpAPI查价 + SQLite历史 + Claude分析 + Discord日报，每天17:30 EDT自动运行 | 修改监控路线/阈值时读取 README.md |
| `research/` | 技术研究笔记：Claude Code 源码分析等，供下次对话复用 | 进行技术研究或参考历史分析时 |
| `scripts/` | 自动化Python脚本：setup_db / index_conversations / search_conversations / log_session | 维护 cowork.db 对话搜索系统时 |
| `reference/` | 参考文档：`skill_official_rules.md`（Skill规范）+ `knowledge_base.md`（已审核技术参考库，遇报错先查） | 创建新 Skill、遇工具报错或环境问题时 |
| `trading/` | P9 TIDE量化交易系统：`cognitive_scanner.py`(季度建仓扫描) / `signal_collector.py`+`signal_alert.py`(每日信号) / `screener.py`(月度候选股池) / `close_position.py`(手动平仓+归因) / `quarterly_review.py`(季度复盘) / `trading.db`(scanner_picks/trades/thesis_alerts) | 查看P9状态、修改策略时；入口脚本：`bash run_scanner.sh` |
| `cowork.db` | FTS5+向量对话搜索数据库：conversations/sessions/session_embeddings/message_embeddings（1844条消息级向量） | 搜索历史对话（/搜索 Skill）；收工时自动写入 |

**Skill 系统**（2026-04-17 上线，位置 `~/.claude/skills/`；本地备份 `cowork/skills/`）：

| Skill | 调用方式 | 功能 |
|-------|---------|------|
| `/收工` | `skill: "收工"` | 4步会话结束流程（保存进度+日志 / 文档同步检查 / 备份+commit+push / 写入cowork.db） |
| `/搜索` | `skill: "搜索"` | 自然语言搜索 cowork.db 历史对话 |
| `/整理记忆` | `skill: "整理记忆"` | 5步记忆整理流程（auto_pending审核→对比双路径→写入→更新时间戳） |
| `/系统复盘` | `skill: "系统复盘"` | friction归类统计→检查复发→输出报告→等确认后修改 |
| `/审核架构` | `skill: "审核架构"` | 7维度系统架构检查，输出问题清单 |
| `project-plan/todolist 系列` | 各自 skill 名 | 项目规划工作流（生成/审核/修复） |
| `SKILLS_INDEX.md` | 读取文件 | 所有 Skill 的触发词/调用语法/不适用场景说明书 |

**Hook 守卫系统**（2026-04-13 上线，配置在 `~/.claude/settings.json`）：
完整文档见 [`reference/hooks_system.md`](reference/hooks_system.md)（14项 Hook 详细说明 + 授权流程图）

| Hook | 触发时机 | 作用 |
|------|---------|------|
| `git_commit_guard.sh` | PreToolUse(Bash) | 拦截 git commit/push；拦截 Claude 自行 touch task_approved |
| `system_file_guard.sh` | PreToolUse(Edit/Write) | 白名单放行；其他文件需 task_approved token |
| `discord_approve.py` | UserPromptSubmit | 检测授权关键词（"可以执行"等）→ 自动 touch task_approved |
| `honesty_check.sh` | Stop | 检测声称读完但实际只读了部分文件 |
| `discord_reply_check.sh` | Stop | Discord 消息漏回复时 block |
| `rm -f /tmp/task_approved` | UserPromptSubmit | 每次主公发消息自动清除授权 token |

**Codex 执行层**（2026-04-20 接入）：

| 项目 | 说明 |
|------|------|
| 角色 | 代码/脚本/文件批处理的执行者；我（Claude）负责策划+验收，Codex 负责执行 |
| 调用方式 | `codex-companion.mjs task --background "..."` → 轮询 status → 读取 result |
| 适用任务 | 写代码、跑脚本、文件批处理（有明确输入输出的任务） |
| 不适用 | 理解意图、策略讨论、需要上下文判断的任务（这些由 Claude 处理） |
| 认证 | `codex login` 在 Claude Code 终端运行；token 过期需重新 `codex logout && codex login` |

**版本控制：** cowork/ 系统文件已建立 Git 版本控制，推送至 github.com/Tommyz123/cowork_system（私有）。追踪范围：CLAUDE.md、ARCHITECTURE.md、context.md、memory/、playbooks/ 等核心文件；排除 cowork_log.md、newscripts/、backups/ 等。

**运行原则（2026-04-20确立）：**
- **CLI优先**：脚本需要AI分析时用 `claude --print`（订阅），不调 Anthropic API（付费）
- **纽约时间**：所有时间表达用纽约时间（EDT/EST），不说UTC

---

## 四、资料/ 层（主文件库）

**用途：** 主公电脑上所有个人文件的统一归档地。

| 文件 | 职责 | 什么时候读 |
|------|------|----------|
| `INDEX.md` | 资料/内部所有文件夹和文件的详细语义索引 | 找具体文件时，先读这里 |
| `RULES.md` | 文件整理规则：收件箱流程/重命名/去重/更新规范 | 整理新文件前读，确认操作规范 |

**内部文件夹结构（顶层）：**

| 文件夹 | 用途 |
|--------|------|
| `cannabis/` | 大麻零售创业全套（商业计划/法规/数据/合同） |
| `c_project/` | AI 技术开发与学习项目 |
| `数据分析/` | 数据科学项目集 |
| `个人文档/` | 简历、证件、Fiverr 作品集 |
| `出租lease/` | 出租房产管理 |
| `_待整理/` | 新文件收件箱（整理入口） |
| *(其他文件夹)* | 见 INDEX.md 完整列表 |

---

## 五、其他项目文件夹

每个活跃项目文件夹有自己的规则文件：

| 文件夹 | 规则文件 | 索引文件 |
|--------|---------|---------|
| `marketing/` | `CLAUDE.md` | `PROJECT_INDEX.md` |
| `legal_library/` | `RULE.md` | `INDEX.md` |
| `cc_skill/` | 无独立规则文件 | 各子目录 README |
| `cannabis_AI_BUDTENDER/` | `CLAUDE.md` + `agents.md` | — |
| `cowork/scraper/`（⏸️ paused） | `playbooks/dutchie_scraper.md` | — |

---

## 六、文件之间的关系

```
memory/MEMORY.md（自动载入）
  └── 索引 → 各记忆文件（user_profile / feedback / project 等）
        存：AI 对主公的长期理解，跨对话持久

context.md
  └── 高层导航："资料/ 里有 cannabis/、c_project/ 等，找细节去 INDEX.md"
      └── INDEX.md
            └── 详细记录：资料/ 下每一个资料/文件夹的路径、关键词、状态

CLAUDE.md（cowork）
  └── 总规则，覆盖所有项目
      ├── 资料/RULES.md → 文件整理专属规则
      ├── marketing/CLAUDE.md → 该项目专属规则
      └── playbooks/<项目名>.md → 各项目操作手册（启动序列/工作流/格式）
```

**核心原则：**
- context.md = 高层导航（知道去哪找）
- INDEX.md = 详细目录（知道具体是什么）
- 两者不重复细节，context.md 指向 INDEX.md

---

## 七、更新规则（谁更新谁）

| 发生了什么 | 更新哪里 |
|-----------|---------|
| 资料/ 内部文件变动（新增/移动/删除） | INDEX.md ✅，context.md ❌ |
| 资料/ 顶层新增文件夹 | INDEX.md ✅，context.md ✅（文件夹列表） |
| 项目状态有进展 | `CURRENT_SESSION.md` ✅（v2 起不再更新 context.md 活跃项目快照） |
| 桌面新授权文件夹 | context.md 新增区块 ✅ |
| 每完成一个主公意图（不是每次文件修改） | cowork_log.md ✅（必须） |


> ⚠️ 行为规则（启动顺序、场景触发等）统一以 `CLAUDE.md` 为准，ARCHITECTURE.md 只描述架构结构。

---

## 八、v1 → v2 变更摘要（2026-03-24）

| 变更点 | v1 | v2 |
|--------|----|----|
| 记忆来源 | `.auto-memory/` + `cowork/memory/` 双轨并存 | 唯一来源：`cowork/memory/` |
| 保存进度更新范围 | CURRENT_SESSION.md + context.md + memory/project_*.md | 只更新 CURRENT_SESSION.md |
| context.md 活跃项目区块 | 每次进度保存自动维护 | 静态描述，不再跟踪进度 |
| memory/project_*.md | 含进度字段 | 移除进度字段，只存项目背景 |
| 版本控制 | 无 | 新增 `backups/v1/` + `VERSIONS.md` |
