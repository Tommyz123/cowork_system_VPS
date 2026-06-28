# 待确认草稿区

> 每次对话开始时检查，有内容则第一件事列出请主公决策

---

（空 — 2026-06-23 已清空：6-10 至 6-22 共 12 批草稿全部经主公逐批审核处理完毕。处理摘要见 cowork_log.md 同日"review_drafts批N"行。）

---

## [草稿] 2026-06-23 深度审核（3 sessions：96b24987 / abd8d2eb / f95f94af）

### 🤖 本次自动写入摘要（4 分，已直接写入正式文件）
- **[评分:4]** knowledge_base「permissions.deny 禁止特定工具触发」→ 已写入 reference/knowledge_base.md「MCP 与系统设计」区块

### 🗑️ 本次自动丢弃摘要（1 分，未保留）
- 共 3 条 1 分候选被 AI 自判低价值丢弃（f95f94af=已全提交4cc349f/96b24987=7条极简/abd8d2eb产出已入5a86386）

---

## [草稿] 2026-06-23 深度审核·第二批（3 sessions：41968649 / dab72bb5 / 9893fc2f）

### 🤖 本次自动写入摘要（4-5 分，已直接写入正式文件）
- **[评分:5]** feedback「文档为AI而写总纲」→ 已写入 memory/feedback_docs_for_ai.md（含读者二分判据+系统内文档标准+脚本四段写法）
- **[评分:5]** FERC信号漏确认闭环修复 → 已写入 trading/notes/趋势追踪档案.md(CEG 6/23更正行+修订区) + 趋势观察池.md(E1两阶段) + scripts/ferc_watch.py(逻辑说明)
- **[评分:4]** 信号作战表(给AI看的信号→动作SOP) → 已新建 trading/notes/信号作战表.md + 登记INDEX.md/cron_jobs.md
- **[评分:4]** friction「收工git授权失灵+token被hook清」→ 已写入 friction_log.md（根因待查留两问）

### 🗑️ 本次自动丢弃摘要（1 分，未保留）
- 2 条 1 分候选丢弃：41968649=周报HTML渲染修复(已历史完成入提交)/dab72bb5=三实例runner核验(已完成工作的核验,2小尾巴已入be4aaf5)

### 📌 留主公决策（非草稿，已记 CURRENT_SESSION）
- P9 两待决策：① NAND/光模块是否加轻量哨兵 ② 通知是否改三级分级（🔴出手即时/🟡事件当天/⚪周检心跳）

## [草稿] 2026-06-24 深度审核

### Friction 建议补记（0条）
（本场 2 条假问题 friction 已实时记入 friction_log，无需补）

### Playbook 建议更新（0处）
（playbooks/p9_trading.md 本场已直接更新账号实时查口径）

### CLAUDE.md 规则建议（1处）
- **[评分:3]** CLAUDE.md 白名单补 `friction_log_archive.md`：本场(及 6/24 00:38 AA 场)发现收工归档 friction 时，改 `friction_log.md`(白名单内)放行但写 `friction_log_archive.md`(白名单写的是目录 `archive/`,不含根目录的 `friction_log_archive.md`)被任务守卫拦。两者同性质(收工高频归档操作),建议白名单加 `friction_log_archive.md` 给同等权限。需主公确认是否改 CLAUDE.md。

---

## [草稿] 2026-06-25 深度审核（本场=重启+收工，复核昨日大会话 bcfbf1ac）

### ⚠️ 上一条草稿状态复核（重要）
- 上面「CLAUDE.md 白名单补 `friction_log_archive.md`」**hook 层已自动解决**：6/24 20:53 的 D 修复已把 `system_file_guard.sh:27` 白名单从 `friction_log.md` 改成子串 `friction_log`，子串匹配同时覆盖 `friction_log.md` + `friction_log_archive.md`，task 守卫不再拦归档文件。
- **但残留一处文档↔实现不一致**：`~/.claude/CLAUDE.md:29` 文字白名单仍写 `friction_log.md`（人读文档），与 hook 实际放行的 `friction_log`（含 archive）不符。
  - **[评分:3]** 建议：把 `~/.claude/CLAUDE.md:29` 白名单文字 `friction_log.md` 改成 `friction_log*`（或注明"含 archive"），让人读文档与 hook 行为一致（符合 feedback_doc_single_source）。需主公确认。这是**唯一仍需处理项**，原"补白名单"诉求已由 D 技术解决。

