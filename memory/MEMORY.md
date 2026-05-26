# Memory Index

> 最后更新：2026-05-19（更新 feedback_p9_no_ghost_data + feedback_p9_auto_execute：反模式根治版——cognitive_scanner 写 'submitted'/'auto_pending' + sync_fill_prices 升级 reconciler，防 ghost positions 同款 24h 复发）
> 维护规则：新增记忆文件后立即在此处添加条目；不用的记忆文件同步删除对应条目

## User
- [user_profile.md](user_profile.md) — Tom（zhi89，Discord: tommzzz.）；Windows + iPhone遥控Claude；AI+大麻零售双轨创业；自研V5框架（Planning/Skill/Memory/Execution/Evaluation）；偏好先讨论机制再动手，直说实话不讨好

## Feedback（行为规则）
- [feedback_honesty.md](feedback_honesty.md) — 不讨好不奉承，客观陈述优缺点，有问题直说，不因顾虑情绪而含糊
- [feedback_confirm_before_execute.md](feedback_confirm_before_execute.md) — 执行确认：WSL 必须独立 .py（其他 CLAUDE.md 已有）
- [feedback_logging.md](feedback_logging.md) — 日志纪律：大事记不记细节；收工 ⊃ 保存进度（其他 CLAUDE.md 已有）
- [feedback_discord_allowlist.md](feedback_discord_allowlist.md) — Discord保持pairing模式；allowlist模式会导致reply工具报错"channel is not allowlisted"，不要改
- [feedback_auto_context.md](feedback_auto_context.md) — 涉及文件操作时主动读context.md；纯聊天不需要读
- [feedback_memory_system.md](feedback_memory_system.md) — 按需读取+两层写入过滤；快速拒绝（想法→BACKLOG/进度→CURRENT_SESSION/可推导→不写）；5问题判断：持久/跨对话价值/改变行为/不可推导/够具体，<3个Yes不写
- [feedback_project_pause_policy.md](feedback_project_pause_policy.md) — 暂停项目保留在活跃列表，不主动建议降BACKLOG；主公原话"放下去可能就永远不做了"
- [feedback_roi_assessment.md](feedback_roi_assessment.md) — 评估新自动化/Hook前，先查friction_log+cowork_log评估违规频率，不反问主公
- [feedback_api_key_storage.md](feedback_api_key_storage.md) — API key禁止硬编码，必须存.env文件+环境变量读取，.env加入.gitignore
- [feedback_skill_execution.md](feedback_skill_execution.md) — disable-model-invocation Skill须直读SKILL.md执行；历史设计类问题两步查询（memory+搜索历史）；SKILL.md模型无关可供Codex使用
- [feedback_third_party_docker.md](feedback_third_party_docker.md) — 第三方GitHub项目/工具，主动询问是否Docker隔离运行；方案在BACKLOG
- [feedback_codex_collaboration.md](feedback_codex_collaboration.md) — 我+Codex分工：我策划验收，Codex执行；复杂分析派Opus subagent；CLAUDE.md只加"违反出事"的规则，操作习惯不写
- [feedback_claude_cli_vs_api.md](feedback_claude_cli_vs_api.md) — 脚本需AI分析时用claude CLI订阅（claude --print），不调Anthropic API，这是主公明确原则
- [feedback_preview_before_execute.md](feedback_preview_before_execute.md) — HTML邮件/视觉输出改动必须先生成样本发Discord预览，主公确认后再执行（2026-04-23明确要求）
- [feedback_yagni.md](feedback_yagni.md) — 按需而做不过度工程化；"要需要才做，不是为了工程而做"；没真实场景就不建抽象层
- [feedback_discord_ts_hook.md](feedback_discord_ts_hook.md) — Discord ts字段解析必须先json.loads()，直接搜原始stdin会因JSON转义失败
- [feedback_discord_approve_design.md](feedback_discord_approve_design.md) — discord_approve.py设计原则：Skill命令不进APPROVE_KEYWORDS；关键词必须边界regex防从句误触发
- [feedback_proposal_data_first.md](feedback_proposal_data_first.md) — 推系统优化方案前必须先grep friction_log验证痛点真实性，禁止凭直觉推方案
- [feedback_methodology.md](feedback_methodology.md) — 主公工作方法论：小步起步+监测+数据驱动升级+已研究方案留底；与YAGNI互补
- [feedback_token_economy.md](feedback_token_economy.md) — 系统优化必须算token经济账；真正省token优先级反直觉：开新对话 > 搜索升级 > 图谱 > LLM调用（净增）
- [feedback_hair_ave_save.md](feedback_hair_ave_save.md) — 收到Hair Ave文件立即存入 资料/Hair Ave/2025-2026_周报/，无需确认
- [feedback_direct_correction.md](feedback_direct_correction.md) — 主公对技术机制有误解时，第一句直接纠正，不顺着误解走讨论方案
- [feedback_forward_thinking.md](feedback_forward_thinking.md) — 做决策必须同时考虑当下和未来影响，不能只看眼前能否解决问题
- [feedback_p9_ops.md](feedback_p9_ops.md) — P9手动触发TIDE扫描必须用bash run_scanner.sh，不能直接python3 cognitive_scanner.py（失败告警邮件在.sh里）
- [feedback_delete_verify_first.md](feedback_delete_verify_first.md) — 删除/精简内容前先验证目标已就绪：先读接收方文件确认内容已在那里，B有才删A，B没有先补B再删A
- [feedback_write_triggers_scan.md](feedback_write_triggers_scan.md) — 写入即扫描：每次更新playbook/memory时，自动扫描同项目相关文档是否有过时内容需清理（通用规则，非P9专用）
- [feedback_rule_vs_hook.md](feedback_rule_vs_hook.md) — 规则描述期望，Hook强制执行；关键行为违反超过一次→评估升级为Hook
- [feedback_claudemd_discipline.md](feedback_claudemd_discipline.md) — CLAUDE.md只加"违反了会出事"的规则；操作习惯/判断标准内化不写文档（2026-05-08）
- [feedback_env_check.md](feedback_env_check.md) — 进入新环境先跑hostname/whoami/pwd/ifconfig.me确认，不能凭路径格式猜测
- [feedback_artifact_indexing.md](feedback_artifact_indexing.md) — 新建脚本/cron/文档/数据必须最后一步加索引(ARCHITECTURE/cron_jobs/MEMORY/INDEX等)；沉默建文件=任务未完成
- [feedback_tide_utils_load_env.md](feedback_tide_utils_load_env.md) — trading/scripts 读 env 必须 `from tide_utils import load_env`，不许本地复制写 load_env()（5/17 P9 提醒发送失败教训，6 脚本复发）
- [feedback_thesis_normalization.md](feedback_thesis_normalization.md) — P9 thesis 必须 hypothesis 语气（may/could/historically），不许 declarative 断言；未验证精确数字只能放监测信号；范围 > 单点（5/18 GPT 二次纠偏）
- [feedback_auto_rca.md](feedback_auto_rca.md) — 错误自动 RCA：三档分级 + 5 触发器 + 反糊弄；Skill: auto-rca
- [feedback_p9_no_ghost_data.md](feedback_p9_no_ghost_data.md) — P9 status 反映真实 broker；数据修复≠流程修复（铁律）；DB=thesis SoT/Alpaca=持仓 SoT
- [feedback_p9_auto_execute.md](feedback_p9_auto_execute.md) — P9 自动执行流程 + 4 层 sanity check + $3000/只；真钱前必须重评
- [feedback_p9_alt_data_sidecar.md](feedback_p9_alt_data_sidecar.md) — P9 alt-data sidecar（独立 P9 主线）；周日自动收集；4-8 周观察 / 1 年后才入评分
- [feedback_read_before_conclude.md](feedback_read_before_conclude.md) — 先读信息再结论：有信息源（文件/日志/脚本/配置）禁止跳读猜测（P11 调试教训）
- [feedback_pacing_and_plain_language.md](feedback_pacing_and_plain_language.md) — 默认逐条+大白话+无术语；主公"没理解"立即换比喻重讲（5/23+5/25 节奏违反 2 次 + 术语致"没理解"反复触发）
- [feedback_clarify_hard_requirements.md](feedback_clarify_hard_requirements.md) — "什么都行/都可以/看你"必须先追问"有没有不接受的"再讨论选项；用户说宽松词≠真的宽松，常是没想到先说底线

