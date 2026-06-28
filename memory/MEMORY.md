# Memory Index

> 最后更新：2026-06-10（memory双目录合并统一：补3条孤儿索引、去重投资直给、三实例symlink指向本目录）
> 维护规则：新增记忆文件后立即在此处添加条目；不用的记忆文件同步删除对应条目

## User
- [user_profile.md](user_profile.md) — Tom（zhi89，Discord: tommzzz.）；Windows + iPhone遥控Claude；AI+大麻零售双轨创业；自研V5框架（Planning/Skill/Memory/Execution/Evaluation）；偏好先讨论机制再动手，直说实话不讨好
- [user_bazi.md](user_bazi.md) — 主公真实八字真盘（1990-11-29未时·福建长乐）：戊土日主·身强财旺·食神生财命；辛卯大运(2023-2032)；2026-06-03 用lunar_python修正旧"丁火身弱"错误

## Feedback（行为规则）
- [feedback_understand_before_act.md](feedback_understand_before_act.md) — ⭐习惯：做任何事/给任何建议前，先了解清楚背景和实际情况（查实际数据/代码/战略，别凭记忆直觉）；禁止"先抛听起来合理的答案再回头补功课"
- [feedback_direct_investment_advice.md](feedback_direct_investment_advice.md) — 投资/判断类问题直给推测+推荐，免责声明压到一句内；不展开边界列表（2026-06-06）
- [feedback_investment_thesis.md](feedback_investment_thesis.md) — ⭐投资真实意图=押时代级大趋势本身（英伟达/特斯拉/闪迪式链条受益股），不必精确押龙头；核心=容错率+趋势判断；选标的/评P9以此为锚（2026-06-10）
- [feedback_us_stock_only.md](feedback_us_stock_only.md) — ⭐只做美股，非美股（德股/港股/A股/OTC粉单ADR）一律排除；选标的前先过这道筛子；主公强调两次（2026-06-21）
- [feedback_discord_long_doc.md](feedback_discord_long_doc.md) — 给主公发长文档禁止只发md附件（手机Discord打不开）；默认分段贴Discord文字每段≤1900字符，路径只作存档（2026-06-10）
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
- [feedback_doc_single_source.md](feedback_doc_single_source.md) — ⭐文档纪律(治"更新追不上")：①会变的事实别写死只写"实时查XXX"②要写的判断改就改干净禁新旧并存(区别于轨迹只增不改)；报"问题/差异"前必读权威文档当前态（2026-06-24 P9审核连环误报后立）
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
- [feedback_p9_auto_execute.md](feedback_p9_auto_execute.md) — P9 自动执行流程 + 4 层 sanity check + $1000/只 + 季度上限 top25（2026-05-30 攒样本提速）；真钱前必须重评
- [feedback_p9_alt_data_sidecar.md](feedback_p9_alt_data_sidecar.md) — P9 alt-data sidecar（独立 P9 主线）；周日自动收集；4-8 周观察 / 1 年后才入评分
- [feedback_read_before_conclude.md](feedback_read_before_conclude.md) — 先读信息再结论：有信息源（文件/日志/脚本/配置）禁止跳读猜测（P11 调试教训）
- [feedback_pacing_and_plain_language.md](feedback_pacing_and_plain_language.md) — 默认逐条+大白话+术语分层（Claude Code 生态/业务领域术语直接用，底层技术术语需比喻）；"没理解"立即换比喻（2026-05-27 升级）
- [feedback_clarify_hard_requirements.md](feedback_clarify_hard_requirements.md) — "什么都行/都可以/看你"必须先追问"有没有不接受的"再讨论选项；用户说宽松词≠真的宽松，常是没想到先说底线
- [feedback_cleanup_temp_data.md](feedback_cleanup_temp_data.md) — 做完涉及数据/文件/一次性脚本的任务后，主动提醒主公判断删多余临时数据/中间文件/临时脚本（2026-06-06；2026-06-24补点名「临时脚本」也纳入；上次堆17个垃圾文件教训）
- [feedback_self_organize_artifacts.md](feedback_self_organize_artifacts.md) — 每完成一摊多文件产出，自动整合进专门文件夹+写README+context.md登记位置，不等提醒（2026-06-06；给未来Claude看懂上下文）
- [feedback_proactive_update_alert.md](feedback_proactive_update_alert.md) — 主动扫描+及时提醒：工作中扫描到任何需要更新的内容(文档/索引/记忆/简历)立即 Discord 提醒，不等主公问；write_triggers_scan/artifact_indexing/deprecation_cleanup 的总纲
- [feedback_immediate_vs_longterm_framing.md](feedback_immediate_vs_longterm_framing.md) — 推 3 选 1 / 优先级建议前必须先问"立即推动 vs 长期方向"；两种场景判断框架完全不同（立即→看难度+ROI；长期→看战略契合度，重不再是缺点）
- [feedback_p9_strategy_discipline.md](feedback_p9_strategy_discipline.md) — P9 优化提案先过"是否改了策略本身"关；攒样本只能框架内拓宽广度，不能改扫描频率（数据回来前不改策略）
- [feedback_tmux_cross_instance.md](feedback_tmux_cross_instance.md) — tmux send-keys 跨实例通讯必须用英文/ASCII；中文字符会被丢弃对方收不到（tmux 编码限制）
- [feedback_three_instance_purpose.md](feedback_three_instance_purpose.md) — 三实例(AA/BB/CC)是并行任务工具不是备份；不建议减少实例数量，维护成本是必要成本
- [feedback_delegation_task_spec.md](feedback_delegation_task_spec.md) — 主公委托下属工作流：先和我聊清需求→我写成清晰任务说明→发下属；我是"需求翻译层"，主公聊任务安排时主动提议帮写说明（2026-06-09）
- [feedback_three_stances.md](feedback_three_stances.md) — 三姿态切换(老师/参谋/对手)；我的惯性=遇判断题滑回老师姿态；识别信号=主公已有判断缺的不是知识→主动切参谋/对手（2026-06-09）
- [feedback_prediction_data_first.md](feedback_prediction_data_first.md) — 预测前必先夯实数据：事实100%核实+标来源确信度+补缺口，数据不准禁止开跑（主公定性"儿戏"，2026-06-08）
- [feedback_savework_continuous.md](feedback_savework_continuous.md) — 收工是连贯流程：一口气跑完6步，commit+push全自动，禁止中途反复要git授权（2026-06-07）
- [feedback_tracking_facts_only.md](feedback_tracking_facts_only.md) — ⭐通用:所有文件记录数据与主观判断必须分层隔离——数据区零主观,判断单独分区+标时点,禁混写污染数据(数据会变判断会跟着变,分层才能追溯对比);分层=每次写入前置自检,写入即分层不事后补不靠提醒（2026-06-13 Organic Blooms案立,2026-06-24 P9 E1案强化）
- [feedback_data_driven_no_hardcode.md](feedback_data_driven_no_hardcode.md) — ⭐通用:会随业务增删的对象集合(股票/客户/关键词/文件清单)禁硬编码,必须从数据源解析;规矩要落文档防重犯(2026-06-21 趋势档案自动写入案)
- [feedback_dossier_outmigration.md](feedback_dossier_outmigration.md) — ⭐通用:总览表条目一旦从"一句话"长成"需持续追进展+判断演进的活体对象"就外迁独立档案+总览留一句话指针(防总览表撑爆);独立档案=头部4要素+事实/判断分层(2026-06-24 P9 E1案立,Organic Blooms为范本)
- [feedback_instance_mapping.md](feedback_instance_mapping.md) — ⭐三实例**操作铁律**(动手前必查映射/禁凭目录名猜/token对调教训)；口诀opus=BB/opus2=CC；**完整映射表已移至reference_dual_bot单一权威源**，本文件只留"为什么+怎么做"（2026-06-25 去重）
- [feedback_docs_for_ai.md](feedback_docs_for_ai.md) — ⭐总纲:文档分两类(定时发出的给人看/留系统里的给AI看得懂);系统内文档第一读者=没上下文的未来AI,标准="新AI能否看懂整个结构与分工不混乱";脚本头部四段(是什么/为什么做/为什么这样设计/演进);artifact_indexing等是其分身（2026-06-23）

