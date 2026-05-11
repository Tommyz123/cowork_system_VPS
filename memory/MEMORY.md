# Memory Index

> 最后更新：2026-05-11
> 维护规则：新增记忆文件后立即在此处添加条目；不用的记忆文件同步删除对应条目

## User
- [user_profile.md](user_profile.md) — Tom；远程控Claude；AI+大麻创业；V5框架；直说实话不讨好

## Feedback（行为规则）
- [feedback_honesty.md](feedback_honesty.md) — 不讨好不奉承，客观陈述优缺点，有问题直说
- [feedback_confirm_before_execute.md](feedback_confirm_before_execute.md) — 确认后执行；5步流程；新API先独立验证；"直接开始"可跳
- [feedback_logging.md](feedback_logging.md) — 大事记cowork_log.md；保存进度=CURRENT_SESSION+日志两步；收工是超集
- [feedback_discord_allowlist.md](feedback_discord_allowlist.md) — Discord保持pairing模式；勿改为allowlist（会报错"channel is not allowlisted"）
- [feedback_auto_context.md](feedback_auto_context.md) — 涉及文件操作时主动读context.md；纯聊天不读
- [feedback_memory_system.md](feedback_memory_system.md) — 按需读取+两层过滤；快速拒绝（想法→BACKLOG/推导→不写）；5问题判断<3个Yes不写
- [feedback_project_pause_policy.md](feedback_project_pause_policy.md) — 暂停项目留活跃列表，不建议降BACKLOG
- [feedback_backlog_format.md](feedback_backlog_format.md) — BACKLOG必须注明真实讨论日期+背景+决策原因
- [feedback_roi_assessment.md](feedback_roi_assessment.md) — 评估新Hook/自动化前先查friction_log频率，不反问主公
- [feedback_api_key_storage.md](feedback_api_key_storage.md) — API key禁止硬编码；存.env+环境变量读取；.env加.gitignore
- [feedback_skill_execution.md](feedback_skill_execution.md) — Skill须直读SKILL.md执行；SKILL.md模型无关可供Codex
- [feedback_third_party_docker.md](feedback_third_party_docker.md) — 第三方GitHub工具主动询问是否Docker隔离；方案在BACKLOG
- [feedback_codex_collaboration.md](feedback_codex_collaboration.md) — Codex执行我验收；复杂分析派Opus；CLAUDE.md只加违规出事的规则
- [feedback_timezone.md](feedback_timezone.md) — 时间用纽约时间（EDT/EST），不说UTC
- [feedback_claude_cli_vs_api.md](feedback_claude_cli_vs_api.md) — AI分析用claude --print（CLI订阅），不调Anthropic API
- [feedback_preview_before_execute.md](feedback_preview_before_execute.md) — HTML邮件/视觉输出先Discord预览确认再执行
- [feedback_yagni.md](feedback_yagni.md) — 按需做，不过度工程化；无真实场景不建抽象层
- [feedback_discord_ts_hook.md](feedback_discord_ts_hook.md) — Discord ts字段必须先json.loads()，不能直接搜原始stdin
- [feedback_hair_ave_save.md](feedback_hair_ave_save.md) — 收到Hair Ave文件立即存入资料/Hair Ave/2025-2026_周报/
- [feedback_direct_correction.md](feedback_direct_correction.md) — 主公有技术误解时第一句直接纠正，不顺着误解走
- [feedback_forward_thinking.md](feedback_forward_thinking.md) — 决策同时考虑当下和未来，不只看眼前
- [feedback_p9_ops.md](feedback_p9_ops.md) — P9触发TIDE用bash run_scanner.sh，不能直接python3 cognitive_scanner.py
- [feedback_delete_verify_first.md](feedback_delete_verify_first.md) — 删前验证目标就绪：B有才删A，否则先补B
- [feedback_write_triggers_scan.md](feedback_write_triggers_scan.md) — 更新playbook/memory时自动扫描相关文档是否过时
- [feedback_rule_vs_hook.md](feedback_rule_vs_hook.md) — 规则=期望，Hook=强制；关键行为违反超一次升级为Hook
- [feedback_claudemd_discipline.md](feedback_claudemd_discipline.md) — CLAUDE.md只加"违反出事"的规则；操作习惯内化不写