### 其他类别
- INSIGHTS/Friction/Playbook/文档对齐/MEMORY清理：本场无新增。昨日大会话的洞察（先读代码再诊断、自我更正、停手防数据丢失）均为已有 memory 规则的再次印证，无新规则可写。F 检查 MEMORY.md 无废弃孤儿（🗄️ 两条为有意保留）。

---

### 🤖 本次自动写入摘要（4-5 分，已直接写入正式文件）
- **[评分:5]** Feedback 文档纪律 `feedback_doc_single_source` → 已写入 memory/（会变的别写死+状态类就地覆盖禁新旧并存；治"文档更新追不上"）
- **[评分:4]** Feedback `feedback_cleanup_temp_data` 扩展"临时脚本"纳入 → 已写入 memory/（主公 6/24 点名）

---

## [草稿] 2026-06-25 深度审核（本场=FERC新闻引出文档纪律连锁，session 51f703d0）

### ⚠️ 上一条草稿状态复核
- 上面「`~/.claude/CLAUDE.md:29` 白名单文字 `friction_log.md`→`friction_log*` 对齐」**仍待主公确认**，本场未动。这是唯一历史遗留待决项。

### Playbook 建议更新（1处）
- **[评分:3]** `playbooks/p9_trading.md`：建议补一句哨兵命中处理SOP——FERC等事件哨兵命中后按 🆕[新事]/🔁[复述] 分类记入对应事件独立档案(命中次数≠真事件数)，攒"真新事数"判断是否值得上自动记录。本场新立的实操习惯，值得在playbook留指针。需主公确认。

### 其他类别
- INSIGHTS/Friction/文档对齐/MEMORY清理：本场无新增送审项。核心洞察(命中频率≠真事件数/活体对象外迁)已直接写入E1档案+memory(见下方自动写入摘要)。2条friction(文档纪律未自检+相对路径事故)已实时闭环记入friction_log。F检查MEMORY.md无废弃孤儿。

---

### 🤖 本次自动写入摘要（4-5 分，已直接写入正式文件）
- **[评分:5]** Feedback `feedback_dossier_outmigration`(新建) → memory/（总览表条目长成活体对象就外迁独立档案+留指针;主公明确"以后会越来越多"+Organic Blooms范本，跨项目通用+完整规则）
- **[评分:4]** Feedback `feedback_tracking_facts_only`强化"写入即分层前置自检" → memory/（主公明确"每次写入都自动分层好"）
- **[评分:4]** Feedback `feedback_docs_for_ai`升级验收标准"看懂→能独立接手"+头部4要素 → memory/（主公连环追问"AI看得懂吗"逼出）

---

## [草稿] 2026-06-25 深度审核（晚场=sonnet任务半收尾+失忆事故，sessions 4392e122+7f6ac272）

### 审核范围说明
今天晚场两个未审 session 实为**同一连续任务的两段**（context 压缩切分）：4392e122=BB 做 sonnet 任务上半场（含 CC plugin 2.1.191 排查）+ 7f6ac272=本会话下半场（断片后误判→复盘）。核心产出已全部落地，仅 1 条执行教训送审。

### Friction/规则强化 建议（1条）
- **[评分:3]** 失忆事故根因=**违反既有"超40轮该开新对话"规则**（CLAUDE.md 已有，本次拖到740轮才触发 context 压缩→摘要丢"sonnet任务是BB自做"上下文→对主公"做好了吗"断片+把自己写的报告误判成"AA发的"连环错）。属执行问题非缺规则。**送审决策**：要不要把"40轮软提醒"升级为**硬 hook**（轮次超阈值时 UserPromptSubmit 强插显著警告/或自动建议收工）？依据 feedback_rule_vs_hook「关键行为违反超过一次→评估升级 Hook」。需主公定。[src:7f6ac272]

### 其他类别
- CC plugin 2.1.191 升级踩坑（4392e122 主线之一）→ 已闭环：friction_log 17:42+18:10 两条 + reference_dual_bot.md 升级指南(138行起)，无新增。
- sonnet 任务 → 待办已记 CURRENT_SESSION P2，无送审项。
- INSIGHTS/Playbook/文档对齐/MEMORY清理：本场无新增。

---

## [草稿] 2026-06-27 深度审核（授权债修复 + BB plugin重启失起故障）

### 审核范围说明
今天 8 个 session：主线=授权债死循环修复(1396886a,本会话BB亲历)+DO root救援(0ec674fc,昨晚sonnet改名操作,已记P2)+**BB Discord plugin重启后没起来**(02db1c46+ee866ce0两段同事)+改密码引导(40f0d303)+hi测试/resume若干(无价值)。