## Project（项目背景）
- [project_cannabis_retail.md](project_cannabis_retail.md) — ⭐ P12 大麻零售主线（2026年主线，2026-05-14 确立）；NY牌照申请中+AI赋能+SaaS化路径；八字辛卯大运对应；playbook: playbooks/cannabis_retail.md；P1/P3/P5 已并入作为子模块
- [project_cannabis_advisor.md](project_cannabis_advisor.md) — 🗄️已并入P12(AI增强层子模块)；纽约大麻AI顾问；保留独有细节market.db(SQLite)+curl_cffi技术栈；原项目暂停（2026-04-06）
- [project_ai_skill.md](project_ai_skill.md) — cc_skill V5框架；P2 cowork.db+5个Skill化（2026-04-17完成）；P2方向：规则→Hook/Skill自动化；目录Desktop/cc_skill/
- [project_daily_news_digest.md](project_daily_news_digest.md) — 本地cron每天13:00 EDT；脚本cowork/newscripts/run_daily_news.sh；新闻5类（政治/股市/加密/AI/大麻NY）；每条要真实链接+AI点评
- legal_library — 纽约大麻法律知识库；详见 [reference_legal_library.md](reference_legal_library.md)；进度见CURRENT_SESSION.md [P5]
- [project_design_principles.md](project_design_principles.md) — Cowork系统设计原则：模型无关性，不绑定特定AI，接口层可替换（2026-04-16确定）
- [project_insights_system.md](project_insights_system.md) — INSIGHTS双轨：INSIGHTS.md=临时缓冲区，reference/knowledge_base.md=已审核永久参考库（2026-04-17确定）
- [project_mac_mini.md](project_mac_mini.md) — Mac mini M4服务器计划：SSH+Discord+Email方案，Email已配好(zhitao776@gmail.com)，买了后全程协助迁移
- [project_cowork_roadmap.md](project_cowork_roadmap.md) — Cowork多agent路线图+Codex审核3个发展方向；路线可灵活调整，我有更好判断时提出讨论
- [project_sage_seeds_aiq.md](project_sage_seeds_aiq.md) — P8 Sage Seeds Alpine IQ数据能力边界：cmpID活动归因+漏斗可做/discID优惠码核销字段空查不了/code归因需老板建测试码实测（2026-06-07）
- [project_career_ops.md](project_career_ops.md) — P8求职：作品敲门路线+Cannabis Budtender实体试用+目标EliseAI/Dutchie/LeafLink；兼职/Contract优先；2026-05在职dispensary老板给Alpine IQ API key让做客户分析(=作品机会)
- [project_personal_library.md](project_personal_library.md) — P10个人文件库：267文件已索引(简历/lease/财务/证书/cannabis)，personal.db独立，阶段5-8暂停等OCR
- [project_pyramid_learning.md](project_pyramid_learning.md) — 《金字塔原理》精读：第1-2章学透毕业(L3达标)；含教学5规则+训练承诺(学透L3)+核心深练边角略过策略+全书深浅地图+4个易错点；下次开第3章(中等深度)；写材料时主动引用
- [project_p9_validation_philosophy.md](project_p9_validation_philosophy.md) — P9 验证哲学「先改进再认输」：三指数基准(IWM/SPY/QQQ)+Sharpe，跑输=找根因改进，认输门槛需多季度稳定跑输（2026-06-02 主公确立）
- [project_p9_narrative_tracker.md](project_p9_narrative_tracker.md) — P9 公司叙事追踪系统(建仓前研究跟踪,"新闻不是资产假设才是资产")；2026-06-27上线,VST试点等8/6财报第一次对答案；4表(narrative_*)+财报哨兵cron；"建仓即移交"边界防与持仓监控打架