## Project（项目背景）
- [project_cannabis_retail.md](project_cannabis_retail.md) — ⭐ P12 大麻零售主线（2026年主线，2026-05-14 确立）；NY牌照申请中+AI赋能+SaaS化路径；八字辛卯大运对应；playbook: playbooks/cannabis_retail.md；P1/P3/P5 已并入作为子模块
- [project_cannabis_advisor.md](project_cannabis_advisor.md) — 纽约大麻AI顾问；目录Desktop/marketing/；数据库market.db（SQLite）；技术栈Python+SQLite+curl_cffi；当前暂停（2026-04-06）；【已并入 P12】
- [project_ai_skill.md](project_ai_skill.md) — cc_skill V5框架；P2 cowork.db+5个Skill化（2026-04-17完成）；P2方向：规则→Hook/Skill自动化；目录Desktop/cc_skill/
- [project_daily_news_digest.md](project_daily_news_digest.md) — 本地cron每天13:00 EDT；脚本cowork/newscripts/run_daily_news.sh；新闻5类（政治/股市/加密/AI/大麻NY）；每条要真实链接+AI点评
- legal_library — 纽约大麻法律知识库；详见 [reference_legal_library.md](reference_legal_library.md)；进度见CURRENT_SESSION.md [P5]
- [project_design_principles.md](project_design_principles.md) — Cowork系统设计原则：模型无关性，不绑定特定AI，接口层可替换（2026-04-16确定）
- [project_insights_system.md](project_insights_system.md) — INSIGHTS双轨：INSIGHTS.md=临时缓冲区，reference/knowledge_base.md=已审核永久参考库（2026-04-17确定）
- [project_mac_mini.md](project_mac_mini.md) — Mac mini M4服务器计划：SSH+Discord+Email方案，Email已配好(zhitao776@gmail.com)，买了后全程协助迁移
- [project_cowork_roadmap.md](project_cowork_roadmap.md) — Cowork多agent路线图+Codex审核3个发展方向；路线可灵活调整，我有更好判断时提出讨论
- [project_career_ops.md](project_career_ops.md) — P8求职：作品敲门路线+Cannabis Budtender实体试用+目标EliseAI/Dutchie/LeafLink；兼职/Contract优先
- [project_personal_library.md](project_personal_library.md) — P10个人文件库：267文件已索引(简历/lease/财务/证书/cannabis)，personal.db独立，阶段5-8暂停等OCR