### Friction/规则强化 建议（1条）
- **[评分:3]** **BB Discord plugin VPS重启后启动失败**(02db1c46+ee866ce0)：6/26 20:28 VPS被DO平台层硬重启(无shutdown记录,13天周期=6/13也一次,疑DO维护/宿主迁移),重启后AA/CC的plugin正常拉起但**BB(opus_home)的Discord plugin子进程没起来**→主公Discord发消息BB静默→SSH进来排查。证据链查到:plugin cache有`.in_use`锁(时间戳=重启时刻),且kill-server重启BB后plugin仍不起,最终暴露**进程身份混乱**(SSH对话的"BB"实为老BB派生的游离`daemon run --origin transient`后台daemon PID5727,非systemd主线)。**[AA补充结局]** 最终通过`tmux -L opus_socket kill-server`+watchdog 2s拉起全新session，BB专属bun discord进程(PID10168 HOME=opus_home)成功起来，三实例Discord全恢复(AA 20:51日志实锤)。**送审决策**:①结局已闭环(AA补充确认)②是否值得记一条knowledge"BB突然Discord静默→第一查plugin cache .in_use锁+确认是否游离daemon→kill-server+watchdog重建"③13天周期DO重启是否要加监控/重启后plugin自检。[src:02db1c46][src:ee866ce0]

### 其他类别
- DO root救援(0ec674fc)→已记P2(AA改名sonnet),无新增。
- 改密码引导(40f0d303)→主公曾贴临时密码到Discord,我已当场安全提醒,临时密码用完即废,无需记。
- INSIGHTS/操作记录/Playbook/文档对齐/MEMORY清理:本场无新增。

---

### 🤖 本次自动写入摘要（4-5 分，已直接写入正式文件）
- 本场无 4-5 分自动写入。

### 🗑️ 本次自动丢弃摘要（1 分，未保留）
- 共 3 条 1 分候选丢弃（hi连接测试61d762ed/90c38713 + resume卡background agent 31b3b1d8，纯连接/无内容）。

---

## [草稿] 2026-06-27 AA深度审核（三实例分层核查 + CC token恢复）

### 审核范围
今天AA未审session：d983d518（本收工会话，三实例分层核查+CC token恢复）、19809fbd（BB/CC故障状态快速确认，6条）。

### 其他类别
- d983d518/19809fbd：无新价值（日常核查+已记日志），1分丢弃。
- BB 6-27草稿里的BB plugin故障「结局未明」：AA已补充闭环事实（见上方补注）。
- INSIGHTS/Friction/Playbook/文档对齐/MEMORY清理：本场无新增。

### 🤖 本次自动写入摘要（4-5 分）
- 本场无 4-5 分自动写入。

### 🗑️ 本次自动丢弃摘要（1 分）
- 共 2 条 1 分候选丢弃：d983d518（日常三实例分层核查，无新洞察）、19809fbd（BB/CC故障状态确认，已记日志）。

---

## [草稿] 2026-06-27 CC深度审核（P9「过期单也对答案」+ 运维事故）

### 审核范围
CC今天未审session：fba4111f(本场,P9过期单闭环主线)、02db1c46/1396886a(BB身份+Discord断连,已记日志)、0ec674fc(DO Console启动指引,运维)、40f0d303(密码重置+泄露提醒,运维)、61d762ed(CC Not logged in,无内容)。

### INSIGHTS 建议写入（2条）
1. **[评分:4]** OPG市价单"开盘集合竞价未撮合即过期"机制 → 盘后下的 market+opg 单只在次日开盘那一瞬参与集合竞价,没撮上立刻 expired(filled_qty=0,实测10笔全在开盘0-5分钟内废),**不顺延盘中、与价格无关**(市价单不挑价);冷门中小盘股开盘流动性不足易过期;同票不同天结果不同(GNTX 5/18成交5/26过期)。排查口诀=拉 Alpaca order 看 submitted_at/expired_at 时间线。[src:fba4111f] [ref-worthy]
2. **[评分:4]** 通用方法论"没买到/没成交也能对答案验证选股眼光" → 过期单虽没实盘盈亏,但留了signal_entry_price+score=可纸面跟踪后续涨跌验证"选得准不准"(买没买到≠选得对不对);落地=独立tracker脚本仿post_exit_tracker,数据层(客观涨跌)与审计层(确定性规则打对错)分字段隔离,不碰判断verdict。可迁移到任何"有信号但未执行"的样本回填。[src:fba4111f]

