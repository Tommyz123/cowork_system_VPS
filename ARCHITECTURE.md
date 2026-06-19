# Cowork 系统架构说明

> 最后更新：2026-06-10（记忆系统 v5：三实例原生路径 symlink 合一到 cowork/memory，根治双目录漂移）
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

**唯一记忆源：** `/home/cowork/cowork/memory/`（git 版本控制追踪，三实例 AA/BB/CC 共享同一份）

**原生 auto-memory 与自建记忆的关系（2026-06-10 v5：symlink 合一）：**
- 平台 auto-memory 默认写各实例独立路径（`$HOME/.claude/projects/<cwd>/memory/`），三实例各记各的 → 曾导致双目录漂移（6/7"原生路径从未写入"的判断是错的——原生机制一直在写，2026-06-10 实测抓到漂移）
- **现行结构**：三实例的原生路径**全部 symlink → `cowork/memory/`**；原生机制和自建规矩写的是同一份物理文件，每次对话原生注入的 MEMORY.md 就是 git 正本
- 好处：三实例共享 + git 可审查可回滚 + 原生自动注入照常工作，零漂移
- ⚠️ 新实例上线必须补 symlink 并 readlink 实测，checklist 见 `memory/reference_dual_bot.md`「Memory 例外」区块

**写入方式：** 主公触发"整理记忆" → 人工审查后写入 `cowork/memory/` + 更新 MEMORY.md 索引

**用途：** 存储 AI 对主公的长期理解，跨对话 + 跨实例持久生效。

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
> ⚠️ **v4 说明（2026-06-07）**：废除"双路径同步"机制，唯一记忆源定为 `cowork/memory/`。
> ⚠️ **v5 说明（2026-06-10）**：v4"原生路径留空不用/从未写入"判断有误（原生机制一直在写，导致漂移+CC漏链裸跑）。改为三实例原生路径全部 symlink → `cowork/memory/`，物理合一。详见上方「原生 auto-memory 与自建记忆的关系」。

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
| `scripts/` | 自动化Python脚本：setup_db / index_conversations / search_conversations / log_session / **cannabis_docket_reminder.py** (NY大麻诉讼周提醒)；**所有脚本登记见 `scripts/INDEX.md`**（状态/调用方/频率/依赖） | 维护 cowork.db 对话搜索系统时；查 cron 任务总览见 `reference/cron_jobs.md` |
| `reference/` | 参考文档：`skill_official_rules.md`（Skill规范）+ `knowledge_base.md`（已审核技术参考库，遇报错先查）+ **`cron_jobs.md`（所有 cron 任务唯一总索引）** + `agent_view_rules.md`（Agent View 调研笔记）+ `dual_bot_setup_log.md`（双bot架构记录）| 创建新 Skill、遇工具报错或环境问题、加新 cron 任务时 |
| `trading/` | P9 TIDE量化交易系统：`cognitive_scanner.py`(季度建仓扫描) / `signal_collector.py`+`signal_alert.py`(每日信号) / `screener.py`(月度候选股池) / `close_position.py`(手动平仓+归因) / `quarterly_review.py`(季度复盘) / `trading.db`(scanner_picks/trades/thesis_alerts) | 查看P9状态、修改策略时；入口脚本：`bash run_scanner.sh` |
| `cowork.db` | FTS5+向量对话搜索数据库：conversations/sessions/session_embeddings/message_embeddings（1844条消息级向量） | 搜索历史对话（/搜索 Skill）；收工时自动写入 |

**Skill 系统**（2026-04-17 上线，位置 `~/.claude/skills/`；本地备份 `cowork/skills/`）：

| Skill | 调用方式 | 功能 |
|-------|---------|------|
| `/收工` | `skill: "收工"` | 6步会话结束流程（保存进度+日志 / 文档同步检查 / 备份+commit+push / 写入cowork.db / 深度审核草稿 / 索引更新） |
| `/搜索` | `skill: "搜索"` | 自然语言搜索 cowork.db 历史对话 |
| `/整理记忆` | `skill: "整理记忆"` | 记忆整理流程（auto_pending审核→增量扫描→列出建议→写入 cowork/memory→更新时间戳；步骤以 SKILL.md 为准） |
| `/系统复盘` | `skill: "系统复盘"` | friction归类统计→检查复发→输出报告→等确认后修改 |
| `/审核架构` | `skill: "审核架构"` | 7维度系统架构检查，输出问题清单 |
| `project-plan/todolist 系列` | 各自 skill 名 | 项目规划工作流（生成/审核/修复） |
| `SKILLS_INDEX.md` | 读取文件 | 所有 Skill 的触发词/调用语法/不适用场景说明书 |

**Hook 守卫系统**（2026-04-13 上线，配置在 `~/.claude/settings.json`）：
完整文档见 [`reference/hooks_system.md`](reference/hooks_system.md)（15项 Hook 详细说明 + 授权流程图）

**Hook 命中日志机制**（2026-05-23 上线）：每个 hook 顶部加 1 行调用共享 logger `~/.claude/hooks/_log_hit.sh`（bash hook）或 `_log_hit.py`（python hook），统一写入 `cowork/logs/hook_hits.log`（格式 `[ts] hook | event | outcome`），供使用频率审计（5/30 首次审计 → 砍 0 触发 hook）。

| Hook | 触发时机 | 作用 |
|------|---------|------|
| `git_commit_guard.sh` | PreToolUse(Bash) | 拦截 git commit/push；拦截 Claude 自行 touch task_approved |
| `system_file_guard.sh` | PreToolUse(Edit/Write) | 白名单放行；其他文件需 task_approved token |
| `discord_approve.py` | UserPromptSubmit | 检测授权关键词（"执行"等）→ 自动 touch task_approved |
| `discord_ts_convert.py` | UserPromptSubmit | Discord 消息时间戳转换 → 注入纽约时间上下文（`⏰ Discord消息时间`） |
| `honesty_check.sh` | Stop | 检测声称读完但实际只读了部分文件 |
| `discord_reply_check.sh` | Stop | Discord 消息漏回复时 block |
| `rm -f /tmp/task_approved` | UserPromptSubmit | 每次主公发消息自动清除授权 token |

**子Agent 协作层**（2026-06-07 精简：路由判断改用平台内置自动匹配，删除手写①②④判据）：

| 项目 | 说明 |
|------|------|
| 角色 | Claude 策划+验收，子Agent 执行（读多文件+改+验证场景） |
| 路由规则 | 平台内置自动匹配（按子agent说明书选 `Explore`/`general-purpose`/`Plan`）；拿不准就自己做，不强行派；长耗时（爬虫/批处理）强制 `general-purpose` 防阻塞 |
| 指令写法 | 路径+做什么+约束；禁止背景/解释；改前读现状，验证通过才完成，卡住即报告 |

**Auto-RCA 子系统**（2026-05-18 上线）：

错误自动根因分析五件套，触发后按分级（trivial/minor/major/critical）处理：

| 组件 | 位置 | 作用 |
|------|------|------|
| 规则 | `memory/feedback_auto_rca.md` | 三档分级标准 + 5元触发器 + 反糊弄约束 |
| 触发入口 | `friction_log.md` | minor 以上写入，major 另建 RCA 文档 |
| RCA 文档 | `trading/rca/` | major/critical 事件完整五问分析（按日期命名） |
| 执行接口 | `Skill: auto-rca` | 触发 RCA 流程的 Skill 入口 |
| 结果记录 | `cowork_log.md` | 每次 RCA 结果写日志 |

触发条件（满足任一）：主公纠正 / hook报错 / 数据不一致 / 工具失败 / 我自判为major级错误。

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
