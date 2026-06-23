# Cowork AI 行为规则

> 最后更新：2026-05-14（全局规则已移至 ~/.claude/CLAUDE.md；本文件只保留 cowork 专属规则）

## 🚀 启动（按需读取）
- **每次对话开始时**：检查 `reference/review_drafts.md` 是否有待确认草稿 → 有内容则第一件事列出来请主公决策
- 被问到文件/项目/信息是否存在或在哪里 → 必须先读 `context.md`，禁止猜路径或直接回答"没有"
- 修改系统架构 → 读 `ARCHITECTURE.md`
- 找具体文件 → 读 `资料/INDEX.md`
- 查项目进度 → 读 `CURRENT_SESSION.md`
- 进入某个项目工作 → 读 `playbooks/<项目名>.md`；每个 playbook 有 frontmatter triggers 字段，匹配关键词自动路由（marketing / legal_library / ai_skill / cowork_system / cannabis_ai_budtender / dutchie_scraper）
- 遇到工具报错或环境问题 → 先查 `reference/knowledge_base.md` 和 `friction_log.md`，有已知解决方案直接用，避免重复踩坑
- 写新脚本或修改脚本 → 先读 `reference/script_standards.md`
- 执行涉及 Claude Code 官方工具/功能（Routines/Hooks/MCP/Skill等）的任务 → 先查 `reference/` 对应规则文件；主公纠正我关于某工具的错误信息时，主动提议"要重新抓取 XXX 规则对齐吗？"
- 修改 `settings.json` → 确认 `env.PATH` 包含所有工具路径（bun/nvm/local等），漏掉会导致 Discord 断连

## 🔧 Skill 快速路由
- 保存进度 / 存一下 / 先存着 → `~/.claude/skills/保存进度/SKILL.md`（轻量，2分钟，日常多次用）
- 收工 / 结束 / 停 → `~/.claude/skills/收工/SKILL.md`（深度审核+push，睡前用一次）
- 整理记忆 → `~/.claude/skills/整理记忆/SKILL.md`
- 搜索历史对话 / 查XXX → `skill: "搜索"`
- 归档 Skills（项目规划/任务清单/审核架构/系统复盘）→ 查 `cowork/skill_archives/INDEX.md`，按索引读对应 SKILL.md 执行
- 创建新Skill → `skill: "skill-creator:skill-creator"`
- 完整 Skill 列表 → `~/.claude/skills/SKILLS_INDEX.md`
- **方法论总索引** → `reference/methodology_index.md`：汇总所有「按需调用方法论」(自有skill_archives + 官方official_plugins + external预留)。主公做营销/法律/数据/项目规划/客户开发等工作时，**主动查此索引的触发点 → 提醒"有现成方法论可借鉴"+给路径**（不自动配置，只提醒+读取套用）；新增方法论必带「来源+日期+类型(self/official/external)」出处三字段

## ✅ 执行确认补充（cowork 专属）
固定触发指令（直接执行，跳过5步）：保存进度 / 读取进度 / 整理记忆 / 收工 / 系统复盘 / 审核系统架构
外部连接/API任务：先读 `reference/knowledge_base.md` 技术踩坑区块，把已知限制写进选项说明
执行前判断：需要「探索→改文件→验证」循环的任务派子agent，其他我直接执行

## 📝 日志（cowork 专属）
日志文件：`cowork_log.md`
保存进度格式：`💾保存进度 | [PX] 项目名 | 本次完成 + 下一步`
文档同步标记：涉及需要同步其他文档的改动，在日志行末加 `[需同步: 目标文件]`；收工时步骤3扫描此标记
归档：日志接近满时（约280行）移至 `archive/cowork_log_YYYY.md`
BACKLOG 写想法必须注明：①真实讨论日期 ②背景/来源 ③决策原因

## 💾 进度管理
- **保存进度**：匹配项目ID [PX] → 更新 `CURRENT_SESSION.md` + 记日志；新项目则新增块
- **读取进度**：读活跃区块 → 列出供选择 → 选后加载；归档超50行提醒处理
- **进度X完成**：移至归档区 + 加完成日期
- 存档格式：`## [PX] 名称 / 状态 / 停在 / 下一步（含路径）/ 路径`

## 🧠 记忆管理
整理记忆 → `skill: "整理记忆"`（流程：auto_pending审核 → 增量扫描 → 列出建议 → 写入 `cowork/memory/` → 更新时间戳；详细步骤以 SKILL.md 为准）

## 💡 Insights 自动记录
判断标准：**下次遇到同类情况会用到 → 就记**。立即追加到 `INSIGHTS.md`（临时缓冲区）：
格式：`[YYYY-MM-DD] [项目/领域] 标题 → 内容（一两行，说清楚怎么用）`
审核后有价值的迁入 `reference/knowledge_base.md`，无价值的删除。
**[ref-worthy] 标记**：有完整流程/配置/踩坑记录的，行末加 `[ref-worthy]`；收工时统一扫描。

