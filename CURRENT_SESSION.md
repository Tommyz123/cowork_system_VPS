# 进度管理

> 读取指令：说"读取进度"显示活跃列表；说"保存进度"更新对应存档；说"进度X完成"移至归档

---

## 元数据

last_memory_sync: 2026-05-08 14:52
last_audit_date: 2026-04-19

---

## 📊 项目仪表盘（快速扫描）

### 🔄 需人工干预（计入活跃项目数）
| ID | 项目 | 状态 | 最后更新 | 下一步摘要 |
|---|---|---|---|---|
| P2 | Cowork系统优化 | 🔄 迭代中 | 2026-05-10 | opus_CC Discord MCP修好(env.PATH)；access.json频道修正；两bot独立DM架构确认 |
| P10 | 个人文件库 | 🔄 活跃 | 2026-04-25 | MVP完成(简历3文件)，阶段2扩展分类 |
| P3 | Cannabis Budtender | ⏸️ 暂停 | 2026-05-07 | eval 100%完成，暂停中，下次继续：sativa效果测试+架构修复清单 |
| P8 | 求职 (career-ops) | ⏸️ 暂停 | 2026-05-07 | 策略确定（作品敲门），暂停中，下次继续：LinkedIn截图重写profile |
| P5 | Legal Library | ⏸️ 暂停（按需更新） | 2026-05-07 | v4.5完成，有新法规时入库，平时按需 |

### ⚙️ 自动运行（不计入活跃项目数）
| ID | 项目 | 状态 | 最后更新 | 备注 |
|---|---|---|---|---|
| P4 | 每日新闻日报 | ✅ cron运行中 | 2026-05-10 | 5/10补发成功；root权限/tmp/news_ai.txt问题已确认不影响当前脚本 |
| P6 | 机票监控 Agent | ✅ cron运行中 | 2026-05-07 | SerpAPI key自动轮换（KEY2耗尽→自动切KEY）；直飞数据恢复 |
| P7 | Mac mini价格监控 | ✅ cron运行中 | 2026-04-23 | HTML邮件（链接藏入<a>标签）；今日eBay $305触发提醒 |
| P9 | AI量化交易系统 TIDE | ✅ cron运行中 | 2026-05-09 | 6只open持仓；price_snapshot.py上线(6/5自动填30d价格)；CSW pending等5/21；系统75%闭环；下次：B/C规则(不急) |

---

## 活跃进度

### [P2] Cowork 系统优化
状态：持续迭代中
last_updated: 2026-05-12
停在：双bot memory 已 symlink 共享；Agent View 调研沉淀；Gmail API 仍未启动；MEMORY.md 废弃条目清理（下次收工自动触发）

本次完成（2026-05-12 中午，opus_CC bot）：
- **双 bot memory 共享改造**：opus_home memory 改 symlink 指向 cowork bot 活 memory；打破"4 层隔离"中的 memory 层独立原则；reference/dual_bot_setup_log.md 加章节六完整记录架构决策+实施命令+回滚方法+收工分工约定
- **feedback_honesty.md 加 2 条新规则**：① "伪数据吹捧规则"（编 top%/对照分布等编造统计违规）② "时间跨度推断规则"（说"X 年/X 月"前必查 git log，禁止从版本号脑补）—— 同日 2 次伪数据违规驱动
- **feedback_backlog_format.md 加 "暂不做必须二选一"规则**：暂不做决策必须明确归类为🟡缓做（移到等触发条件区块）或🔴砍掉（直接删除），禁止留在"下次对话做"区块当僵尸条目
- **收工 SKILL.md 步骤 1 加强制规则**：遇到"暂不做"决策必须当场追问主公归类，已同步备份到 cowork/skills/
- **BACKLOG.md 清理**：删除 Discord Webhook 配置僵尸条目（已决定暂不做 7 天未清理）
- **reference/agent_view_rules.md 新建**：完整 Agent View 调研笔记（是什么/核心能力/限制/对比 Sub-agent vs Agent Teams/对 cowork 不启用结论/调研记录），防止下次重复派 subagent 浪费配额
- **对主公能力的深度对话**：4 强项（抽象学习/系统思维/元认知/韧性）+ 4 短板（执行收敛/聚焦/对 AI 严格 vs 对自己宽松/回避真实世界反馈）—— 深度对话内容通过步骤 5 深度审核会提炼到 review_drafts.md
下一步（2026-05-12）：
- Gmail API 配置（主公 GCP 端 6 步，我代码端 5 个脚本）
- MEMORY.md 废弃条目清理（收工时自动扫）
- 验证 index_conversations.py 的 JSONL_DIR 是否真的能扫到两个 bot 的 .jsonl（疑似 bug：写死路径 `-root-cowork`）—— 不紧急但影响搜索完整性
- 评估"主动审主公"周一 cron 任务（解决他"逃避取舍"命门，对话中识别为高杠杆动作）—— 待主公决策