### Friction 建议补记（1条）
- **[评分:3]** scanner_picks 全表25笔verdict默认填'tentative' → 判断字段被旧流程批量填默认值=轻微分层瑕疵(违feedback_tracking_facts_only"判断该空就空");非本次引入;建议清理为NULL让"未判断"如实留空。CC做unfilled_tracker时发现并主动避开(没复用verdict,另建audit_*字段)。[src:fba4111f]

### Playbook 建议更新（1处）
- **[评分:3]** playbooks/p9或project_p9_trading：补登 unfilled_tracker.py(过期单纸面跟踪,周一17:05 cron)+「过期单也对答案」B-轻量版闭环+三层数据地基(数据/审计层),接主题累积研究loop的阶段0数据基础。[src:fba4111f]

### 🤖 本次自动写入摘要（4-5 分）
- 本场无 4-5 分自动写入（冷启动期保守,4分也送审）。

### 🗑️ 本次自动丢弃摘要（1 分）
- 共3条1分丢弃：02db1c46/1396886a(BB运维已记日志)、0ec674fc(DO指引一次性)、61d762ed(掉登录无内容);40f0d303密码泄露提醒已是已知安全规则不重记。

## [草稿] 2026-06-28 深度审核

### INSIGHTS 建议写入（2条）
1. **[评分:3]** AI写库系统的"记录透明度"原则：透明对象应是「语义动作」(AI对材料做了筛选/判断/归因)而非「数据库动作」(每行insert)；分三级报备(动账本逐条/有判断的可拦/纯留痕汇总)。Codex核心警告=单人系统最大风险不是AI偷改数值,而是AI长期悄悄筛材料致用户误以为看全貌实为AI过滤叙事。[src:c84032e9]（已落地为P9叙事追踪方案的1·五节,此处考虑提炼成通用规则）
2. **[评分:3]** AI自动化的折中模式"出草稿+人把关"：当用户要"自动化"但又怕AI乱判断时,解法=让AI自动出草稿/建议(标"建议")自动推送,但真正落库/动账本仍需人确认。既零负担又不丢判断质量,区别于"AI自动改终稿没人看"。[src:c84032e9]

### Friction 建议补记（0条，已直接记friction_log）

### Playbook 建议更新（0处，已更新p9_trading.md）

---

### 🤖 本次自动写入摘要（4-5分，已直接写入正式文件）
- 无（本次候选最高3分，全部送审，未自动写正式文件——冷启动保守）

### 🗑️ 本次自动丢弃摘要（1分，未保留）
- 共约2条1分候选(哨兵脚本措辞小瑕疵/dry模式细节)被AI自判低价值丢弃

## [草稿] 2026-06-28 深度审核（session 8a6d016c · BB）

### INSIGHTS 建议写入（2条）
1. **[评分:3]** 哨兵类自动化系统的"闭环"≠"全自动" → 判断这类系统健康看两点:①一圈动作能否首尾相接自己转下去(=闭环成立)②人工推动循环(周检/复盘/补哨兵)是否在转(="越用越好"非"越放越好")。FERC哨兵=机器盯防+人工判断的半自动闭环,人工判断故意不让机器做(是不是真终局/利不利好机器判不了)。本质区分:闭环管"不错过信号",赚不赚钱另算 [src:8a6d016c]
2. **[评分:2]** friction复盘"按去向分4摞"手法 → 读全本后先识别同根因(本次:授权债12条同根因从6/06复发到6/28),再分①同根因待根治②已闭环可归档③需主公拍板独立项④已沉淀成规则可归档;避免把同一个病当N个独立问题逐条处理 [src:8a6d016c]

### Friction 建议补记（1条）
- **[评分:3]** ⚠️ 跨实例git工作区 | 收工步骤3 git status显示E1档案等多个M文件,核查发现E1档案我的改动已被CC实例最近一次收工commit(f63e8a6)连带提交+push,工作区=HEAD无差异 | 现象=三实例共享同一git正本(memory/notes等symlink),一个实例编辑的文件可能被另一实例的收工commit带走 | 处理:收工只add本次确属自己且git diff有差异的文件,提交前用`git diff HEAD <file>`核实真实差异,不凭git status的M盲目add | 状态:本次无害(CC帮提交了),但需观察是否会致提交归属混乱/或两实例同时改同文件冲突 [src:8a6d016c]

---

### 🤖 本次自动写入摘要（4-5 分）
- 无（本次候选均 2-3 分送审，取保守不自动写入）

### 🗑️ 本次自动丢弃摘要（1 分）
- 0 条