## Project（项目背景）
- [project_cannabis_advisor.md](project_cannabis_advisor.md) — 大麻AI顾问；Desktop/marketing/；market.db（SQLite）；暂停
- [project_ai_skill.md](project_ai_skill.md) — cc_skill V5框架；P2完成；Desktop/cc_skill/
- [project_daily_news_digest.md](project_daily_news_digest.md) — 每天13:00 EDT cron；run_daily_news.sh；5类新闻+链接+点评
- legal_library — 纽约大麻法律知识库；见 [reference_legal_library.md](reference_legal_library.md)；进度见CURRENT_SESSION [P5]
- [project_design_principles.md](project_design_principles.md) — 设计原则：模型无关，接口可替换
- [project_insights_system.md](project_insights_system.md) — INSIGHTS.md=临时缓冲；knowledge_base.md=永久参考
- [project_mac_mini.md](project_mac_mini.md) — Mac mini M4计划；Email已配好；买后协助迁移
- [project_cowork_roadmap.md](project_cowork_roadmap.md) — 多agent路线图+Codex方向；可灵活调整
- [project_career_ops.md](project_career_ops.md) — P8求职；作品路线；目标EliseAI/Dutchie/LeafLink；兼职优先
- [project_personal_library.md](project_personal_library.md) — P10文件库；267文件；personal.db；阶段5-8暂停等OCR

## Reference（位置索引）
- [reference_claude_md_rules.md](reference_claude_md_rules.md) — CLAUDE.md≤200行；超180删旧；拆分用@import/.claude/rules/
- [reference_cowork_location.md](reference_cowork_location.md) — Win: C:\Users\zhi89\Desktop\cowork\；WSL: /mnt/c/Users/zhi89/Desktop/cowork/；核心：CLAUDE.md/context.md/CURRENT_SESSION.md
- [reference_cowork_github.md](reference_cowork_github.md) — github.com/Tommyz123/cowork_system（私有）；收工commit；不追踪cowork_log.md
- [reference_cc_source.md](reference_cc_source.md) — 研究笔记：cowork/research/cc_source_insights.md；Stop Hook/记忆过滤落地
- [reference_legal_library.md](reference_legal_library.md) — legal_library路径+GitHub(Tommyz123/legal_library私有)+入库标准→RULE.md；收工push
- [feedback_legal_library_workflow.md](feedback_legal_library_workflow.md) — VPS保留/home/cowork/legal_library/；每次git pull不重新clone；主公说push才推
- [feedback_legal_library_review.md](feedback_legal_library_review.md) — 审核3步：①讲内容（条款/数字/案件）②入库判断③扫12月批次线索
- [reference_p3_cannabis_budtender.md](reference_p3_cannabis_budtender.md) — P3路径；Flickr API在api_keys.env；图片用Flickr/loremflickr不用Unsplash
- [reference_hair_ave.md](reference_hair_ave.md) — 理发店投资文件在资料/Hair Ave/；.numbers需导出CSV/Excel处理
- [reference_discord_permissions.md](reference_discord_permissions.md) — Allow/Deny弹窗在Discord手机可操；当前用/tmp/task_approved替代
- [reference_routines.md](reference_routines.md) — Routines：云端定时；Pro 5次/天；新闻待迁移(需Discord webhook)
- cowork/reference/routines_rules.md — Routines官方规则存档
- [reference_skill_rules.md](reference_skill_rules.md) — Skill创建规则；实体~/.claude/skills/；备份cowork/skills/
- [reference_semantic_search.md](reference_semantic_search.md) — VoyageAI语义搜索；scripts/.env；search_conversations.py hybrid
- [reference_api_keys.md](reference_api_keys.md) — 所有API key在config/api_keys.env
- [reference_trading_agents.md](reference_trading_agents.md) — TradingAgents框架在Desktop/trading/TradingAgents/；技术指标废弃
- [feedback_deprecation_cleanup.md](feedback_deprecation_cleanup.md) — 停用时弃用标记+扫描memory/playbook清遗留引用（自主执行）
- [project_p9_trading.md](project_p9_trading.md) — P9 TIDE；主题驱动埋伏；ORA持仓；纸账号$1M；积累完成；下次=ORA平仓
- [reference_token_quota.md](reference_token_quota.md) — Claude Code token配额：长对话消耗；重要任务开新对话
- [reference_competitor_scraper.md](reference_competitor_scraper.md) — 竞品爬虫；GF/SS用Playwright捕dutchie graphql；ZZ用HTTP直连；cowork/scraper/
- [reference_gstack.md](reference_gstack.md) — GStack（Garry Tan开源）：github.com/garrytan/gstack；Skill设计借鉴

## Auto Pending（待审区）
- [auto_pending.md](auto_pending.md) — 自动捕获待审记忆；有[条目时列出请主公审核