本次完成（2026-05-11 第三次）：
- **project_*.md 精简（4个）**：daily_news_digest删WSL旧cron配置/mac_mini删迁移任务/personal_library删路径+阶段细节/career_ops删并行行动；5个确认无需改动
- **BACKLOG.md 清理**：删除已完成的 project_*.md 整理条目
- **MEMORY.md 分层研究**：Opus确认方案A ROI低不做，改向方案C（收工时扫废弃条目）
- **收工SKILL.md 加F项**：MEMORY.md废弃检查，有发现写草稿待主公确认，无发现静默跳过
下一步：
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
- MEMORY.md废弃条目清理（下次收工时自动触发）
本次完成（2026-05-11 夜）：
- **整理记忆 auto_pending 17条**：新建 reference_dual_bot / reference_p11_discord / feedback_env_check；更新 project_p9_trading / feedback_p9_ops / reference_cowork_location；knowledge_base.md 新增系统维护/Discord plugin/VPS限制/Gmail选型等条目；MEMORY.md 更新时间戳
- **ops_log.md 统一日志系统**：新建 /home/cowork/cowork/ops_log.md，所有 cron 脚本 + Skill 均写入
- **SMTP→Brevo修复**：run_py.sh / run_scanner.sh / run_flight.sh / run_mac_monitor.sh trap全部改为Brevo HTTP API；ops_alert.py新建
- **P9 crontab时间修正**：scanner_tracker→16:30, price_tracker→16:45, thesis_monitor→16:30, run_scanner→17:00, quarterly_review→18:30（错开DB冲突）
- **friction_log清理**：归档3组已修复条目，活跃条目14→11
- **INSIGHTS.md清空**：4条全处理（3迁knowledge_base，1删除）
下一步：
- BACKLOG.md 加项目标签（锦上添花，不急）
- MEMORY.md 分层（高频/低频，专门安排）
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
路径：VPS `/home/cowork/cowork/` | WSL挂载 `~/vps-cowork/`

本次完成（2026-05-11 下午第二次）：
- **MEMORY.md 进一步精简**：74行→69行，8.1KB→7.5KB；删4条冗余/废弃条目（legal_library裸文本/routines_rules裸路径/trading_agents废弃/gstack低频）；更新cowork路径(WSL→VPS)
- **Token 优化决策**：CLAUDE.md精简不做（收益小+执行确认区压缩净负向，Opus子agent独立验证同意）
- **Token 消耗分析**：Opus sub-agent贵（~26K tokens），非必要少派；Prompt Cache工作正常；Context window 200K，当前43.5%
- **MEMORY.md分层方向**：高频/低频分文件，ROI最高，待下次专门做
下一步：
- MEMORY.md 分层（高频/低频，下次专门做）
- CLAUDE.md 进一步精简（另找时间）
- 养成任务前 /compact 习惯
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
本次完成（2026-05-11）：
- **discord_approve.py加入"收工"触发词**：收工指令本身即全程授权，不再需要中途确认
- **review_drafts.md草稿处理完毕**：2条INSIGHTS写入+1条friction补记+ARCHITECTURE.md 4处Edit确认已处理
- **P4 May 10失败根因定位**：旧版脚本写/tmp/news_ai.txt vs root权限文件；当前版本已修复，今天13:00 EDT正常运行
- **P9时间确认**：今天周一，三件套+scanner_tracker+price_tracker在16:00 EDT运行
本次完成（2026-05-10 收工）：
- **ARCHITECTURE.md + playbooks Codex引用同步**：Codex执行层→子Agent协作层（路由规则4条+2判据）
- **review_drafts.md 草稿清除**：已处理的Codex引用检查项删除
本次完成（2026-05-10 第七次）：
- **CLAUDE.md 规则精简**：156→151行；删后台进程规则/合并摩擦记录/压缩Codex指令/删重复脚本标准section；长对话阈值30→40轮
- **Codex→子Agent协作**：全文替换Codex引用；路由规则4条精确版+两判据（验收能写死+无需中途对话）；Explore子agent测试通过（规则②验证）
- **Sonnet读→Opus析流水线**：测试通过；适用"大文件+需深度推理"非常见场景
- **review_drafts.md**：写入收工检查项（验证ARCHITECTURE.md/playbooks Codex引用是否已在收工时更新）
下一步：
- ARCHITECTURE.md 4处Edit（草稿主公已审，待执行）
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
路径：VPS `/home/cowork/cowork/` | WSL挂载 `~/vps-cowork/`