## Reference（位置索引）
- [reference_claude_md_rules.md](reference_claude_md_rules.md) — Claude Code官方规则：CLAUDE.md目标≤200行；超180行优先删旧；拆分用@import或.claude/rules/
- [reference_cowork_location.md](reference_cowork_location.md) — Win/WSL路径+VPS路径(/home/cowork/cowork/)；service用户=cowork非root；核心文件: CLAUDE.md/context.md/CURRENT_SESSION.md/memory/
- [reference_cowork_github.md](reference_cowork_github.md) — github.com/Tommyz123/cowork_system（私有）；收工时commit核心系统文件；不追踪cowork_log.md和.log文件
- [reference_cc_source.md](reference_cc_source.md) — 研究笔记在cowork/research/cc_source_insights.md；Stop Hook可解日志漏记；记忆相关性过滤省token；已借鉴落地：last_memory_sync/180行预警/收工双写检查
- [reference_legal_library.md](reference_legal_library.md) — legal_library路径+GitHub(Tommyz123/legal_library私有)+入库标准指向RULE.md+收工时git push
- [feedback_legal_library_workflow.md](feedback_legal_library_workflow.md) — Legal Library 工作流：①入库(VPS本地/home/cowork/legal_library/,git pull不重clone,主公说push才推)②审核材料3步(详细讲内容/入库判断/扫12月批次线索)
- [reference_p3_cannabis_budtender.md](reference_p3_cannabis_budtender.md) — P3路径+Flickr API(key在api_keys.env)+图片踩坑：Unsplash猜ID不稳定，用Flickr/loremflickr
- [reference_hair_ave.md](reference_hair_ave.md) — 理发店投资文件在资料/Hair Ave/；.numbers需导出CSV/Excel才能在WSL处理
- [reference_discord_permissions.md](reference_discord_permissions.md) — Claude Code Allow/Deny弹窗出现在Discord，手机可操作；当前用/tmp/task_approved token机制代替
- [reference_routines.md](reference_routines.md) — Routines(2026-04-14)：云端定时执行，Pro 5次/天；每日新闻待迁移(需Discord webhook)；机票监控暂留本地
- cowork/reference/routines_rules.md — Routines完整官方规则本地存档（2026-04-18）：触发类型/网络权限/Discord webhook方案/Pro(5次)vsMax(15次)/坑点
- [reference_skill_rules.md](reference_skill_rules.md) — Skill创建规则：skill-creator用于新能力，迁移型可手写；实体在~/.claude/skills/，备份在cowork/skills/
- [reference_semantic_search.md](reference_semantic_search.md) — VoyageAI语义搜索：API key在scripts/.env，embed_sessions/messages.py向量化，search_conversations.py hybrid模式
- [reference_api_keys.md](reference_api_keys.md) — 所有API key统一存config/api_keys.env；SerpAPI×2/Gmail/Discord/Voyage/OpenAI/Anthropic/Tavily/DeepL/DeepSeek/Alpaca/FMP(备用)/Finnhub(P9新闻主力,2026-05-08)
- [feedback_deprecation_cleanup.md](feedback_deprecation_cleanup.md) — 停用系统/模块时：弃用标记+全量扫描memory/playbook清理遗留引用checklist（自主执行，不等提醒）
- [project_p9_trading.md](project_p9_trading.md) — P9 TIDE系统：主题驱动季度埋伏/叙事先行/ORA持仓/纸账号swing(余额实时查Alpaca不写死)/IWM基准/积累阶段完成(2026-05-08)/下次人工决策=ORA平仓
- [reference_token_quota.md](reference_token_quota.md) — Claude Code每日token配额：长对话本身也消耗，非Codex专属；重要任务在新对话开始时执行
- [reference_competitor_scraper.md](reference_competitor_scraper.md) — 竞品爬虫：GF/SS用Playwright捕dutchie graphql；ZZ用HTTP直连WP proxy+固定retailerId；DB在cowork/scraper/
- [reference_dual_bot.md](reference_dual_bot.md) — ⭐**三实例唯一权威全表**(AA/BB/CC全字段:模型/HOME/socket/session/频道/token/appid/service/版本)+架构：隔离4层(tmux/HOME/plugin/token)/memory例外=三实例symlink共享cowork/memory(2026-06-10统一,含新实例上线checklist)/DO VPS IP/3 systemd服务全自启/远程装plugin方法/升级指南。查实例任何字段认这张
- [reference_p11_discord.md](reference_p11_discord.md) — VPS Discord接入：plugin v0.0.4已知bug+patch位置+降级方案(discord.py自建bot~100行)
- cowork/reference/cron_jobs.md — 所有 cron + systemd 自启任务唯一总索引（每日新闻/机票/Mac监控/P9系列/rclone备份/大麻诉讼追踪 + 3 个 Claude 实例 systemd），加新 cron / service 必须在此注册
- cowork/reference/agent_view_rules.md — Claude Code Agent View 完整调研笔记（不启用，多窗口管理工具不适合远程遥控场景）
- legal_library/18_Organic_Blooms_v_CCB_Tracking.md — NY大麻 December queue 诉讼追踪（Index 904497-24，影响主公申请），每周一09:00 EDT 自动 Discord 提醒查 NYSCEF
- cowork/reference/methodology_index.md — ⭐方法论统一总索引：一页看全所有按需调用方法论(自有skill_archives 8个 + 官方official_plugins 16个 + external预留)；主公做相关工作时查触发点主动提醒；不含已配置的自动加载skill
- cowork/reference/official_plugins/INDEX.md — Anthropic官方 knowledge-work-plugins 方法论参考库(16插件/140skill)；纯参考未配置；属上面总索引的official区块

## Auto Pending（待审区）
- [auto_pending.md](auto_pending.md) — 系统自动捕获的待审记忆缓冲区；有[开头条目时需列出请主公确认后写入正式memory/