## Reference（位置索引）
- [reference_claude_md_rules.md](reference_claude_md_rules.md) — Claude Code官方规则：CLAUDE.md目标≤200行；超180行优先删旧；拆分用@import或.claude/rules/
- [reference_cowork_location.md](reference_cowork_location.md) — Win/WSL路径+VPS路径(/home/cowork/cowork/)；service用户=cowork非root；核心文件: CLAUDE.md/context.md/CURRENT_SESSION.md/memory/
- [reference_cowork_github.md](reference_cowork_github.md) — github.com/Tommyz123/cowork_system（私有）；收工时commit核心系统文件；不追踪cowork_log.md和.log文件
- [reference_cc_source.md](reference_cc_source.md) — 研究笔记在cowork/research/cc_source_insights.md；Stop Hook可解日志漏记；记忆相关性过滤省token；已借鉴落地：last_memory_sync/180行预警/收工双写检查
- [reference_legal_library.md](reference_legal_library.md) — legal_library路径+GitHub(Tommyz123/legal_library私有)+入库标准指向RULE.md+收工时git push
- [feedback_legal_library_workflow.md](feedback_legal_library_workflow.md) — VPS本地保留/home/cowork/legal_library/，每次git pull不重新clone；主公说push才推GitHub
- [feedback_legal_library_review.md](feedback_legal_library_review.md) — 审核材料3步：①详细讲内容（具体条款/数字/案件）②入库判断③主动扫描12月批次线索（December Queue/队列进展/主公申请相关）
- [reference_p3_cannabis_budtender.md](reference_p3_cannabis_budtender.md) — P3路径+Flickr API(key在api_keys.env)+图片踩坑：Unsplash猜ID不稳定，用Flickr/loremflickr
- [reference_hair_ave.md](reference_hair_ave.md) — 理发店投资文件在资料/Hair Ave/；.numbers需导出CSV/Excel才能在WSL处理
- [reference_discord_permissions.md](reference_discord_permissions.md) — Claude Code Allow/Deny弹窗出现在Discord，手机可操作；当前用/tmp/task_approved token机制代替
- [reference_routines.md](reference_routines.md) — Routines(2026-04-14)：云端定时执行，Pro 5次/天；每日新闻待迁移(需Discord webhook)；机票监控暂留本地
- cowork/reference/routines_rules.md — Routines完整官方规则本地存档（2026-04-18）：触发类型/网络权限/Discord webhook方案/Pro(5次)vsMax(15次)/坑点
- [reference_skill_rules.md](reference_skill_rules.md) — Skill创建规则：skill-creator用于新能力，迁移型可手写；实体在~/.claude/skills/，备份在cowork/skills/
- [reference_semantic_search.md](reference_semantic_search.md) — VoyageAI语义搜索：API key在scripts/.env，embed_sessions/messages.py向量化，search_conversations.py hybrid模式
- [reference_api_keys.md](reference_api_keys.md) — 所有API key统一存config/api_keys.env；SerpAPI×2/Gmail/Discord/Voyage/OpenAI/Anthropic/Tavily/DeepL/DeepSeek/Alpaca/FMP(备用)/Finnhub(P9新闻主力,2026-05-08)
- [feedback_deprecation_cleanup.md](feedback_deprecation_cleanup.md) — 停用系统/模块时：弃用标记+全量扫描memory/playbook清理遗留引用checklist（自主执行，不等提醒）
- [project_p9_trading.md](project_p9_trading.md) — P9 TIDE系统：主题驱动季度埋伏/叙事先行/ORA持仓/纸账号$1M/IWM基准/积累阶段完成(2026-05-08)/下次人工决策=ORA平仓
- [reference_token_quota.md](reference_token_quota.md) — Claude Code每日token配额：长对话本身也消耗，非Codex专属；重要任务在新对话开始时执行
- [reference_competitor_scraper.md](reference_competitor_scraper.md) — 竞品爬虫：GF/SS用Playwright捕dutchie graphql；ZZ用HTTP直连WP proxy+固定retailerId；DB在cowork/scraper/
- [reference_dual_bot.md](reference_dual_bot.md) — 双bot架构：cowork+opus_CC频道ID/隔离4层(tmux/HOME/plugin/token)/DO VPS IP/systemd服务/远程装plugin方法
- [reference_p11_discord.md](reference_p11_discord.md) — VPS Discord接入：plugin v0.0.4已知bug+patch位置+降级方案(discord.py自建bot~100行)
- cowork/reference/cron_jobs.md — 所有 cron 任务唯一总索引（每日新闻/机票/Mac监控/P9系列/rclone备份/大麻诉讼追踪），加新 cron 必须在此注册
- cowork/reference/agent_view_rules.md — Claude Code Agent View 完整调研笔记（不启用，多窗口管理工具不适合远程遥控场景）
- legal_library/18_Organic_Blooms_v_CCB_Tracking.md — NY大麻 December queue 诉讼追踪（Index 904497-24，影响主公申请），每周一09:00 EDT 自动 Discord 提醒查 NYSCEF

## Auto Pending（待审区）
- [auto_pending.md](auto_pending.md) — 系统自动捕获的待审记忆缓冲区；有[开头条目时需列出请主公确认后写入正式memory/