本次完成（2026-05-10 第六次）：
- **双bot配置参考日志**：reference/dual_bot_setup_log.md，含架构/8个踩坑/完整配置/操作速查
- **深度收工系统升级**：收工Skill→6步（路径修复+深度审核Step5+索引Step6）；草稿区reference/review_drafts.md；tracking文件reference/deep_reviewed_sessions.json
- **保存进度Skill新建**：~/.claude/skills/保存进度/SKILL.md，轻量3步，日常多次用
- **CLAUDE.md更新**：[ref-worthy]标记规则+review_drafts启动检查+Skill路由
- **opus_home Skills软链接**：opus_CC现可使用所有Skill
- **SKILLS_INDEX.md更新**：保存进度/收工条目对齐
下一步：
- ARCHITECTURE.md 4处Edit（草稿主公已审，待执行）
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
- 今晚收工验证深度审核全流程
路径：VPS `/home/cowork/cowork/` | WSL挂载 `~/vps-cowork/`

本次完成（2026-05-10 第四次）：
- **双 bot 独立重启互不干扰**：CLAUDE.md 重启规则按 $HOME 动态识别 tmux server，cowork bot 杀默认 socket / opus_CC 杀 -L opus_socket，互不误伤
- **独立 tmux server 隔离**：主公升级 claude_opus_runner.sh 用 `tmux -L opus_socket`，修复同 socket 下 HOME 环境变量被串问题；HOME 真正独立（/home/cowork vs /home/cowork/opus_home）
- **opus_home 完整 Discord plugin 安装**：通过 tmux send-keys 模拟 /plugin install discord@claude-plugins-official + /reload-plugins；之前 opus_CC 蹭 cowork plugin cache，现在 opus_home 自己有完整 plugin 状态
- **opus_CC DM channel 建立**：用 opus_CC token 调 Discord API 主动创建 DM channel(1503165641379545228) + 发首条消息建立通道；主公预授权 allowFrom 跳过 pairing 流程
- **opus_home settings.json 同步 permissions 配置**：复制 cowork 的 allow/deny/defaultMode:bypassPermissions + skipDangerousModePermissionPrompt；opus_CC 不再每个工具调用弹权限确认
- **opus_CC systemd 服务装机完成**：cowork-opus.service 装到 /etc/systemd/system/，主公 WSL SSH 进 root@142.93.207.54 跑安装命令；enabled + active，VPS reboot 自动起；与 cowork-claude.service 完全独立
- **cowork bot 模型改 sonnet 4.6**：/home/cowork/.claude/settings.json:45 model: opus→sonnet（下次重启生效，opus_CC 保持 opus-4-7）
下一步：
- 测试双 bot 实际重启隔离（!重启 各自验证）
- ARCHITECTURE.md 4处Edit（草稿主公已审，待执行）
- Gmail API配置（主公GCP端6步，我代码端5个脚本）