## ⚠️ 摩擦记录
遇到规则模糊/冲突/缺失/被纠正/工具限制时，立即追加到 `friction_log.md`：
`[YYYY-MM-DD HH:MM] ⚠️ 类型 | 场景 | 处理方式 | 状态：已自行修复 / 需主公确认`
Skill执行遇到问题 → 额外追加：`[YYYY-MM-DD HH:MM] ⚠️ Skill摩擦 | Skill名称 | 问题描述 | 状态：待讨论`
**归档规则**：系统复盘确认闭环后，已处理条目移至 `friction_log_archive.md`
**被主公纠正时**：额外包含①表面错误 ②根因 ③建议规则变更；末尾加`验证标准`+`验证状态：【待验证】`

## 🪝 Hook 三实例统一（强制）
- **通用 hook 一律放项目共享层** `/home/cowork/cowork/.claude/settings.json` → AA/BB/CC 自动合并继承，改一处=三处同步。**禁止把通用 hook 写进某个实例的用户层 `$HOME/.claude/settings.json`**（会漏配，见 friction_log 2026-06-02）
- 实例专属配置（model/env.PATH/permissions/enabledPlugins/statusLine）才留用户层
- 实例专属 hook（如 P9 的 position_check.py 只在 AA 跑）留对应实例用户层
- **改共享层 settings.json 是「合并不是覆盖」**：必须保留已有 hook（如 log_write_event.py），新 hook 追加
- token（task_approved/git_approved）按实例后缀隔离 `_AA/_BB/_CC`，由 `$HOME` 推导，推导失败拒绝放行
- **收工/保存进度自动授权 git（2026-06-03）**：主公说「收工」「保存进度」时 `discord_approve.py` 额外写 `git_approved_<实例>`（内容 `savework`）；git 守卫见 savework 标记**放行且不消耗**，覆盖整个收工的 commit+push，无需手动 touch。普通授权词（"执行/可以"）只授权文件写入、不碰 git（保持 git 额外谨慎）。每条新消息由 UserPromptSubmit 清空 git_approved 再按本条重授
- **task_approved 响应级授权（2026-06-06）**：整个响应内有效，Stop hook 响应结束自动清除，无需手动 rm；下条消息重新走授权。流程：我列清单→主公批准→我一口气完成所有步骤→Stop自动清
- **token 统一工具（2026-06-07）**：所有 token 操作走 `~/.claude/hooks/token_utils.sh`（write/check/clear），实例推导单一来源
- 共享层配置改完需**重启对应实例**才生效；改前先备份 .bak，可 cp 回滚

## 🗂️ 文档同步维护
- 新增授权文件夹或项目状态变化 → 更新 `context.md` 对应区块
- **新增活跃项目（加入 CURRENT_SESSION.md）→ 同时在 `playbooks/` 新建对应手册**
- 修改 `context.md` → 同步更新顶部"最后更新"日期
- 修改 CLAUDE.md 规则 → 检查 `ARCHITECTURE.md` 和 `memory/` 是否需要同步
- **新增/删除/调用方变更 `cowork/scripts/` 下脚本 → 同步 `cowork/scripts/INDEX.md` 登记册**
- **重构留 `_backup` / `.bak` 文件 → 必须设 7 天兜底删除提醒**（git history 已留底，文件系统副本是认知噪音，长期不删会被误读/误改）

### 项目内外文档双轨同步规则
| 层级 | 位置 | 内容 |
|------|------|------|
| 项目层 | `项目目录/CLAUDE.md` | 代码规范、环境配置（权威来源） |
| 导航层 | `cowork/playbooks/<项目名>.md` | 快速启动、进度指针、协作习惯 |

修改项目 `CLAUDE.md` 的路径或命令 → 必须同步更新 `playbooks/` 对应「快速启动」区块

## 🧠 自动记忆捕获（Auto Pending）
- 看到 `🧠 [记忆捕获]` 提示 → 先过5问题判断（持久/跨对话价值/改变行为/不可推导/够具体），≥3个Yes才写入 `memory/auto_pending.md`
- 看到 `⏳ [待审记忆]` 提示 → **例外：正在执行收工/整理记忆时忽略**；其他情况读并逐条列出请主公确认
- 主公确认后 → 写入正式 `memory/` → 从 `auto_pending.md` 删除已处理条目

## 🤖 子Agent 协作
- 路由判断由平台内置（按子agent说明书自动匹配 `Explore`/`general-purpose`/`Plan`）；拿不准就自己做，不强行派
- 长耗时任务（爬虫/批处理）→ 强制派 `general-purpose`（防阻塞）
- **需授权写文件的子agent任务用同步调用，别用后台**：后台 agent 跑完会在"完成通知"的新响应里触发，此时 task token 已被 Stop hook 清掉 → 子agent 写文件被守卫拦、任务卡死（2026-06-11 趋势地图实锤）。同步调用（原地等它跑完、不结束响应）令牌还在，写文件不被拦
- 子agent改动后：Claude 必须在 cowork_log.md 写带 `[需同步: ...]` 的条目
- **长对话提醒**：对话超过40轮时，主动提醒主公"当前对话已偏长，建议收工开新对话"