本次完成（2026-05-10 第三次）：
- **长对话提醒阈值 40→30轮**：CLAUDE.md修改；Shell Hook无法检测context%，降低轮数阈值以更早触发提醒
- **GitHub VPS备份建立**：生成ed25519 SSH key(alias:cowork-vps)+新仓库cowork_system_VPS；首次push成功(159文件)；旧cowork_system保留为WSL归档；memory同步更新
- **Google Drive镜像同步**：rclone_backup.sh改写去掉--backup-dir，纯mirror sync；全量上传54.8MB/259文件；gcrypt密码Qaz8939152!（需保存）
- **opus_CC bot配置**：tmux session cowork_opus启动，HOME=/home/cowork，DISCORD_BOT_TOKEN=opus_CC token覆盖，/model claude-opus-4-7；scripts/claude_opus_runner.sh新建；Discord邀请待验证
- **P4补发5/10新闻**：root权限/tmp/news_ai.txt不影响当前脚本（路径$SCRIPTS/news_ai.tmp不同）；run_daily_news.sh补发成功
下一步：
- ARCHITECTURE.md 4处Edit（草稿主公已审，待执行）
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
- opus_CC bot：主公邀请至Discord服务器+验证DM是否正常
- 长期观察：discord_approve.py关键词是否误触发
路径：VPS `/home/cowork/cowork/` | WSL挂载 `~/vps-cowork/`

本次完成（2026-05-10 第二次）：
- **问题1：数据诚信规则改写**：CLAUDE.md 数据诚信扩展三条可操作规则（来源标注/推测标注/读完标注）
- **honesty_check.sh Stop Hook**：检测声称读完但实际部分读取，触发警告；修复pipe+heredoc stdin冲突bug
- **问题2：Discord授权机制升级（方案C）**：discord_approve.py检测关键词自动touch；git_commit_guard.sh拦截Claude自行touch；禁止自授权
- **reference/hooks_system.md 新建**：14项Hook完整文档（概览表+详细说明+授权流程图）
- **ARCHITECTURE.md Hook表格更新**：补充新增hook+加hooks_system.md指针
- **VPS_SYSTEM_SETUP.md 对比**：确认VPS系统完整，文档比VPS落后2个hook
下一步：
- ARCHITECTURE.md 4处Edit（草稿主公已审，待执行）
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
- 问题2需长期观察：discord_approve.py关键词是否误触发
路径：VPS `/home/cowork/cowork/` | WSL挂载 `~/vps-cowork/`

### [P10] 个人文件库
状态：活跃 - 阶段4完成，阶段5-8暂停
last_updated: 2026-04-25
停在：267个文件已索引（简历/lease/财务/证书/cannabis），阶段5药房计划待做
本次完成（2026-04-25）：
- 架构：personal.db 从 cowork.db 独立出去（cowork/personal/trading/market 各自独立）
- 索引13个文件（简历全文件夹含_旧版，budtender/AI/通用/求职信/面试准备自动分类）
- 验收：说"发我AI Agent简历"/"发我budtender简历"均成功 ✅
- 5阶段索引计划：简历✅→出租lease✅→个人财务→cannabis→证书
- **阶段2（出租lease）**：加PDF支持(pdfplumber)+lease分类，索引7个新文件；搜索修复（切词+权重分级）✅
- **阶段3（个人财务+证书）**：索引15个新文件（W2/淘宝购物清单/13张证书），finance/certificate分类 ✅
- **阶段4（cannabis）**：索引232个文件，18个跳过（扫描PDF无文字层/损坏），验收通过 ✅
- 总计：267个文件已索引（简历13+lease7+财务2+证书13+cannabis232）
下一步（阶段5-8，OCR已装好，可继续）：
- 阶段5：药房计划（14个）
- 阶段6：牙科（6个）
- 阶段7：老人公寓（4个）
- 阶段8：Hair Ave（2个）
- OCR已安装（tesseract + pytesseract + pdf2image）✅
gbrain升级后续：
- D（两步CoT收工摘要）：改收工Skill，收工时额外生成知识摘要存储+向量化；复利型，待排期
- B+C（知识图谱）：等session > 100条再做
路径：`C:\Users\zhi89\Desktop\cowork\personal\`
数据库：`cowork/personal/personal.db`

### [P3] Cannabis AI Budtender
状态：活跃 - Eval 100% + Streaming 修复 + 文档架构重构
last_updated: 2026-04-12
停在：eval 25/25 通过，streaming 真正逐 token，sativa 规则修复，文档双轨同步建立
本次完成（2026-04-12）：
- Langfuse 接入（US region keys，drop-in wrapper）
- 黄金数据集 eval 25 TC 全部通过（100%），修复3个失败项：
  - tc_G2：信息收集问 form 前必须有 lead-in（prompt ❌ 反例）
  - tc_B2：强度反馈 → max_thc 注入 + FastPath 同步修复
  - tc_C4：_BEGINNER_SIGNALS 加入"never smoked"；injection 强制同时要求 lower-THC framing + safety tip
- Streaming 真正 token-by-token：重写 _run_agent_loop_stream()，新增 _stream_final_response()；修复 has_tool_results AttributeError（ChatCompletionMessage 无 .get()）
- Prompt 修复：sativa/indica/hybrid 已知时直接问 form，不再问 experience（INFORMATION_GATHERING_PROMPT 新增 STRAIN TYPE RULE）
- 文档架构重构：项目内外双轨同步规则建立；项目 CLAUDE.md + agents.md 加入收工流程；playbook 按新模板重写
- 规则写入：bug/报错类先说方案再执行；WSL 禁止内联测试脚本
下一步：
1. 继续测试 sativa 问法改进效果（后端 --reload 已生效）
2. 架构修复清单（INSIGHTS整理/memory同步/friction复盘）
3. （可选）为其他项目 playbook 按新模板对齐
路径：`C:\Users\zhi89\Desktop\cannabis_AI_BUDTENDER\` | 前端：`frontend-next/preview.html` | 后端：`localhost:8000`

### [P4] 每日新闻日报
状态：本地 cron 正常运行，格式修复完成
last_updated: 2026-04-16
停在：GitHub Action 删除，发布时间标注功能上线（2026-03-31）
本次完成（2026-03-31）：
- 诊断格式错误根因：GitHub Actions 无 ANTHROPIC_API_KEY，走 fallback 只显示裸标题
- 删除 `.github/workflows/daily_news.yml`，push 到 GitHub
- `daily_news.py` 新增 `published` 字段抓取
- `run_daily_news.sh` prompt 加入发布时间要求，测试通过
下一步：
1. **迁移到 Routines（待排期）** — 方案已确定：
   - `newscripts/` 加入 GitHub（移出 .gitignore）
   - `run_daily_news.sh` 移除 `claude --print` 调用，改纯数据输出
   - Discord token 改读环境变量（同机票脚本模式）
   - `newscripts/.env` 新建存 DISCORD_BOT_TOKEN
   - Routine prompt 让 Claude 直接生成摘要 + 发送
   - 本地 cron 保留作 fallback，Routine 稳定后再关
2. 按需优化 RSS 新闻来源
路径：`C:\Users\zhi89\Desktop\cowork\newscripts\`

---

### [P6] 机票监控 Agent
状态：✅ cron 运行中
last_updated: 2026-04-16
停在：cron 正常运行，安全修复 + AI建议修复完成
本次完成（2026-04-13/14）：
- 需求讨论：8条路线（JFK/EWR→HKG/CAN/SZX超级经济转机 + JFK→HKG/CAN经济直飞）
- 技术方案：SerpAPI查价 + SQLite存历史 + claude --print分析 + Discord推送（和新闻日报同架构）
- 代码完成：flight_monitor.py + build_report.py + run_flight.sh
- Bug修复：舱位代码（2=超级经济，3=商务）+ 过滤>24小时绕路 + 链接改用SerpAPI真实URL
- 测试通过：全部8条路线查价成功，Discord日报含价格/时间/链接/AI建议
- 文档完成：README.md + context.md + ARCHITECTURE.md + playbook
下一步：
1. 观察运行稳定性（电脑每天开着，cron 足够可靠，无需迁移 Task Scheduler）
2. 运行一周后观察价格走势
路径：`C:\Users\zhi89\Desktop\cowork\flightscripts\`
SerpAPI Key：已改为环境变量读取（SERPAPI_KEY in .env）

---

### [P5] Legal Library v4.5
状态：活跃 - 持续更新中
last_updated: 2026-05-11
停在：2案入库完成（本地2个commit），待主公说push才推GitHub；知识库完整性评估完成
本次完成（2026-05-11 第二次）：
- VPS GitHub SSH 直连 legal_library 建立（克隆至 /home/cowork/legal_library/）
- **案例四入库（17_Legal_Cases.md）**：Riverhead 预占案——Cannabis Law §131 预占地方区划，Board 驳回市政府反对，批准 CAURD 续期；push 至 GitHub（commit 074bb29）
- **案例五入库（17_Legal_Cases.md）**：Upstate State 预占边界补充——Cannabis Law 未预占的地方法规（ADA/建筑/zoning）仍有效，州执照不豁免地方合规义务；本地 commit e016adc
- LEGAL_TIMELINE.md + INDEX.md 同步更新（两次 commit）
- 跳过：2026-28（AU续期批量）、2026-27（执照修改批量），无增量内容
- 知识库完整性评估：覆盖好，缺口有 Community Impact Plan/December Queue 最新/PT3 Branding/Gotham Buds
- 工作流确认记忆：VPS /home/cowork/legal_library/ 持久保留，主公说 push 才推
- 审核偏好记忆写入：详细讲内容 + 入库判断 + 12月批次线索扫描
下一步：
- 等主公发新材料继续入库
- 主公确认 push 时统一推 GitHub
- 补充 Community Impact Plan 要求（新发现缺口）
路径：VPS `/home/cowork/legal_library/` | GitHub: Tommyz123/legal_library
本次完成（2026-04-11）：
- 17号新增 Bazaar Royale 条件性驳回案（§72(5)街道层面主入口要求/Proximity Protection≠选址合规/对比Brooklyn High案/补救路径）
- 17号补入数据来源（CCB 2026-04-02会议录音转录文件，决议编号待官方文件确认）
- 20号补入：①祖父条款不延伸至快闪许可证 ②Microbusiness独立举办受限说明
- LEGAL_TIMELINE.md新增2026-04-11记录
- 全部 git commit + push 至 Tommyz123/legal_library
本次完成（2026-04-10）：
- 入库 Part 117 Cannabis Showcase Events（20号文件，快闪活动新法规）
- S9155新法同步至05/14/16号（学校入口测量/青少年设施无同街限制）
- RULE.md v4.5：规则层级声明/入库验收清单/联动映射/删除子流程/内容主从/日志分工
- UPDATE_PROTOCOL v4.5：删除流程统一、步骤7具体化、版本表补全
- 删除低价值文件（18/22号批量名单）；建立CCB决议入库标准
- GitHub备份建立：github.com/Tommyz123/legal_library（私有）
下一步：下次入库新法规时按验收清单操作；定期 git push 同步
路径：`C:\Users\zhi89\Desktop\legal_library\` | GitHub: Tommyz123/legal_library

---

### [P8] 求职 (career-ops)
状态：活跃 - 策略确定，执行中
last_updated: 2026-04-19
停在：策略重定向完成，等LinkedIn截图重写profile
本次完成（2026-04-19）：
- 策略讨论：确定"作品敲门"路线，不依赖投简历
- 核心策略：找1-2家认识的大麻零售商免费跑Cannabis Budtender 3个月，积累案例和testimonial
- 目标公司：EliseAI（垂直AI Agent）/ Dutchie / LeafLink（cannabis tech，主场优势）
- 并行行动：LinkedIn重写+X/LinkedIn发帖建presence+DataAnnotation接任务
- 补充策略：先把Budtender做扎实（给实体做项目），再用结果敲门
下一步：
1. LinkedIn profile重写（等主公发截图）
2. 找认识的大麻零售商谈试用合作
3. DataAnnotation.tech注册尝试接任务
路径：`C:\Users\zhi89\Desktop\job\career-ops\`

---


### [P9] AI量化交易系统（TIDE系统）
状态：✅ 系统稳定自动运行 + price_snapshot.py上线
last_updated: 2026-05-09
停在：6只open持仓(ORA/CPK/LZ/WTRG/VRRM/CSW)；fill_price全部已同步；CSW verdict=pending等5/21财报；price_snapshot.py每天21:00 UTC自动填30/60/90天价格(6/5起生效)；系统75%闭环
本次完成（2026-05-09 第二次）：
- **price_snapshot.py上线**：每天21:00 UTC自动检查30/60/90天节点→yfinance抓价→写outcome_tracking；crontab已配置；6/5起第一批填入
- **CSW outcome_tracking notes写入**：机构建仓叙事+催化剂5/21；verdict保持pending等财报
- **系统完整审核**：75%闭合，cron全正常，所有脚本存在，fill_price全同步
- **P9流程梳理**：全买等权纸账号；30/60/90天节点验证框架；无日线价格记录（明确决策）
- **P11 Discord bug分析**：plugin v0.0.4通知协议与Claude Code v2.1.137不匹配；降级方案：①修plugin ②discord.py bot（功能降级）；plugin是唯一完整方案
- **深度整理Agent设计**：收工轻量化+深夜VPS跑对话整理；写入BACKLOG等P11稳定后建
本次完成（2026-05-09）：
- **持仓数据对齐**：DB vs Alpaca持仓对比；6只候选股状态统一为open；补单5只(CPK×24/WTRG×80/LZ×480/VRRM×210/CSW×10各约$3K等权)
- **trades表写入order_id**：5只补单order_id写入，sync_fill_prices.py将自动同步entry_price
- **8-K噪音修复**：signal_collector.py新增`(SYMBOL)`过滤——只保留目标公司自己发的8-K
- **催化剂日期Discord告警**：signal_alert.py新增check_catalyst_dates()，催化剂当天/次日自动发Discord提醒
- **signal_alert.py Discord集成**：复用scanner_tracker.py的send_discord()模式
- **DB噪音清理**：删7条错误8-K信号(LSAK/CDCC/VAL/RXRX/NUVB/AHRT/KKR)
- **outcome_tracking 5只verdict**：VRRM=positive/CPK|LZ|WTRG=neutral/CNR=invalid；附研究notes
- **快速验证模式确认**：P9阶段原则写入auto_pending（纸账号/全买/等权/最大化数据点）
- **BACKLOG新增**：daily_briefing.py + TIDE 5断点人工决策体系

本次完成（2026-05-08 第五次）：
- **告警可靠性修复**：run_scanner.sh加`set -eo pipefail`；cognitive_scanner.py 3处关键失败路径加[ERROR]日志(claude CLI/JSON/transcript)；main()新增analyzed_count字段+pipeline全跪时sys.exit(1)触发ERR trap邮件
- **SEC EDGAR 10-Q抓取闭环**：transcript_fetcher.py新增fetch_sec_10q+lookup_cik+extract_10q_text+CLI `--10q`；CIK缓存7天TTL；skip_if_exists去重
- **catalyst_monitor自动同步10-Q**：sync_open_positions_10q()每工作日扫open持仓抓新10-Q；7只持仓全部入库trading/transcripts/(共1.27MB)
- **trading/outcomes/目录建立**：事后归因报告独立子目录
- **ORA outcome报告(10-Q全文5171行100%覆盖)**：纠正前次冒烟报告5处错误(GAAP EPS $0.72 not $1.30/储能营收已独立披露/无guidance在10-Q等)；挖出5个警示信号(Product +458%含TOPP2一次性$105M/GAAP净利仅+8.7%/经营现金流-10.7%/KPLC+ENEE逾期$42M/Platanares违约)+5个加分项；推荐持有不加仓等Q2验证
- **CNR ticker错位发现**：sanity check 7只持仓→6/7匹配；CNR实际Core Natural Resources(煤炭)非加拿大铁路(CNI)；27股$2,357纸账号暴露但事前thesis对煤炭股完全无效
- **诚信失败+元规则**：第一版ORA outcome报告头标"数据源：10-Q 全文"实际只读3.6%；主公定性"骗"；"禁用标签膨胀"规则待升级CLAUDE.md(已写auto_pending标记严重)；"你确定吗"语义元规则(让我反思找漏洞而非改立场)写入auto_pending
本次完成（2026-05-08 第三次）：
- **Finnhub接入**：替代FMP付费新闻端点（FMP免费层不含/news/stock）；transcript_fetcher+signal_collector改用FINNHUB_API_KEY
- **system_log.md**：signal_collector每次运行后自动追加运行摘要（symbols/news/8k/inserted/Finnhub状态）
- **DB每日自动备份**：backup_db()每天cron跑完后自动cp，保留30天，存trading/backups/
- **Prompt版本快照**：prompts/cognitive_scanner_v1.0_20260508.md（6维打分prompt+评分说明+已知偏差）
- **Finnhub失效Gmail告警**：news_count=0时自动发Gmail提醒检查API
- **ORA叙事封存**：prompts/ORA_thesis_sealed_20260508.md（地热→储能转型叙事+催化剂+失效条件+验证标准）
- **验证框架确认**（Opus参与）：IWM基准/≥55%胜率/+3%超额/25+样本/封存事前预测
本次完成（2026-05-08 第四次）：
- **IWM基准全链路统一**：weekly_review.py(SPY→IWM/yfinance替FMP)、close_position.py(平仓时抓IWM)、quarterly_review.py(标签改IWM)、scanner_picks(7只open股spy_entry从$733.83→$286.80)
- **Opus审核过滤**：7个问题→仅修基准矛盾（其余6条过度工程化，纸账号阶段不做）
- **信号质量评估**：Finnhub新闻约50%有用/50%噪音，LLM层可过滤，不影响验证数据
- **审核收敛决策**：连续两轮无P0/P1→停止审核，系统正式进入自动运行阶段
下一步：
1. **B/C流程规则讨论**（下次对话专门议，ORA约8月才需要平仓决策）
   - B: 持仓期间何时加仓/减仓/止损？
   - C: 什么条件触发平仓（thesis失效 / 时间到 / 价格目标）？
2. **CSW 5/21财报后**更新verdict+notes
3. signal_collector积累60-90天后建theme_discovery.py（约2026年8月）
4. 5-10只平仓后回来定正式验证框架（25样本前不做复杂归因）
路径：`C:\Users\zhi89\Desktop\cowork\trading\` | DB：`trading/trading.db`

**TIDE完整自动运行流程（全部纽约时间 EDT/EST）**：
- 每天**16:00**：signal_collector / signal_alert / catalyst_monitor（三件套同时，各自独立调API）
- 每周一**16:30**：scanner_tracker（持仓周报）
- 每周一**16:45**：price_tracker（补充历史价）
- 每周三**16:30**：thesis_monitor（thesis失效→Discord告警+写thesis_alerts）
- 每周日**16:00**：weekly_review（结果追踪周报→Gmail，含IWM对比）
- 每月第一周一**15:00**：screener（刷新候选股池）
- 每季度第一周一**17:00**：run_scanner（季度主题扫描建仓）
- 每季度第一周一**18:30**：quarterly_review（季度复盘报告，含Alpha vs IWM）
- 每天**20:30**（周一至周五）：price_guard（持仓价格守卫，跌幅>7%告警）
- 每天**21:00**：price_snapshot（30/60/90天节点价格记录）

---

## 归档

### [P11] Cowork VPS 迁移 / ✅ 完成 / 完成日期：2026-05-10
停在：全链路迁移完成
完成内容：VPS(142.93.207.54) cowork用户全面接管；Discord reply/Brevo发件/所有cron/Skills全部验证通过；WSL2 cron已关闭；smtplib→Brevo全清；tide_utils DISCORD_BOT_TOKEN fallback机制建立
路径：VPS=`142.93.207.54:/home/cowork/cowork/` | service: `systemctl status cowork-claude`

### [P11] AI漫剧短视频 / ⏸️ 归档 / 归档日期：2026-05-03
停在：第一集技术流程跑通（10镜头视频+字幕SRT），待剪映配音导出
归档原因：视频制作需大量学习成本，当前阶段不投入
路径：`C:\Users\zhi89\Desktop\短剧\`

### [P1] 大麻法律助手建设 / ✅ 完成待用 / 完成日期：2026-03-23
停在：RULE.md + INDEX.md 建立完成，测试通过
下一步：在 `Desktop/legal_library/` 开 Claude Code 直接提问；如需扩展则补 INDEX.md 条目
路径：`C:\Users\zhi89\Desktop\legal_library\`
